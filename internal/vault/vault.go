// Package vault is passnotp's own encrypted store for passwords and OTP
// secrets.
//
// The data is encrypted with a random 256-bit vault key (AES-256-GCM). The
// vault key itself is stored inside the file wrapped by a key derived from
// the master password (argon2id), so the file alone is enough to move the
// vault to another machine. Callers may also cache the vault key elsewhere
// (the OS keyring) and unlock with it directly.
package vault

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"time"
	"unicode/utf8"

	"golang.org/x/crypto/argon2"
)

const (
	formatVersion = 1
	keySize       = 32
	aadKey        = "passnotp-vault-v1:key"
	aadData       = "passnotp-vault-v1:data"
	MinPassword   = 12
)

var ErrWrongPassword = errors.New("wrong master password")

type Password struct {
	Value   string    `json:"value"`
	Updated time.Time `json:"updated"`
}

type OTP struct {
	Secret    string    `json:"secret"`
	Algorithm string    `json:"algorithm"`
	Digits    int       `json:"digits"`
	Period    int       `json:"period"`
	Issuer    string    `json:"issuer,omitempty"`
	Account   string    `json:"account,omitempty"`
	Updated   time.Time `json:"updated"`
}

// Data is the decrypted content of the vault.
type Data struct {
	Passwords map[string]Password `json:"passwords"`
	OTP       map[string]OTP      `json:"otp"`
}

type kdfParams struct {
	Name    string `json:"name"`
	Salt    []byte `json:"salt"`
	Time    uint32 `json:"time"`
	Memory  uint32 `json:"memory_kib"`
	Threads uint8  `json:"threads"`
}

// fileFormat is what is written to disk. []byte fields are base64 in JSON.
type fileFormat struct {
	Version    int       `json:"version"`
	KDF        kdfParams `json:"kdf"`
	WrappedKey []byte    `json:"wrapped_key"`
	Data       []byte    `json:"data"`
}

// Locked is a vault file that has been read but not decrypted yet.
type Locked struct {
	path string
	file fileFormat
}

type Vault struct {
	path string
	file fileFormat
	key  []byte
	Data Data
}

func Exists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

// Create writes a new, empty vault protected by password.
func Create(path string, password string) (*Vault, error) {
	if Exists(path) {
		return nil, fmt.Errorf("%s already exists", path)
	}
	key := make([]byte, keySize)
	if _, err := rand.Read(key); err != nil {
		return nil, err
	}
	v := &Vault{
		path: path,
		file: fileFormat{Version: formatVersion},
		key:  key,
		Data: Data{Passwords: map[string]Password{}, OTP: map[string]OTP{}},
	}
	if err := v.wrapKey(password); err != nil {
		return nil, err
	}
	return v, v.Save()
}

func Open(path string) (*Locked, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var f fileFormat
	if err := json.Unmarshal(raw, &f); err != nil {
		return nil, fmt.Errorf("parse %s: %w", path, err)
	}
	if f.Version != formatVersion {
		return nil, fmt.Errorf("%s: unsupported vault version %d", path, f.Version)
	}
	// The KDF settings come from the file, which may be an import from
	// elsewhere: bound them so a crafted file cannot exhaust memory or CPU.
	if k := f.KDF; k.Name != "argon2id" || len(k.Salt) < 16 || k.Time < 1 || k.Time > 10 ||
		k.Memory < 8*1024 || k.Memory > 1024*1024 || k.Threads < 1 || k.Threads > 16 {
		return nil, fmt.Errorf("%s: invalid key derivation settings", path)
	}
	return &Locked{path: path, file: f}, nil
}

// UnlockWithKey decrypts the vault with a cached vault key.
func (l *Locked) UnlockWithKey(key []byte) (*Vault, error) {
	plain, err := open(key, l.file.Data, aadData)
	if err != nil {
		return nil, errors.New("the cached vault key does not open this vault")
	}
	v := &Vault{path: l.path, file: l.file, key: key}
	if err := json.Unmarshal(plain, &v.Data); err != nil {
		return nil, fmt.Errorf("parse vault data: %w", err)
	}
	if v.Data.Passwords == nil {
		v.Data.Passwords = map[string]Password{}
	}
	if v.Data.OTP == nil {
		v.Data.OTP = map[string]OTP{}
	}
	return v, nil
}

func (l *Locked) UnlockWithPassword(password string) (*Vault, error) {
	key, err := open(l.file.KDF.derive(password), l.file.WrappedKey, aadKey)
	if err != nil {
		return nil, ErrWrongPassword
	}
	return l.UnlockWithKey(key)
}

func (v *Vault) Path() string { return v.path }

// Key is the vault key, for caching in the OS keyring.
func (v *Vault) Key() []byte { return v.key }

// ChangePassword re-wraps the vault key; the data stays encrypted as is.
func (v *Vault) ChangePassword(password string) error {
	if err := v.wrapKey(password); err != nil {
		return err
	}
	return v.Save()
}

// SaveCopy writes the vault to another file, locked with the same master
// password.
func (v *Vault) SaveCopy(path string) error {
	c := *v
	c.path = path
	return c.Save()
}

// Save encrypts the data and atomically replaces the vault file.
func (v *Vault) Save() error {
	plain, err := json.Marshal(v.Data)
	if err != nil {
		return err
	}
	if v.file.Data, err = seal(v.key, plain, aadData); err != nil {
		return err
	}
	out, err := json.MarshalIndent(v.file, "", "  ")
	if err != nil {
		return err
	}
	return writeAtomic(v.path, out)
}

func (v *Vault) wrapKey(password string) error {
	if utf8.RuneCountInString(password) < MinPassword {
		return fmt.Errorf("the master password must be at least %d characters", MinPassword)
	}
	kdf := kdfParams{Name: "argon2id", Salt: make([]byte, 16), Time: 3, Memory: 64 * 1024, Threads: 4}
	if _, err := rand.Read(kdf.Salt); err != nil {
		return err
	}
	wrapped, err := seal(kdf.derive(password), v.key, aadKey)
	if err != nil {
		return err
	}
	v.file.KDF, v.file.WrappedKey = kdf, wrapped
	return nil
}

func (k kdfParams) derive(password string) []byte {
	return argon2.IDKey([]byte(password), k.Salt, k.Time, k.Memory, k.Threads, keySize)
}

// seal returns nonce || AES-256-GCM ciphertext.
func seal(key, plain []byte, aad string) ([]byte, error) {
	gcm, err := newGCM(key)
	if err != nil {
		return nil, err
	}
	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return nil, err
	}
	return gcm.Seal(nonce, nonce, plain, []byte(aad)), nil
}

func open(key, sealed []byte, aad string) ([]byte, error) {
	gcm, err := newGCM(key)
	if err != nil {
		return nil, err
	}
	if len(sealed) < gcm.NonceSize() {
		return nil, errors.New("ciphertext too short")
	}
	n := gcm.NonceSize()
	return gcm.Open(nil, sealed[:n], sealed[n:], []byte(aad))
}

func newGCM(key []byte) (cipher.AEAD, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	return cipher.NewGCM(block)
}

func writeAtomic(path string, data []byte) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o700); err != nil {
		return err
	}
	tmp, err := os.CreateTemp(dir, ".vault-*")
	if err != nil {
		return err
	}
	defer os.Remove(tmp.Name()) // no-op once renamed
	if err := tmp.Chmod(0o600); err != nil {
		tmp.Close()
		return err
	}
	if _, err := tmp.Write(data); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Sync(); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	return os.Rename(tmp.Name(), path)
}
