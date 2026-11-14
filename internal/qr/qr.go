// Package qr reads the text out of a QR code in an image.
package qr

import (
	"errors"
	"image"
	"image/color"
	"image/draw"

	"github.com/makiuchi-d/gozxing"
	"github.com/makiuchi-d/gozxing/qrcode"
)

var ErrNoCode = errors.New("no QR code found in the image; try selecting the code with a little margin around it")

// Decode returns the text of the QR code in img.
func Decode(img image.Image) (string, error) {
	hints := map[gozxing.DecodeHintType]any{gozxing.DecodeHintType_TRY_HARDER: true}
	// A tight selection can cut off the quiet zone the decoder needs, so
	// retry with a white border added.
	for _, candidate := range []image.Image{img, withBorder(img, 32)} {
		bmp, err := gozxing.NewBinaryBitmapFromImage(candidate)
		if err != nil {
			continue
		}
		res, err := qrcode.NewQRCodeReader().Decode(bmp, hints)
		if err == nil {
			return res.GetText(), nil
		}
	}
	return "", ErrNoCode
}

func withBorder(img image.Image, px int) image.Image {
	b := img.Bounds()
	out := image.NewRGBA(image.Rect(0, 0, b.Dx()+2*px, b.Dy()+2*px))
	draw.Draw(out, out.Bounds(), &image.Uniform{color.White}, image.Point{}, draw.Src)
	draw.Draw(out, image.Rect(px, px, px+b.Dx(), px+b.Dy()), img, b.Min, draw.Src)
	return out
}
