package otp

import (
	"testing"
	"time"
)

const rfcSecret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ" // "12345678901234567890"

// RFC 6238 appendix B vectors (SHA1).
func TestCodeRFC6238(t *testing.T) {
	for unix, want := range map[int64]string{
		59:         "287082",
		1111111109: "081804",
		1234567890: "005924",
		2000000000: "279037",
	} {
		got, err := Code(FromSecret(rfcSecret), time.Unix(unix, 0))
		if err != nil {
			t.Fatal(err)
		}
		if got != want {
			t.Errorf("Code at %d = %s, want %s", unix, got, want)
		}
	}
	p := FromSecret(rfcSecret)
	p.Digits = 8
	if got, _ := Code(p, time.Unix(59, 0)); got != "94287082" {
		t.Errorf("8-digit code = %s, want 94287082", got)
	}
}

func TestCodeNormalisesSecret(t *testing.T) {
	a, _ := Code(FromSecret("jbsw y3dp ehpk 3pxp"), time.Unix(59, 0))
	b, _ := Code(FromSecret("JBSWY3DPEHPK3PXP"), time.Unix(59, 0))
	if a != b {
		t.Errorf("lowercase/spaced secret gave %s, want %s", a, b)
	}
}

func TestParse(t *testing.T) {
	p, err := Parse("otpauth://totp/GitHub:alice@example.com?secret=JBSWY3DPEHPK3PXP&issuer=GitHub&digits=8&period=60&algorithm=SHA256")
	if err != nil {
		t.Fatal(err)
	}
	want := Params{Secret: "JBSWY3DPEHPK3PXP", Algorithm: "SHA256", Digits: 8, Period: 60, Issuer: "GitHub", Account: "alice@example.com"}
	if p != want {
		t.Errorf("Parse = %+v, want %+v", p, want)
	}

	p, err = Parse("  jbsw y3dp ehpk 3pxp ")
	if err != nil || p != FromSecret("JBSWY3DPEHPK3PXP") {
		t.Errorf("bare secret: %+v, %v", p, err)
	}

	for _, bad := range []string{
		"",
		"not base32!",
		"otpauth://hotp/x?secret=JBSWY3DPEHPK3PXP&counter=1",
		"otpauth-migration://offline?data=abc",
		"otpauth://totp/x?secret=JBSWY3DPEHPK3PXP&algorithm=MD5",
	} {
		if _, err := Parse(bad); err == nil {
			t.Errorf("Parse(%q) succeeded", bad)
		}
	}
}
