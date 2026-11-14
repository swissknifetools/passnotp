// Package capture gets an image from a screen region, the clipboard or a
// file, using whatever tool the platform provides.
package capture

import (
	"bytes"
	"errors"
	"fmt"
	"image"
	_ "image/jpeg"
	_ "image/png"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

var ErrCancelled = errors.New("screenshot cancelled")

// CanSelectRegion reports whether Region is available on this platform.
func CanSelectRegion() bool { return runtime.GOOS != "windows" }

// Region lets the user drag a box on screen and returns that image.
func Region() (image.Image, error) {
	switch runtime.GOOS {
	case "darwin":
		return viaTempFile(func(path string) *exec.Cmd {
			return exec.Command("screencapture", "-i", "-x", path)
		})
	case "windows":
		return nil, errors.New("region capture is not supported on Windows yet: take a screenshot with Win+Shift+S and use --clipboard")
	}

	if os.Getenv("WAYLAND_DISPLAY") != "" && have("grim") && have("slurp") {
		geometry, err := exec.Command("slurp").Output()
		if err != nil {
			return nil, ErrCancelled
		}
		return decode(exec.Command("grim", "-g", strings.TrimSpace(string(geometry)), "-"))
	}
	if have("flameshot") {
		args := []string{"gui", "--raw"}
		// Finish as soon as the mouse is released instead of waiting for
		// Enter, on versions that support it.
		if help, _ := exec.Command("flameshot", "gui", "--help").CombinedOutput(); bytes.Contains(help, []byte("--accept-on-select")) {
			args = append(args, "--accept-on-select")
		}
		return decode(exec.Command("flameshot", args...))
	}
	if have("maim") {
		return decode(exec.Command("maim", "-s"))
	}
	if have("gnome-screenshot") {
		return viaTempFile(func(path string) *exec.Cmd {
			return exec.Command("gnome-screenshot", "-a", "-f", path)
		})
	}
	return nil, errors.New("no screenshot tool found: install flameshot (or grim and slurp on Wayland), or use --clipboard/--image")
}

// Clipboard returns the image currently on the clipboard.
func Clipboard() (image.Image, error) {
	switch runtime.GOOS {
	case "darwin":
		return viaTempFile(func(path string) *exec.Cmd {
			script := fmt.Sprintf(`set f to open for access POSIX file %q with write permission
write (the clipboard as «class PNGf») to f
close access f`, path)
			return exec.Command("osascript", "-e", script)
		})
	case "windows":
		return viaTempFile(func(path string) *exec.Cmd {
			script := fmt.Sprintf(`Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$i = [System.Windows.Forms.Clipboard]::GetImage(); if ($i -eq $null) { exit 1 }
$i.Save('%s', [System.Drawing.Imaging.ImageFormat]::Png)`, strings.ReplaceAll(path, "'", "''"))
			return exec.Command("powershell", "-NoProfile", "-STA", "-Command", script)
		})
	}
	if os.Getenv("WAYLAND_DISPLAY") != "" && have("wl-paste") {
		return decodeClipboard(exec.Command("wl-paste", "--type", "image/png"))
	}
	if have("xclip") {
		return decodeClipboard(exec.Command("xclip", "-selection", "clipboard", "-t", "image/png", "-o"))
	}
	return nil, errors.New("reading images from the clipboard needs xclip (X11) or wl-clipboard (Wayland)")
}

func File(path string) (image.Image, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	img, _, err := image.Decode(f)
	if err != nil {
		return nil, fmt.Errorf("%s: %w", path, err)
	}
	return img, nil
}

func have(tool string) bool {
	_, err := exec.LookPath(tool)
	return err == nil
}

// decode runs a tool that writes an image to stdout.
func decode(cmd *exec.Cmd) (image.Image, error) {
	out, err := cmd.Output()
	if err != nil || len(out) == 0 {
		return nil, ErrCancelled
	}
	img, _, err := image.Decode(bytes.NewReader(out))
	if err != nil {
		return nil, ErrCancelled
	}
	return img, nil
}

func decodeClipboard(cmd *exec.Cmd) (image.Image, error) {
	img, err := decode(cmd)
	if err != nil {
		return nil, errors.New("the clipboard does not contain an image")
	}
	return img, nil
}

// viaTempFile runs a tool that writes an image to the given path.
func viaTempFile(build func(path string) *exec.Cmd) (image.Image, error) {
	dir, err := os.MkdirTemp("", "passnotp-*")
	if err != nil {
		return nil, err
	}
	defer os.RemoveAll(dir)
	path := filepath.Join(dir, "capture.png")
	if err := build(path).Run(); err != nil {
		return nil, ErrCancelled
	}
	if info, err := os.Stat(path); err != nil || info.Size() == 0 {
		return nil, ErrCancelled
	}
	return File(path)
}
