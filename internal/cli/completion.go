package cli

import (
	"fmt"
	"io"

	"github.com/spf13/cobra"
)

// The alias completions complete the short `pass` and `otp` names by asking
// `passnotp __complete pass|otp ...`, the same backend cobra uses.
const aliasBashCompletion = `
_passnotp_alias() {
    local cur="${COMP_WORDS[COMP_CWORD]}" out
    out=$(command passnotp __completeNoDesc "${COMP_WORDS[0]}" "${COMP_WORDS[@]:1:COMP_CWORD}" 2>/dev/null) || return
    COMPREPLY=($(compgen -W "$(sed '$d' <<<"$out")" -- "$cur"))
}
complete -F _passnotp_alias pass otp
`

const aliasZshCompletion = `
_passnotp_alias() {
    local -a comps
    comps=("${(@f)$(command passnotp __completeNoDesc "${words[1]}" "${(@)words[2,CURRENT]}" 2>/dev/null)}")
    compadd -- "${(@)comps[1,-2]}"
}
compdef _passnotp_alias pass otp
`

const aliasFishCompletion = `
for alias in pass otp
    complete -c $alias -f -a "(passnotp __completeNoDesc $alias (commandline -opc)[2..-1] (commandline -ct) 2>/dev/null | sed '\$d')"
end
`

func newCompletionCmd() *cobra.Command {
	return &cobra.Command{
		Use:       "completion bash|zsh|fish|powershell",
		Short:     "Print a shell completion script.",
		Long:      "Print a shell completion script, which also completes the short `pass` and `otp` names.\n\nTry it in the current shell only:  source <(passnotp completion bash)",
		Args:      cobra.MatchAll(cobra.ExactArgs(1), cobra.OnlyValidArgs),
		ValidArgs: []string{"bash", "zsh", "fish", "powershell"},
		RunE: func(cmd *cobra.Command, args []string) error {
			out := cmd.OutOrStdout()
			root := cmd.Root()
			switch args[0] {
			case "bash":
				if err := root.GenBashCompletionV2(out, false); err != nil {
					return err
				}
				_, err := io.WriteString(out, aliasBashCompletion)
				return err
			case "zsh":
				if err := root.GenZshCompletion(out); err != nil {
					return err
				}
				_, err := io.WriteString(out, aliasZshCompletion)
				return err
			case "fish":
				if err := root.GenFishCompletion(out, false); err != nil {
					return err
				}
				_, err := io.WriteString(out, aliasFishCompletion)
				return err
			case "powershell":
				return root.GenPowerShellCompletionWithDesc(out)
			}
			return fmt.Errorf("unknown shell %q", args[0])
		},
	}
}
