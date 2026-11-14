package qr

import (
	"image"
	"image/color"
	"image/draw"
	"testing"

	"github.com/pquerna/otp/totp"
)

func TestDecodeOTPAuthQR(t *testing.T) {
	key, err := totp.Generate(totp.GenerateOpts{Issuer: "GitHub", AccountName: "alice@example.com"})
	if err != nil {
		t.Fatal(err)
	}
	img, err := key.Image(300, 300)
	if err != nil {
		t.Fatal(err)
	}

	// Simulate a screenshot: the code somewhere on a larger grey page.
	page := image.NewRGBA(image.Rect(0, 0, 800, 600))
	draw.Draw(page, page.Bounds(), &image.Uniform{color.Gray{0xee}}, image.Point{}, draw.Src)
	draw.Draw(page, image.Rect(250, 150, 550, 450), img, image.Point{}, draw.Src)

	for name, in := range map[string]image.Image{"tight crop": img, "screenshot": page} {
		got, err := Decode(in)
		if err != nil {
			t.Fatalf("%s: %v", name, err)
		}
		if got != key.String() {
			t.Errorf("%s: got %q, want %q", name, got, key.String())
		}
	}
}

func TestDecodeNoCode(t *testing.T) {
	blank := image.NewRGBA(image.Rect(0, 0, 200, 200))
	if _, err := Decode(blank); err != ErrNoCode {
		t.Fatalf("err = %v, want ErrNoCode", err)
	}
}
