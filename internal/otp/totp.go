// Package otp generates one-time codes and parses otpauth:// URLs.
package otp

import (
	"encoding/base32"
	"errors"
	"fmt"
	"strings"
	"time"

	potp "github.com/pquerna/otp"
	"github.com/pquerna/otp/totp"
)

// Params describes a TOTP account.
type Params struct {
	Secret    string
	Algorithm string // SHA1, SHA256 or SHA512
	Digits    int
	Period    int
	Issuer    string
	Account   string
}

// FromSecret returns the defaults used by most sites:
// SHA1, 6 digits, 30 seconds.
func FromSecret(secret string) Params {
	return Params{Secret: secret, Algorithm: "SHA1", Digits: 6, Period: 30}
}

// Parse accepts either an otpauth://totp/... URL (what QR codes contain)
// or a bare base32 secret, and checks that it can produce codes.
func Parse(s string) (Params, error) {
	s = strings.TrimSpace(s)
	var p Params
	switch {
	case strings.HasPrefix(s, "otpauth-migration://"):
		return p, errors.New("this is a Google Authenticator export QR, which is not supported yet; export accounts one at a time instead")
	case strings.HasPrefix(s, "otpauth://"):
		key, err := potp.NewKeyFromURL(s)
		if err != nil {
			return p, fmt.Errorf("invalid otpauth URL: %w", err)
		}
		if key.Type() != "totp" {
			return p, fmt.Errorf("%s codes are not supported, only totp", key.Type())
		}
		p = Params{
			Secret:    key.Secret(),
			Algorithm: key.Algorithm().String(),
			Digits:    key.Digits().Length(),
			Period:    int(key.Period()),
			Issuer:    key.Issuer(),
			Account:   key.AccountName(),
		}
	default:
		p = FromSecret(s)
	}
	p.Secret = normalise(p.Secret)
	if _, err := base32.StdEncoding.WithPadding(base32.NoPadding).DecodeString(strings.TrimRight(p.Secret, "=")); err != nil || p.Secret == "" {
		return p, errors.New("the secret is not valid base32")
	}
	if _, err := Code(p, time.Now()); err != nil {
		return p, err
	}
	return p, nil
}

// Code returns the TOTP code for p at the given time.
func Code(p Params, now time.Time) (string, error) {
	alg, err := algorithm(p.Algorithm)
	if err != nil {
		return "", err
	}
	digits, period := p.Digits, p.Period
	if digits == 0 {
		digits = 6
	}
	if period == 0 {
		period = 30
	}
	return totp.GenerateCodeCustom(normalise(p.Secret), now, totp.ValidateOpts{
		Period:    uint(period),
		Digits:    potp.Digits(digits),
		Algorithm: alg,
	})
}

func normalise(secret string) string {
	return strings.ToUpper(strings.ReplaceAll(secret, " ", ""))
}

func algorithm(name string) (potp.Algorithm, error) {
	switch strings.ToUpper(name) {
	case "", "SHA1":
		return potp.AlgorithmSHA1, nil
	case "SHA256":
		return potp.AlgorithmSHA256, nil
	case "SHA512":
		return potp.AlgorithmSHA512, nil
	}
	return 0, fmt.Errorf("unsupported hash function %q", name)
}
