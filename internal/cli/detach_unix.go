//go:build !windows

package cli

import (
	"os/exec"
	"syscall"
)

// detach starts c in its own session, so closing the terminal does not
// stop it.
func detach(c *exec.Cmd) {
	c.SysProcAttr = &syscall.SysProcAttr{Setsid: true}
}
