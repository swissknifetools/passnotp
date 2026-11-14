package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/swissknifetools/passnotp/internal/cli"
)

func main() {
	args := os.Args[1:]
	// When invoked through a `pass` or `otp` symlink, behave like
	// `passnotp pass ...` / `passnotp otp ...`.
	switch name := strings.TrimSuffix(filepath.Base(os.Args[0]), ".exe"); name {
	case "pass", "otp":
		args = cli.AliasArgs(name, args)
	}

	root := cli.NewRoot(cli.DefaultPaths())
	root.SetArgs(args)
	if err := root.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
