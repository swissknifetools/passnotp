// Package cli wires up the passnotp command tree.
package cli

import (
	"fmt"
	"os"
	"path/filepath"
	"slices"
	"time"

	"github.com/atotto/clipboard"
	"github.com/spf13/cobra"

	"github.com/swissknifetools/passnotp/internal/vault"
)

// Paths of the files passnotp uses.
type Paths struct {
	Vault string
}

func DefaultPaths() Paths {
	config, err := os.UserConfigDir()
	if err != nil {
		home, _ := os.UserHomeDir()
		config = filepath.Join(home, ".config")
	}
	return Paths{
		Vault: envOr("PASSNOTP_VAULT", filepath.Join(config, "passnotp", "vault.json")),
	}
}

func envOr(name, def string) string {
	if v := os.Getenv(name); v != "" {
		return v
	}
	return def
}

// Package-level hooks so tests can capture the clipboard, swap the keyring
// and pin the clock.
var (
	copyToClipboard = clipboard.WriteAll
	keyStore        = defaultKeyStore()
	now             = time.Now
)

func defaultKeyStore() vault.KeyStore {
	if os.Getenv("PASSNOTP_NO_KEYRING") != "" {
		return vault.NoKeyring{}
	}
	return vault.OSKeyring{}
}

// Version is set at build time for releases.
var Version = "dev"

func NewRoot(paths Paths) *cobra.Command {
	a := &app{paths: paths}
	root := &cobra.Command{
		Use:           "passnotp",
		Short:         "Copy passwords and one-time codes to the clipboard.",
		Version:       Version,
		SilenceUsage:  true,
		SilenceErrors: true,
	}
	root.CompletionOptions.DisableDefaultCmd = true
	passCmd, otpCmd := newPassCmd(a), newOTPCmd(a)
	// Tab after `pass` or `otp` offers entry names only, not subcommands
	// like add or ls; they still show in --help and run as usual.
	root.PersistentPreRun = func(cmd *cobra.Command, _ []string) {
		if cmd.Name() != cobra.ShellCompRequestCmd && cmd.Name() != cobra.ShellCompNoDescRequestCmd {
			return
		}
		for _, sub := range append(passCmd.Commands(), otpCmd.Commands()...) {
			sub.Hidden = true
		}
	}
	root.AddCommand(
		passCmd,
		otpCmd,
		newInitCmd(a),
		newExportCmd(a),
		newImportCmd(a),
		newPasswdCmd(a),
		newLockCmd(a),
		newCompletionCmd(),
		newClearCmd(),
	)
	return root
}

// AliasArgs turns the arguments of a `pass`/`otp` symlink invocation into
// the equivalent `passnotp pass|otp ...` arguments.
func AliasArgs(alias string, args []string) []string {
	if len(args) > 0 && args[0] == clearCmdName {
		return args // pass.exe and otp.exe are copies on Windows
	}
	if len(args) > 0 && (args[0] == cobra.ShellCompRequestCmd || args[0] == cobra.ShellCompNoDescRequestCmd) {
		return append([]string{args[0], alias}, args[1:]...)
	}
	return append([]string{alias}, args...)
}

// emit either prints the secret or copies it, then says what happened.
func emit(cmd *cobra.Command, name, value string, print bool) error {
	if print {
		fmt.Fprintln(cmd.OutOrStdout(), value)
		return nil
	}
	if err := copyToClipboard(value); err != nil {
		return fmt.Errorf("copy to clipboard: %w", err)
	}
	d := clearAfter()
	if d == 0 {
		fmt.Fprintf(cmd.ErrOrStderr(), "Copied '%s' to clipboard.\n", name)
		return nil
	}
	if err := scheduleClear(value, d); err != nil {
		fmt.Fprintf(cmd.ErrOrStderr(), "Copied '%s' to clipboard (could not schedule clearing it: %v).\n", name, err)
		return nil
	}
	fmt.Fprintf(cmd.ErrOrStderr(), "Copied '%s' to clipboard, clearing it in %ds.\n", name, int(d.Seconds()))
	return nil
}

func listCmd(short string, names func(*cobra.Command, bool) ([]string, error)) *cobra.Command {
	return &cobra.Command{
		Use:     "ls",
		Aliases: []string{"list"},
		Short:   short,
		Args:    cobra.NoArgs,
		RunE: func(cmd *cobra.Command, _ []string) error {
			n, err := names(cmd, true)
			if err != nil {
				return err
			}
			for _, name := range n {
				fmt.Fprintln(cmd.OutOrStdout(), name)
			}
			return nil
		},
	}
}

// deleteCmd removes an entry from the vault.
func deleteCmd(a *app, noun string, names func(*cobra.Command, bool) ([]string, error), remove func(*vault.Vault, string)) *cobra.Command {
	var yes bool
	cmd := &cobra.Command{
		Use:               "delete [name]",
		Short:             "Delete a " + noun + ".",
		Args:              cobra.MaximumNArgs(1),
		ValidArgsFunction: completeWith(names),
		RunE: func(cmd *cobra.Command, args []string) error {
			name, err := a.pickName(cmd, args, names)
			if err != nil {
				return err
			}
			all, err := names(cmd, true)
			if err != nil {
				return err
			}
			if !slices.Contains(all, name) {
				return a.notFound(name)
			}
			v, err := a.openVault(cmd, true)
			if err != nil {
				return err
			}
			if !yes {
				ok, err := a.prompter(cmd).confirm(fmt.Sprintf("Delete '%s'? [y/N] ", name))
				if err != nil {
					return err
				}
				if !ok {
					fmt.Fprintln(cmd.ErrOrStderr(), "Cancelled.")
					return nil
				}
			}
			remove(v, name)
			if err := v.Save(); err != nil {
				return err
			}
			fmt.Fprintf(cmd.ErrOrStderr(), "Deleted '%s'.\n", name)
			return nil
		},
	}
	cmd.Flags().BoolVarP(&yes, "yes", "y", false, "do not ask for confirmation")
	return cmd
}
