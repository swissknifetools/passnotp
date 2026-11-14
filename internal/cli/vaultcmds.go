package cli

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"slices"

	"github.com/spf13/cobra"
	"github.com/zalando/go-keyring"

	"github.com/swissknifetools/passnotp/internal/vault"
)

func newInitCmd(a *app) *cobra.Command {
	return &cobra.Command{
		Use:   "init",
		Short: "Create the vault and choose its master password.",
		Args:  cobra.NoArgs,
		RunE: func(cmd *cobra.Command, _ []string) error {
			if vault.Exists(a.paths.Vault) {
				return fmt.Errorf("a vault already exists at %s", a.paths.Vault)
			}
			if _, err := a.createVault(cmd); err != nil {
				return err
			}
			fmt.Fprintf(cmd.ErrOrStderr(), "Created %s\n", a.paths.Vault)
			return nil
		},
	}
}

func newExportCmd(a *app) *cobra.Command {
	return &cobra.Command{
		Use:   "export [file]",
		Short: "Save a copy of the vault, to move it to another computer.",
		Long: `Save a copy of the vault, to move it to another computer.

The copy is encrypted with your master password, like the vault itself. On
the other computer, run ` + "`passnotp import <file>`" + `.`,
		Args: cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			v, err := a.openVault(cmd, true)
			if err != nil {
				return err
			}
			if v == nil {
				return errors.New("there is no vault yet, add entries with `pass add` or `otp add`")
			}
			path, err := a.fileArg(cmd, args, "Export to [passnotp-vault.json]: ", "passnotp-vault.json")
			if err != nil {
				return err
			}
			if sameFile(path, a.paths.Vault) {
				return errors.New("that is the vault itself; choose another file")
			}
			if vault.Exists(path) {
				ok, err := a.prompter(cmd).confirm(fmt.Sprintf("%s already exists. Overwrite it? [y/N] ", path))
				if err != nil {
					return err
				}
				if !ok {
					fmt.Fprintln(cmd.ErrOrStderr(), "Cancelled.")
					return nil
				}
			}
			if err := v.SaveCopy(path); err != nil {
				return err
			}
			w := cmd.ErrOrStderr()
			fmt.Fprintf(w, "Exported %d passwords and %d OTP accounts to %s\n", len(v.Data.Passwords), len(v.Data.OTP), path)
			fmt.Fprintln(w, "It is encrypted with your master password. On the other computer, run: passnotp import <file>")
			return nil
		},
	}
}

func newImportCmd(a *app) *cobra.Command {
	return &cobra.Command{
		Use:   "import [file]",
		Short: "Add the entries of an exported vault to this one.",
		Long: `Add the entries of a file made by ` + "`passnotp export`" + `, asking for its master
password.

If this computer has no vault yet, the file becomes the vault and keeps its
master password. Otherwise its entries are added to the vault; names that
are in both keep this vault's value.`,
		Args: cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			path, err := a.fileArg(cmd, args, "File to import: ", "")
			if err != nil {
				return err
			}
			if sameFile(path, a.paths.Vault) {
				return errors.New("that is the vault itself")
			}
			locked, err := vault.Open(path)
			if err != nil {
				return err
			}
			dst, err := a.openVault(cmd, true)
			if err != nil {
				return err
			}
			src, err := a.unlockOther(cmd, locked, dst, path)
			if err != nil {
				return err
			}
			w := cmd.ErrOrStderr()

			if dst == nil {
				if err := src.SaveCopy(a.paths.Vault); err != nil {
					return err
				}
				fmt.Fprintf(w, "Imported %d passwords and %d OTP accounts into %s\n", len(src.Data.Passwords), len(src.Data.OTP), a.paths.Vault)
				fmt.Fprintln(w, "The master password is the one of the imported file.")
				a.cacheKey(cmd, src)
				return nil
			}

			var addedPass, addedOTP, same int
			var kept []string
			for name, p := range src.Data.Passwords {
				switch e, ok := dst.Data.Passwords[name]; {
				case !ok:
					dst.Data.Passwords[name] = p
					addedPass++
				case e.Value == p.Value:
					same++
				default:
					kept = append(kept, "pass "+name)
				}
			}
			for name, o := range src.Data.OTP {
				switch e, ok := dst.Data.OTP[name]; {
				case !ok:
					dst.Data.OTP[name] = o
					addedOTP++
				case e.Secret == o.Secret:
					same++
				default:
					kept = append(kept, "otp "+name)
				}
			}
			if err := dst.Save(); err != nil {
				return err
			}
			fmt.Fprintf(w, "Imported %d passwords and %d OTP accounts (%d already in the vault).\n", addedPass, addedOTP, same)
			slices.Sort(kept)
			for _, k := range kept {
				fmt.Fprintf(w, "Different in both, kept this vault's value: %s\n", k)
			}
			return nil
		},
	}
}

// unlockOther unlocks an exported vault. A copy of this computer's vault
// opens with its key; anything else needs that file's master password.
func (a *app) unlockOther(cmd *cobra.Command, l *vault.Locked, current *vault.Vault, path string) (*vault.Vault, error) {
	if current != nil {
		if v, err := l.UnlockWithKey(current.Key()); err == nil {
			return v, nil
		}
	}
	pw, err := a.prompter(cmd).secret(fmt.Sprintf("Master password of %s: ", filepath.Base(path)))
	if err != nil {
		return nil, err
	}
	return l.UnlockWithPassword(pw)
}

// fileArg returns the file named on the command line, or asks for it.
func (a *app) fileArg(cmd *cobra.Command, args []string, label, def string) (string, error) {
	if len(args) > 0 {
		return cleanPath(args[0]), nil
	}
	path, err := a.prompter(cmd).line(label)
	if err != nil {
		return "", err
	}
	if path = cleanPath(path); path == "" {
		path = def
	}
	if path == "" {
		return "", errors.New("a file is required")
	}
	return path, nil
}

func sameFile(a, b string) bool {
	fa, err := os.Stat(a)
	if err != nil {
		return false
	}
	fb, err := os.Stat(b)
	return err == nil && os.SameFile(fa, fb)
}

func newPasswdCmd(a *app) *cobra.Command {
	return &cobra.Command{
		Use:   "passwd",
		Short: "Change the vault's master password.",
		Args:  cobra.NoArgs,
		RunE: func(cmd *cobra.Command, _ []string) error {
			v, err := a.openVault(cmd, true)
			if err != nil {
				return err
			}
			if v == nil {
				return errors.New("there is no vault yet; run `passnotp init`")
			}
			pw, err := a.prompter(cmd).newSecret("new master password")
			if err != nil {
				return err
			}
			if err := v.ChangePassword(pw); err != nil {
				return err
			}
			fmt.Fprintln(cmd.ErrOrStderr(), "Master password changed.")
			return nil
		},
	}
}

func newLockCmd(a *app) *cobra.Command {
	return &cobra.Command{
		Use:   "lock",
		Short: "Forget the vault key on this machine; the master password is asked next time.",
		Args:  cobra.NoArgs,
		RunE: func(cmd *cobra.Command, _ []string) error {
			err := keyStore.Delete(a.vaultID())
			if errors.Is(err, keyring.ErrNotFound) {
				fmt.Fprintln(cmd.ErrOrStderr(), "The vault key was not saved in the OS keyring.")
				return nil
			}
			if err != nil {
				return err
			}
			fmt.Fprintln(cmd.ErrOrStderr(), "Removed the vault key from the OS keyring.")
			return nil
		},
	}
}
