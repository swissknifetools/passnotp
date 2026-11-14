package cli

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/swissknifetools/passnotp/internal/vault"
)

func newPassCmd(a *app) *cobra.Command {
	var print bool
	cmd := &cobra.Command{
		Use:               "pass <name>",
		Aliases:           []string{"p"},
		Short:             "Copy a password to the clipboard.",
		Args:              cobra.MaximumNArgs(1),
		ValidArgsFunction: completeWith(a.passwordNames),
		RunE: func(cmd *cobra.Command, args []string) error {
			if len(args) == 0 {
				return cmd.Help()
			}
			value, found, err := a.findPassword(cmd, args[0])
			if err != nil {
				return err
			}
			if !found {
				return a.notFound(args[0])
			}
			return emit(cmd, args[0], value, print)
		},
	}
	cmd.Flags().BoolVar(&print, "print", false, "print to stdout instead of copying")

	cmd.AddCommand(
		listCmd("List password names.", a.passwordNames),
		newPassSetCmd(a, false),
		newPassSetCmd(a, true),
		deleteCmd(a, "password", a.passwordNames,
			func(v *vault.Vault, name string) { delete(v.Data.Passwords, name) }),
	)
	return cmd
}

// newPassSetCmd builds `pass add` or, with update, `pass update`.
func newPassSetCmd(a *app, update bool) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "add [name]",
		Short: "Add a password (asks for anything not given).",
		Args:  cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			pick := a.nameArg
			if update {
				pick = func(cmd *cobra.Command, args []string) (string, error) {
					return a.pickName(cmd, args, a.passwordNames)
				}
			}
			name, err := pick(cmd, args)
			if err != nil {
				return err
			}
			if err := checkName(name); err != nil {
				return err
			}
			_, exists, err := a.findPassword(cmd, name)
			if err != nil {
				return err
			}
			if update && !exists {
				return fmt.Errorf("'%s' does not exist; use `pass add %s` to create it", name, name)
			}
			if !update && exists {
				return fmt.Errorf("'%s' already exists; use `pass update %s` to change it", name, name)
			}
			v, err := a.vaultForWrite(cmd)
			if err != nil {
				return err
			}
			pw, err := a.prompter(cmd).newSecret("password")
			if err != nil {
				return err
			}
			v.Data.Passwords[name] = vault.Password{Value: pw, Updated: now()}
			if err := v.Save(); err != nil {
				return err
			}
			fmt.Fprintf(cmd.ErrOrStderr(), "Saved '%s'.\n", name)
			return nil
		},
	}
	if update {
		cmd.Use, cmd.Short = "update [name]", "Change a password."
		cmd.ValidArgsFunction = completeWith(a.passwordNames)
	}
	return cmd
}
