package cli

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"time"

	"github.com/atotto/clipboard"
	"github.com/spf13/cobra"
)

const (
	clearCmdName     = "__clear-clipboard"
	clearHashEnv     = "PASSNOTP_CLEAR_HASH"
	defaultClearSecs = 45
)

// clearAfter is how long a copied secret stays on the clipboard;
// PASSNOTP_CLEAR_SECONDS overrides it and 0 turns clearing off.
func clearAfter() time.Duration {
	s, err := strconv.Atoi(os.Getenv("PASSNOTP_CLEAR_SECONDS"))
	if err != nil || s < 0 {
		s = defaultClearSecs
	}
	return time.Duration(s) * time.Second
}

func hashOf(s string) string {
	sum := sha256.Sum256([]byte(s))
	return hex.EncodeToString(sum[:])
}

// scheduleClear starts a detached passnotp that empties the clipboard after
// d, unless something else has been copied meanwhile. Only a hash of the
// secret is passed to it.
var scheduleClear = func(value string, d time.Duration) error {
	exe, err := os.Executable()
	if err != nil {
		return err
	}
	c := exec.Command(exe, clearCmdName, strconv.Itoa(int(d.Seconds())))
	c.Env = append(os.Environ(), clearHashEnv+"="+hashOf(value))
	detach(c)
	if err := c.Start(); err != nil {
		return err
	}
	return c.Process.Release()
}

// clearIfUnchanged empties the clipboard if it still holds the secret
// with the given hash.
func clearIfUnchanged(hash string, read func() (string, error), write func(string) error) error {
	cur, err := read()
	if err != nil || hashOf(cur) != hash {
		return err
	}
	return write("")
}

func newClearCmd() *cobra.Command {
	return &cobra.Command{
		Use:    clearCmdName + " <seconds>",
		Hidden: true,
		Args:   cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			secs, err := strconv.Atoi(args[0])
			if err != nil {
				return fmt.Errorf("invalid seconds %q", args[0])
			}
			hash := os.Getenv(clearHashEnv)
			if hash == "" {
				return fmt.Errorf("%s is not set", clearHashEnv)
			}
			time.Sleep(time.Duration(secs) * time.Second)
			return clearIfUnchanged(hash, clipboard.ReadAll, clipboard.WriteAll)
		},
	}
}
