package cli

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"strings"

	"golang.org/x/term"
)

// prompter asks questions on stderr. Secrets are read without echo when
// stdin is a terminal; otherwise one line is read per answer, which keeps
// it scriptable and testable.
type prompter struct {
	r   *bufio.Reader
	w   io.Writer
	fd  int
	tty bool
}

func newPrompter(in io.Reader, w io.Writer) *prompter {
	p := &prompter{r: bufio.NewReader(in), w: w}
	if f, ok := in.(*os.File); ok && term.IsTerminal(int(f.Fd())) {
		p.tty, p.fd = true, int(f.Fd())
	}
	return p
}

func (p *prompter) line(label string) (string, error) {
	fmt.Fprint(p.w, label)
	s, err := p.r.ReadString('\n')
	if errors.Is(err, io.EOF) && s != "" {
		err = nil
	}
	return strings.TrimRight(s, "\r\n"), err
}

func (p *prompter) secret(label string) (string, error) {
	if !p.tty {
		return p.line(label)
	}
	fmt.Fprint(p.w, label)
	b, err := term.ReadPassword(p.fd)
	fmt.Fprintln(p.w)
	return string(b), err
}

// newSecret asks twice and checks both answers match.
func (p *prompter) newSecret(what string) (string, error) {
	a, err := p.secret("Enter " + what + ": ")
	if err != nil {
		return "", err
	}
	if a == "" {
		return "", fmt.Errorf("the %s cannot be empty", what)
	}
	b, err := p.secret("Confirm " + what + ": ")
	if err != nil {
		return "", err
	}
	if a != b {
		return "", fmt.Errorf("%ss do not match", what)
	}
	return a, nil
}

func (p *prompter) confirm(label string) (bool, error) {
	s, err := p.line(label)
	if err != nil {
		return false, err
	}
	s = strings.ToLower(strings.TrimSpace(s))
	return s == "y" || s == "yes", nil
}
