package vault

import (
	"bytes"
	"errors"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func TestCreateUnlockRoundTrip(t *testing.T) {
	path := filepath.Join(t.TempDir(), "sub", "vault.json")
	v, err := Create(path, "correct horse")
	if err != nil {
		t.Fatal(err)
	}
	v.Data.Passwords["github"] = Password{Value: "hunter2"}
	v.Data.OTP["aws"] = OTP{Secret: "JBSWY3DPEHPK3PXP", Algorithm: "SHA1", Digits: 6, Period: 30}
	if err := v.Save(); err != nil {
		t.Fatal(err)
	}

	info, err := os.Stat(path)
	if err != nil {
		t.Fatal(err)
	}
	if runtime.GOOS != "windows" && info.Mode().Perm() != 0o600 {
		t.Errorf("vault mode = %v, want 0600", info.Mode().Perm())
	}
	raw, _ := os.ReadFile(path)
	if bytes.Contains(raw, []byte("hunter2")) || bytes.Contains(raw, []byte("github")) {
		t.Fatal("vault file contains plaintext")
	}

	l, err := Open(path)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := l.UnlockWithPassword("wrong password"); !errors.Is(err, ErrWrongPassword) {
		t.Fatalf("wrong password err = %v", err)
	}
	byPw, err := l.UnlockWithPassword("correct horse")
	if err != nil {
		t.Fatal(err)
	}
	byKey, err := l.UnlockWithKey(v.Key())
	if err != nil {
		t.Fatal(err)
	}
	for _, u := range []*Vault{byPw, byKey} {
		if u.Data.Passwords["github"].Value != "hunter2" || u.Data.OTP["aws"].Secret != "JBSWY3DPEHPK3PXP" {
			t.Errorf("unexpected data %+v", u.Data)
		}
	}
	if _, err := l.UnlockWithKey(make([]byte, keySize)); err == nil {
		t.Error("unlocked with a wrong key")
	}
}

func TestChangePasswordKeepsKey(t *testing.T) {
	path := filepath.Join(t.TempDir(), "vault.json")
	v, err := Create(path, "first password")
	if err != nil {
		t.Fatal(err)
	}
	if err := v.ChangePassword("second password"); err != nil {
		t.Fatal(err)
	}
	l, _ := Open(path)
	if _, err := l.UnlockWithPassword("first password"); err == nil {
		t.Error("old password still works")
	}
	u, err := l.UnlockWithPassword("second password")
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(u.Key(), v.Key()) {
		t.Error("vault key changed, cached keys would break")
	}
}

func TestTamperingDetected(t *testing.T) {
	path := filepath.Join(t.TempDir(), "vault.json")
	v, _ := Create(path, "correct horse")
	raw, _ := os.ReadFile(path)
	// Flip one character of the encrypted data.
	i := strings.Index(string(raw), `"data": "`) + len(`"data": "`) + 20
	raw[i] ^= 1
	os.WriteFile(path, raw, 0o600)
	l, err := Open(path)
	if err != nil {
		return // corrupt base64 is also a detection
	}
	if _, err := l.UnlockWithKey(v.Key()); err == nil {
		t.Fatal("tampered vault unlocked")
	}
}

func TestShortPasswordRejected(t *testing.T) {
	for _, pw := range []string{"short", "elevenchars", "ééééééééééé"} {
		if _, err := Create(filepath.Join(t.TempDir(), "v"), pw); err == nil {
			t.Errorf("%q accepted", pw)
		}
	}
	if _, err := Create(filepath.Join(t.TempDir(), "v"), "twelve chars"); err != nil {
		t.Errorf("12 characters rejected: %v", err)
	}
}

func TestHostileKDFSettingsRejected(t *testing.T) {
	path := filepath.Join(t.TempDir(), "vault.json")
	Create(path, "correct horse")
	raw, _ := os.ReadFile(path)
	huge := strings.Replace(string(raw), `"memory_kib": 65536`, `"memory_kib": 4294967295`, 1)
	if huge == string(raw) {
		t.Fatal("fixture did not change")
	}
	os.WriteFile(path, []byte(huge), 0o600)
	if _, err := Open(path); err == nil || !strings.Contains(err.Error(), "key derivation") {
		t.Fatalf("huge memory accepted: %v", err)
	}
}
