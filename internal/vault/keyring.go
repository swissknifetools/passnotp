package vault

import (
	"encoding/base64"

	"github.com/zalando/go-keyring"
)

// KeyStore caches vault keys so the master password is not needed on every
// run. id identifies the vault (its absolute path).
type KeyStore interface {
	Get(id string) ([]byte, error)
	Set(id string, key []byte) error
	Delete(id string) error
}

const keyringService = "passnotp"

// OSKeyring stores vault keys in GNOME Keyring/KWallet (Secret Service),
// the macOS Keychain or the Windows Credential Manager.
type OSKeyring struct{}

func (OSKeyring) Get(id string) ([]byte, error) {
	s, err := keyring.Get(keyringService, id)
	if err != nil {
		return nil, err
	}
	return base64.StdEncoding.DecodeString(s)
}

func (OSKeyring) Set(id string, key []byte) error {
	return keyring.Set(keyringService, id, base64.StdEncoding.EncodeToString(key))
}

func (OSKeyring) Delete(id string) error {
	return keyring.Delete(keyringService, id)
}

// NoKeyring never caches anything, so every run asks for the master password.
type NoKeyring struct{}

func (NoKeyring) Get(string) ([]byte, error) { return nil, keyring.ErrNotFound }
func (NoKeyring) Set(string, []byte) error   { return keyring.ErrUnsupportedPlatform }
func (NoKeyring) Delete(string) error        { return keyring.ErrNotFound }
