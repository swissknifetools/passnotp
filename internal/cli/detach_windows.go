package cli

import (
	"os/exec"
	"syscall"
)

// detach starts c without a console, so closing the terminal does not
// stop it.
func detach(c *exec.Cmd) {
	const detachedProcess = 0x00000008
	c.SysProcAttr = &syscall.SysProcAttr{CreationFlags: detachedProcess | syscall.CREATE_NEW_PROCESS_GROUP}
}
