package cli

import (
	"errors"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"

	"github.com/swissknifetools/passnotp/internal/capture"
	"github.com/swissknifetools/passnotp/internal/otp"
	"github.com/swissknifetools/passnotp/internal/qr"
	"github.com/swissknifetools/passnotp/internal/vault"
)

// Image sources, swappable in tests.
var (
	captureRegion    = capture.Region
	captureClipboard = capture.Clipboard
	captureFile      = capture.File
	canSelectRegion  = capture.CanSelectRegion
)

func newOTPCmd(a *app) *cobra.Command {
	var print bool
	cmd := &cobra.Command{
		Use:               "otp <name>",
		Aliases:           []string{"o"},
		Short:             "Copy the current one-time code to the clipboard.",
		Args:              cobra.MaximumNArgs(1),
		ValidArgsFunction: completeWith(a.otpNames),
		RunE: func(cmd *cobra.Command, args []string) error {
			if len(args) == 0 {
				return cmd.Help()
			}
			p, found, err := a.findOTP(cmd, args[0])
			if err != nil {
				return err
			}
			if !found {
				return a.notFound(args[0])
			}
			code, err := otp.Code(p, now())
			if err != nil {
				return fmt.Errorf("'%s': %w", args[0], err)
			}
			return emit(cmd, args[0], code, print)
		},
	}
	cmd.Flags().BoolVar(&print, "print", false, "print to stdout instead of copying")

	cmd.AddCommand(
		listCmd("List OTP account names.", a.otpNames),
		newOTPAddCmd(a),
		newOTPScanCmd(),
		deleteCmd(a, "OTP account", a.otpNames,
			func(v *vault.Vault, name string) { delete(v.Data.OTP, name) }),
	)
	return cmd
}

// imageFlags are the ways to provide a QR code image.
type imageFlags struct {
	scan      bool
	clipboard bool
	image     string
}

func (f *imageFlags) register(cmd *cobra.Command, withScan bool) {
	if withScan {
		cmd.Flags().BoolVarP(&f.scan, "scan", "s", false, "select the QR code on screen")
	}
	cmd.Flags().BoolVarP(&f.clipboard, "clipboard", "c", false, "read the QR code from an image on the clipboard")
	cmd.Flags().StringVarP(&f.image, "image", "i", "", "read the QR code from an image file")
	if withScan {
		cmd.MarkFlagsMutuallyExclusive("scan", "clipboard", "image")
	} else {
		cmd.MarkFlagsMutuallyExclusive("clipboard", "image")
	}
}

func (f *imageFlags) chosen() bool { return f.scan || f.clipboard || f.image != "" }

// choose asks how to provide the account when no flag was given. Typing
// the secret is choice 4, which leaves every source unset.
func (f *imageFlags) choose(p *prompter) error {
	// Where the screen cannot be selected (Windows), default to the
	// clipboard: take the screenshot with Win+Shift+S first.
	def, first := "1", "Select the QR code on screen"
	if !canSelectRegion() {
		def, first = "2", "Select the QR code on screen (not available here)"
	}
	fmt.Fprintf(p.w, `How do you want to add it?
  1) %s
  2) QR code image on the clipboard
  3) QR code image file
  4) Type the secret or otpauth:// URL
`, first)
	choice, err := p.line("Choice [" + def + "]: ")
	if err != nil {
		return err
	}
	if choice = strings.TrimSpace(choice); choice == "" {
		choice = def
	}
	switch choice {
	case "1":
		f.scan = true
	case "2":
		f.clipboard = true
	case "3":
		path, err := p.line("Image path: ")
		if err != nil {
			return err
		}
		f.image = cleanPath(path)
		if f.image == "" {
			return errors.New("an image path is required")
		}
	case "4":
	default:
		return fmt.Errorf("invalid choice %q", choice)
	}
	return nil
}

// cleanPath tidies a typed or pasted path: surrounding spaces and quotes
// (as when dragging a file into the terminal) and a leading ~/.
func cleanPath(path string) string {
	return expandHome(strings.Trim(strings.TrimSpace(path), `'"`))
}

// expandHome resolves a leading ~/ the way the shell would have.
func expandHome(path string) string {
	if rest, ok := strings.CutPrefix(path, "~/"); ok {
		if home, err := os.UserHomeDir(); err == nil {
			return filepath.Join(home, rest)
		}
	}
	return path
}

// readQR gets an image from the chosen source and returns the QR text.
// ok is false when no image source was chosen.
func (f *imageFlags) readQR(cmd *cobra.Command) (text string, ok bool, err error) {
	var img image.Image
	switch {
	case f.image != "":
		img, err = captureFile(f.image)
	case f.clipboard:
		img, err = captureClipboard()
	case f.scan:
		fmt.Fprintln(cmd.ErrOrStderr(), "Drag a box around the QR code (press Enter if it does not finish on its own, Esc to cancel)...")
		img, err = captureRegion()
	default:
		return "", false, nil
	}
	if err != nil {
		return "", true, err
	}
	text, err = qr.Decode(img)
	if err != nil {
		return "", true, err
	}
	if !strings.HasPrefix(text, "otpauth") {
		return "", true, errors.New("the QR code does not contain an OTP setup link (otpauth://)")
	}
	return text, true, nil
}

func describe(p otp.Params) string {
	switch {
	case p.Issuer != "" && p.Account != "":
		return fmt.Sprintf("%s (%s)", p.Issuer, p.Account)
	case p.Issuer != "":
		return p.Issuer
	}
	return p.Account
}

func newOTPAddCmd(a *app) *cobra.Command {
	var src imageFlags
	var print bool
	cmd := &cobra.Command{
		Use:   "add [name]",
		Short: "Add an OTP account to the vault and copy its current code.",
		Long: `Add an OTP account to the vault and copy its current code.

Just run "otp add": it asks for the name and how to read the account
(QR code on screen, on the clipboard, in a file, or typing the secret).
The flags skip those questions.`,
		Example: "  otp add\n  otp add github --scan\n  otp add github --clipboard\n  otp add github --image qr.png",
		Args:    cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name, err := a.nameArg(cmd, args)
			if err != nil {
				return err
			}
			if err := checkName(name); err != nil {
				return err
			}
			if _, exists, err := a.findOTP(cmd, name); err != nil {
				return err
			} else if exists {
				return fmt.Errorf("'%s' already exists; delete it first to replace it", name)
			}

			if !src.chosen() {
				if err := src.choose(a.prompter(cmd)); err != nil {
					return err
				}
			}
			text, fromImage, err := src.readQR(cmd)
			if err != nil {
				return err
			}
			if !fromImage {
				if text, err = a.prompter(cmd).secret("Secret or otpauth:// URL: "); err != nil {
					return err
				}
			}
			p, err := otp.Parse(text)
			if err != nil {
				return err
			}
			if d := describe(p); d != "" {
				fmt.Fprintf(cmd.ErrOrStderr(), "Found: %s\n", d)
			}

			v, err := a.vaultForWrite(cmd)
			if err != nil {
				return err
			}
			v.Data.OTP[name] = fromParams(p)
			if err := v.Save(); err != nil {
				return err
			}
			fmt.Fprintf(cmd.ErrOrStderr(), "Saved '%s'.\n", name)

			code, err := otp.Code(p, now())
			if err != nil {
				return err
			}
			return emit(cmd, name, code, print)
		},
	}
	src.register(cmd, true)
	cmd.Flags().BoolVar(&print, "print", false, "print the code to stdout instead of copying")
	return cmd
}

func newOTPScanCmd() *cobra.Command {
	src := imageFlags{scan: true}
	var print bool
	cmd := &cobra.Command{
		Use:   "scan",
		Short: "Copy the code from a QR code on screen, without saving it.",
		Args:  cobra.NoArgs,
		RunE: func(cmd *cobra.Command, _ []string) error {
			text, _, err := src.readQR(cmd)
			if err != nil {
				return err
			}
			p, err := otp.Parse(text)
			if err != nil {
				return err
			}
			code, err := otp.Code(p, now())
			if err != nil {
				return err
			}
			name := describe(p)
			if name == "" {
				name = "code"
			}
			return emit(cmd, name, code, print)
		},
	}
	src.register(cmd, false)
	cmd.Flags().BoolVar(&print, "print", false, "print the code to stdout instead of copying")
	return cmd
}
