package cli

import (
	"errors"
	"fmt"
	"maps"
	"path/filepath"
	"slices"
	"strconv"
	"strings"

	"github.com/spf13/cobra"

	"github.com/swissknifetools/passnotp/internal/otp"
	"github.com/swissknifetools/passnotp/internal/vault"
)

var errLocked = errors.New("vault is locked")

// app holds what one invocation needs: paths, the prompter and the vault,
// which is unlocked at most once.
type app struct {
	paths Paths
	p     *prompter
	v     *vault.Vault
}

func (a *app) prompter(cmd *cobra.Command) *prompter {
	if a.p == nil {
		a.p = newPrompter(cmd.InOrStdin(), cmd.ErrOrStderr())
	}
	return a.p
}

// vaultID names the vault in the OS keyring.
func (a *app) vaultID() string {
	if abs, err := filepath.Abs(a.paths.Vault); err == nil {
		return abs
	}
	return a.paths.Vault
}

// openVault unlocks the vault with the cached key, or else the master
// password. It returns nil, nil when there is no vault yet. When
// interactive is false it never prompts and returns errLocked instead.
func (a *app) openVault(cmd *cobra.Command, interactive bool) (*vault.Vault, error) {
	if a.v != nil {
		return a.v, nil
	}
	if !vault.Exists(a.paths.Vault) {
		return nil, nil
	}
	locked, err := vault.Open(a.paths.Vault)
	if err != nil {
		return nil, err
	}
	if key, err := keyStore.Get(a.vaultID()); err == nil {
		if v, err := locked.UnlockWithKey(key); err == nil {
			a.v = v
			return v, nil
		}
	}
	if !interactive {
		return nil, errLocked
	}
	pw, err := a.prompter(cmd).secret("Master password: ")
	if err != nil {
		return nil, err
	}
	v, err := locked.UnlockWithPassword(pw)
	if err != nil {
		return nil, err
	}
	a.v = v
	a.cacheKey(cmd, v)
	return v, nil
}

// vaultForWrite opens the vault, creating it first if there is none.
func (a *app) vaultForWrite(cmd *cobra.Command) (*vault.Vault, error) {
	v, err := a.openVault(cmd, true)
	if err != nil || v != nil {
		return v, err
	}
	fmt.Fprintf(cmd.ErrOrStderr(), "No vault yet, creating one at %s\n", a.paths.Vault)
	return a.createVault(cmd)
}

func (a *app) createVault(cmd *cobra.Command) (*vault.Vault, error) {
	fmt.Fprintf(cmd.ErrOrStderr(), "Choose a master password of at least %d characters; a few random words work well. It opens the vault on a new computer; on this one the OS keyring remembers it.\n", vault.MinPassword)
	pw, err := a.prompter(cmd).newSecret("master password")
	if err != nil {
		return nil, err
	}
	v, err := vault.Create(a.paths.Vault, pw)
	if err != nil {
		return nil, err
	}
	a.v = v
	a.cacheKey(cmd, v)
	return v, nil
}

func (a *app) cacheKey(cmd *cobra.Command, v *vault.Vault) {
	if err := keyStore.Set(a.vaultID(), v.Key()); err != nil {
		fmt.Fprintln(cmd.ErrOrStderr(), "Note: no OS keyring available, so the master password will be asked each time.")
		return
	}
	fmt.Fprintln(cmd.ErrOrStderr(), "Vault key saved to the OS keyring; no master password needed on this machine from now on.")
}

// findPassword reports whether name exists in the vault and, if so, its value.
func (a *app) findPassword(cmd *cobra.Command, name string) (string, bool, error) {
	v, err := a.openVault(cmd, true)
	if err != nil || v == nil {
		return "", false, err
	}
	p, ok := v.Data.Passwords[name]
	return p.Value, ok, nil
}

func (a *app) findOTP(cmd *cobra.Command, name string) (otp.Params, bool, error) {
	v, err := a.openVault(cmd, true)
	if err != nil || v == nil {
		return otp.Params{}, false, err
	}
	e, ok := v.Data.OTP[name]
	return toParams(e), ok, nil
}

// notFound explains a missing entry, pointing new users at how to start.
func (a *app) notFound(name string) error {
	if !vault.Exists(a.paths.Vault) {
		return fmt.Errorf("'%s' does not exist: the vault is empty, add entries with `pass add` or `otp add`", name)
	}
	return fmt.Errorf("'%s' does not exist", name)
}

// passwordNames lists the vault's password names. With interactive false
// (tab completion) a vault that needs the master password yields no names
// instead of prompting.
func (a *app) passwordNames(cmd *cobra.Command, interactive bool) ([]string, error) {
	v, err := a.openVault(cmd, interactive)
	if errors.Is(err, errLocked) {
		return nil, nil
	}
	if err != nil || v == nil {
		return nil, err
	}
	return slices.Sorted(maps.Keys(v.Data.Passwords)), nil
}

func (a *app) otpNames(cmd *cobra.Command, interactive bool) ([]string, error) {
	v, err := a.openVault(cmd, interactive)
	if errors.Is(err, errLocked) {
		return nil, nil
	}
	if err != nil || v == nil {
		return nil, err
	}
	return slices.Sorted(maps.Keys(v.Data.OTP)), nil
}

func toParams(e vault.OTP) otp.Params {
	return otp.Params{Secret: e.Secret, Algorithm: e.Algorithm, Digits: e.Digits, Period: e.Period, Issuer: e.Issuer, Account: e.Account}
}

func fromParams(p otp.Params) vault.OTP {
	return vault.OTP{Secret: p.Secret, Algorithm: p.Algorithm, Digits: p.Digits, Period: p.Period, Issuer: p.Issuer, Account: p.Account, Updated: now()}
}

// nameArg returns the entry name given on the command line, or asks for it.
func (a *app) nameArg(cmd *cobra.Command, args []string) (string, error) {
	if len(args) > 0 {
		return args[0], nil
	}
	name, err := a.prompter(cmd).line("Name: ")
	if err != nil {
		return "", err
	}
	if name = strings.TrimSpace(name); name == "" {
		return "", errors.New("a name is required")
	}
	return name, nil
}

// pickName returns the existing entry named on the command line, or asks
// for part of a name and lets the user choose among the matches. An empty
// answer lists every entry.
func (a *app) pickName(cmd *cobra.Command, args []string, names func(*cobra.Command, bool) ([]string, error)) (string, error) {
	if len(args) > 0 {
		return args[0], nil
	}
	all, err := names(cmd, true)
	if err != nil {
		return "", err
	}
	p := a.prompter(cmd)
	typed, err := p.line("Name (type part of it to search, Enter to list all): ")
	if err != nil {
		return "", err
	}
	typed = strings.TrimSpace(typed)
	if slices.Contains(all, typed) {
		return typed, nil
	}
	var matches []string
	for _, n := range all {
		if strings.Contains(strings.ToLower(n), strings.ToLower(typed)) {
			matches = append(matches, n)
		}
	}
	if len(matches) == 0 {
		return "", fmt.Errorf("nothing matches '%s'", typed)
	}
	for i, m := range matches {
		fmt.Fprintf(p.w, "  %d) %s\n", i+1, m)
	}
	choice, err := p.line("Choice [1]: ")
	if err != nil {
		return "", err
	}
	n := 1
	if choice = strings.TrimSpace(choice); choice != "" {
		if n, err = strconv.Atoi(choice); err != nil || n < 1 || n > len(matches) {
			return "", fmt.Errorf("invalid choice %q", choice)
		}
	}
	return matches[n-1], nil
}

var reservedNames = []string{"ls", "list", "add", "update", "delete", "scan", "help"}

func checkName(name string) error {
	switch {
	case name == "" || strings.ContainsAny(name, " \t\n"):
		return fmt.Errorf("invalid name %q: no spaces allowed", name)
	case strings.HasPrefix(name, "-"):
		return fmt.Errorf("invalid name %q: cannot start with '-'", name)
	case slices.Contains(reservedNames, name):
		return fmt.Errorf("'%s' is a command name and cannot be used as an entry name", name)
	}
	return nil
}

// completeWith adapts a names function for cobra's ValidArgsFunction,
// completing only the first argument and never prompting.
func completeWith(names func(*cobra.Command, bool) ([]string, error)) cobra.CompletionFunc {
	return func(cmd *cobra.Command, args []string, _ string) ([]string, cobra.ShellCompDirective) {
		if len(args) > 0 {
			return nil, cobra.ShellCompDirectiveNoFileComp
		}
		n, _ := names(cmd, false)
		return n, cobra.ShellCompDirectiveNoFileComp
	}
}
