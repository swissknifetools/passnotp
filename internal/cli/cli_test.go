package cli

import (
	"bytes"
	"errors"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
	"time"

	"github.com/pquerna/otp/totp"
	"github.com/zalando/go-keyring"

	"github.com/swissknifetools/passnotp/internal/otp"
	"github.com/swissknifetools/passnotp/internal/vault"
)

const master = "correct horse battery"

// memKeyStore is an in-memory OS keyring.
type memKeyStore map[string][]byte

func (m memKeyStore) Get(id string) ([]byte, error) {
	if k, ok := m[id]; ok {
		return k, nil
	}
	return nil, keyring.ErrNotFound
}
func (m memKeyStore) Set(id string, k []byte) error { m[id] = k; return nil }
func (m memKeyStore) Delete(id string) error {
	if _, ok := m[id]; !ok {
		return keyring.ErrNotFound
	}
	delete(m, id)
	return nil
}

type env struct {
	t       *testing.T
	paths   Paths
	keys    memKeyStore
	cleared []string // values scheduled for clearing from the clipboard
}

// newEnv uses a fresh vault path, with the clock pinned and the keyring
// and clipboard replaced.
func newEnv(t *testing.T) *env {
	e := &env{
		t:     t,
		paths: Paths{Vault: filepath.Join(t.TempDir(), "passnotp", "vault.json")},
		keys:  memKeyStore{},
	}
	origKeys, origNow, origClear := keyStore, now, scheduleClear
	keyStore, now = e.keys, func() time.Time { return time.Unix(59, 0) }
	scheduleClear = func(v string, _ time.Duration) error { e.cleared = append(e.cleared, v); return nil }
	t.Cleanup(func() { keyStore, now, scheduleClear = origKeys, origNow, origClear })
	return e
}

const tricky = `it's a \back\slash & $dollar`

// seed creates the vault with passwords github (hunter2) and tricky, and
// OTP accounts rfc6238 (the RFC 6238 test secret) and other.
func (e *env) seed() {
	e.t.Helper()
	e.mustRun(lines(master, master, "hunter2", "hunter2"), "pass", "add", "github")
	e.mustRun(lines(tricky, tricky), "pass", "add", "tricky")
	e.mustRun(lines("4", "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"), "otp", "add", "rfc6238")
	e.mustRun(lines("4", "JBSWY3DPEHPK3PXP"), "otp", "add", "other")
}

type result struct {
	stdout, stderr, copied string
	err                    error
}

// run executes the command tree with stdin as the answers to any prompts.
func (e *env) run(stdin string, args ...string) result {
	e.t.Helper()
	var r result
	orig := copyToClipboard
	copyToClipboard = func(s string) error { r.copied = s; return nil }
	defer func() { copyToClipboard = orig }()

	var out, errOut bytes.Buffer
	root := NewRoot(e.paths)
	root.SetIn(strings.NewReader(stdin))
	root.SetOut(&out)
	root.SetErr(&errOut)
	root.SetArgs(args)
	r.err = root.Execute()
	r.stdout, r.stderr = out.String(), errOut.String()
	return r
}

func (e *env) mustRun(stdin string, args ...string) result {
	e.t.Helper()
	r := e.run(stdin, args...)
	if r.err != nil {
		e.t.Fatalf("%v: %v\nstderr: %s", args, r.err, r.stderr)
	}
	return r
}

func lines(s ...string) string { return strings.Join(s, "\n") + "\n" }

func TestPassCopies(t *testing.T) {
	e := newEnv(t)
	e.seed()
	for _, args := range [][]string{{"pass", "github"}, {"p", "github"}, AliasArgs("pass", []string{"github"})} {
		r := e.mustRun("", args...)
		if r.copied != "hunter2" || !strings.Contains(r.stderr, "Copied 'github'") {
			t.Errorf("%v: copied=%q stderr=%q", args, r.copied, r.stderr)
		}
	}
	if r := e.mustRun("", "pass", "github", "--print"); r.stdout != "hunter2\n" || r.copied != "" {
		t.Errorf("--print: stdout=%q copied=%q", r.stdout, r.copied)
	}
	if r := e.run("", "pass", "nope"); r.err == nil || r.err.Error() != "'nope' does not exist" {
		t.Errorf("missing: %v", r.err)
	}
	if r := e.mustRun("", AliasArgs("otp", []string{"rfc6238"})...); r.copied != "287082" {
		t.Errorf("otp copied %q, want 287082", r.copied)
	}
}

func TestNoVault(t *testing.T) {
	e := newEnv(t)
	r := e.run("", "pass", "github")
	if r.err == nil || !strings.Contains(r.err.Error(), "the vault is empty") {
		t.Errorf("no vault: %v", r.err)
	}
	if r := e.mustRun("", "pass", "ls"); r.stdout != "" {
		t.Errorf("ls without a vault = %q", r.stdout)
	}
	if vault.Exists(e.paths.Vault) {
		t.Error("reading created a vault")
	}
}

func TestPassAddCreatesVaultAndCachesKey(t *testing.T) {
	e := newEnv(t)
	e.mustRun(lines(master, master, "s3cret", "s3cret"), "pass", "add", "newsite")
	if len(e.keys) != 1 {
		t.Fatal("vault key was not cached in the keyring")
	}
	// No stdin: must unlock through the keyring without prompting.
	if r := e.mustRun("", "pass", "newsite"); r.copied != "s3cret" {
		t.Errorf("copied %q", r.copied)
	}
	if r := e.mustRun("", "pass", "ls"); r.stdout != "newsite\n" {
		t.Errorf("ls = %q", r.stdout)
	}
	if r := e.run(lines("x", "x"), "pass", "add", "newsite"); r.err == nil || !strings.Contains(r.err.Error(), "already exists") {
		t.Errorf("adding an existing name: %v", r.err)
	}
	if r := e.run(lines("a", "b"), "pass", "add", "other"); r.err == nil || !strings.Contains(r.err.Error(), "do not match") {
		t.Errorf("mismatched passwords: %v", r.err)
	}
	if r := e.run("", "pass", "add", "ls"); r.err == nil {
		t.Error("reserved name accepted")
	}
}

func TestNewMachineUnlocksWithMasterPassword(t *testing.T) {
	e := newEnv(t)
	e.mustRun(lines(master, master, "s3cret", "s3cret"), "pass", "add", "newsite")
	clear(e.keys) // the vault file was copied to a machine with an empty keyring

	if r := e.run(lines("wrong password"), "pass", "newsite"); r.err == nil {
		t.Fatal("wrong master password accepted")
	}
	r := e.mustRun(lines(master), "pass", "newsite")
	if r.copied != "s3cret" || len(e.keys) != 1 {
		t.Errorf("copied=%q keys=%d", r.copied, len(e.keys))
	}

	e.mustRun("", "lock")
	if len(e.keys) != 0 {
		t.Error("lock did not remove the key")
	}
}

func TestUpdateAndDelete(t *testing.T) {
	e := newEnv(t)
	e.seed()
	e.mustRun(lines("newvalue", "newvalue"), "pass", "update", "github")
	if r := e.mustRun("", "pass", "github"); r.copied != "newvalue" {
		t.Errorf("after update copied %q", r.copied)
	}
	if r := e.run("", "pass", "update", "nope"); r.err == nil {
		t.Error("updating a missing entry succeeded")
	}
	if r := e.mustRun(lines("n"), "pass", "delete", "github"); !strings.Contains(r.stderr, "Cancelled") {
		t.Errorf("declined delete: %q", r.stderr)
	}
	if r := e.mustRun("", "pass", "delete", "github", "-y"); !strings.Contains(r.stderr, "Deleted 'github'") {
		t.Errorf("delete stderr = %q", r.stderr)
	}
	if r := e.run("", "pass", "delete", "github", "-y"); r.err == nil || !strings.Contains(r.err.Error(), "does not exist") {
		t.Errorf("deleting twice: %v", r.err)
	}
}

func TestExportImportToNewComputer(t *testing.T) {
	old := newEnv(t)
	old.seed()
	file := filepath.Join(t.TempDir(), "backup.json")
	r := old.mustRun(lines("'"+file+"'"), "export")
	if !strings.Contains(r.stderr, "Exported 2 passwords and 2 OTP accounts") {
		t.Errorf("export stderr = %q", r.stderr)
	}
	if b, _ := os.ReadFile(file); bytes.Contains(b, []byte("hunter2")) {
		t.Error("export is not encrypted")
	}
	if r := old.mustRun(lines("n"), "export", file); !strings.Contains(r.stderr, "Cancelled") {
		t.Errorf("overwrite not confirmed: %q", r.stderr)
	}
	if r := old.run("", "export", old.paths.Vault); r.err == nil {
		t.Error("exported onto the vault itself")
	}

	// A new computer: no vault and an empty keyring.
	nu := newEnv(t)
	if r := nu.run(lines("wrong password"), "import", file); !errors.Is(r.err, vault.ErrWrongPassword) {
		t.Fatalf("wrong password: %v", r.err)
	}
	r = nu.mustRun(lines(master), "import", file)
	if !strings.Contains(r.stderr, "Imported 2 passwords and 2 OTP accounts") || len(nu.keys) != 1 {
		t.Errorf("import stderr = %q, keys = %d", r.stderr, len(nu.keys))
	}
	if r := nu.mustRun("", "pass", "tricky"); r.copied != tricky {
		t.Errorf("copied %q", r.copied)
	}
	if r := nu.mustRun("", "otp", "rfc6238"); r.copied != "287082" {
		t.Errorf("otp copied %q", r.copied)
	}
}

func TestImportMerges(t *testing.T) {
	other := newEnv(t)
	other.mustRun(lines("other master", "other master", "hunter2", "hunter2"), "pass", "add", "github")
	other.mustRun(lines("x", "x"), "pass", "add", "tricky")
	other.mustRun(lines("n", "n"), "pass", "add", "fromother")
	file := filepath.Join(t.TempDir(), "other.json")
	other.mustRun("", "export", file)

	e := newEnv(t)
	e.seed()
	r := e.mustRun(lines("other master"), "import", file)
	if !strings.Contains(r.stderr, "Imported 1 passwords and 0 OTP accounts (1 already in the vault)") ||
		!strings.Contains(r.stderr, "kept this vault's value: pass tricky") {
		t.Errorf("merge stderr = %q", r.stderr)
	}
	if r := e.mustRun("", "pass", "fromother"); r.copied != "n" {
		t.Errorf("merged entry copied %q", r.copied)
	}
	if r := e.mustRun("", "pass", "tricky"); r.copied != tricky {
		t.Errorf("conflict overwrote the vault: %q", r.copied)
	}

	// A copy of this vault opens with its key, without asking.
	own := filepath.Join(t.TempDir(), "own.json")
	e.mustRun("", "export", own)
	e.mustRun("", "pass", "delete", "github", "-y")
	r = e.mustRun("", "import", own)
	if !strings.Contains(r.stderr, "Imported 1 passwords and 0 OTP accounts") {
		t.Errorf("own copy stderr = %q", r.stderr)
	}
}

// qrImage returns a QR code for a new TOTP account, as an image and a file.
func qrImage(t *testing.T) (image.Image, string, otp.Params) {
	key, err := totp.Generate(totp.GenerateOpts{Issuer: "GitHub", AccountName: "alice@example.com"})
	if err != nil {
		t.Fatal(err)
	}
	img, err := key.Image(300, 300)
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(t.TempDir(), "qr.png")
	f, _ := os.Create(path)
	png.Encode(f, img)
	f.Close()
	return img, path, otp.FromSecret(key.Secret())
}

func TestOTPAddFromQR(t *testing.T) {
	e := newEnv(t)
	img, path, p := qrImage(t)
	want, _ := otp.Code(p, now())

	r := e.mustRun(lines(master, master), "otp", "add", "gh", "--image", path)
	if !strings.Contains(r.stderr, "Found: GitHub (alice@example.com)") || r.copied != want {
		t.Errorf("--image: stderr=%q copied=%q want %q", r.stderr, r.copied, want)
	}
	if r := e.mustRun("", "o", "gh"); r.copied != want {
		t.Errorf("saved account copied %q, want %q", r.copied, want)
	}

	orig := captureRegion
	captureRegion = func() (image.Image, error) { return img, nil }
	t.Cleanup(func() { captureRegion = orig })
	if r := e.mustRun("", "otp", "add", "gh2", "--scan"); r.copied != want {
		t.Errorf("--scan copied %q", r.copied)
	}
	if r := e.run("", "otp", "add", "gh", "--scan"); r.err == nil {
		t.Error("adding an existing name succeeded")
	}
}

func TestOTPAddFromPrompt(t *testing.T) {
	e := newEnv(t)
	e.mustRun(lines("4", "jbsw y3dp ehpk 3pxp", master, master), "otp", "add", "manual")
	want, _ := otp.Code(otp.FromSecret("JBSWY3DPEHPK3PXP"), now())
	if r := e.mustRun("", "otp", "manual"); r.copied != want {
		t.Errorf("copied %q, want %q", r.copied, want)
	}
	if r := e.run(lines("4", "not a secret!"), "otp", "add", "bad"); r.err == nil {
		t.Error("invalid secret accepted")
	}
}

func TestOTPScanDoesNotSave(t *testing.T) {
	e := newEnv(t)
	img, _, p := qrImage(t)
	orig := captureClipboard
	captureClipboard = func() (image.Image, error) { return img, nil }
	t.Cleanup(func() { captureClipboard = orig })

	want, _ := otp.Code(p, now())
	r := e.mustRun("", "otp", "scan", "--clipboard")
	if r.copied != want || !strings.Contains(r.stderr, "Copied 'GitHub (alice@example.com)'") {
		t.Errorf("copied=%q stderr=%q", r.copied, r.stderr)
	}
	if vault.Exists(e.paths.Vault) {
		t.Error("scan created a vault")
	}
}

func TestCompletion(t *testing.T) {
	e := newEnv(t)
	e.seed()
	e.mustRun(lines("v", "v"), "pass", "add", "invault")

	check := func(args []string, want ...string) {
		t.Helper()
		r := e.mustRun("", args...)
		got := strings.Split(r.stdout, "\n")
		for _, w := range want {
			if !slices.ContainsFunc(got, func(l string) bool { return strings.HasPrefix(l, w) }) {
				t.Errorf("%v: missing %q in\n%s", args, w, r.stdout)
			}
		}
	}
	check(AliasArgs("pass", []string{"__complete", ""}), "github", "invault", "tricky", "ls", "add")
	check(AliasArgs("otp", []string{"__complete", ""}), "other", "rfc6238", "scan")
	check([]string{"__complete", "o", "rf"}, "rfc6238")
	check(AliasArgs("pass", []string{"__complete", "delete", ""}), "invault")

	// With an empty keyring, completion must not prompt (stdin is empty,
	// so a prompt would fail the run); it only offers subcommands.
	clear(e.keys)
	check(AliasArgs("pass", []string{"__complete", ""}), "ls", "add")
}

func TestInteractiveAdd(t *testing.T) {
	e := newEnv(t)
	e.mustRun(lines("site", master, master, "s3cret", "s3cret"), "pass", "add")
	if r := e.mustRun("", "pass", "site"); r.copied != "s3cret" {
		t.Errorf("pass add without args: copied %q", r.copied)
	}
	if r := e.run(lines(""), "pass", "add"); r.err == nil || !strings.Contains(r.err.Error(), "name is required") {
		t.Errorf("empty name: %v", r.err)
	}

	img, path, p := qrImage(t)
	want, _ := otp.Code(p, now())
	orig, origCan := captureRegion, canSelectRegion
	captureRegion = func() (image.Image, error) { return img, nil }
	canSelectRegion = func() bool { return true }
	t.Cleanup(func() { captureRegion, canSelectRegion = orig, origCan })

	// Enter at the menu means "select on screen".
	r := e.mustRun(lines("viascan", ""), "otp", "add")
	if r.copied != want || !strings.Contains(r.stderr, "How do you want to add it?") {
		t.Errorf("default choice: copied=%q stderr=%q", r.copied, r.stderr)
	}
	// Choice 3 with a quoted path, as when dragging a file into the terminal.
	if r := e.mustRun(lines("viafile", "3", "'"+path+"'"), "otp", "add"); r.copied != want {
		t.Errorf("image file choice: copied %q", r.copied)
	}
	if r := e.run(lines("x", "9"), "otp", "add"); r.err == nil || !strings.Contains(r.err.Error(), "invalid choice") {
		t.Errorf("invalid choice: %v", r.err)
	}

	e.mustRun(lines("viafile", "y"), "otp", "delete")
	if r := e.run("", "otp", "viafile"); r.err == nil {
		t.Error("interactive delete did not delete")
	}
}

func TestPickNameSearch(t *testing.T) {
	e := newEnv(t)
	e.seed()
	// "git" matches only github; Enter picks the first match.
	r := e.mustRun(lines("git", "", "nv", "nv"), "pass", "update")
	if !strings.Contains(r.stderr, "1) github") {
		t.Errorf("search list: %q", r.stderr)
	}
	if r := e.mustRun("", "pass", "github"); r.copied != "nv" {
		t.Errorf("after update copied %q", r.copied)
	}
	// Enter lists everything; pick by number, then confirm.
	r = e.mustRun(lines("", "1", "y"), "pass", "delete")
	if !strings.Contains(r.stderr, "2) tricky") || !strings.Contains(r.stderr, "Deleted 'github'") {
		t.Errorf("list all + delete: %q", r.stderr)
	}
	if r := e.run(lines("zzz"), "pass", "delete"); r.err == nil || !strings.Contains(r.err.Error(), "nothing matches") {
		t.Errorf("no match: %v", r.err)
	}
	if r := e.run(lines("", "99"), "pass", "update"); r.err == nil || !strings.Contains(r.err.Error(), "invalid choice") {
		t.Errorf("bad number: %v", r.err)
	}
}

func TestMenuDefaultsToClipboardWithoutRegionSelect(t *testing.T) {
	e := newEnv(t)
	img, _, p := qrImage(t)
	origC, origR := captureClipboard, canSelectRegion
	captureClipboard = func() (image.Image, error) { return img, nil }
	canSelectRegion = func() bool { return false }
	t.Cleanup(func() { captureClipboard, canSelectRegion = origC, origR })

	want, _ := otp.Code(p, now())
	r := e.mustRun(lines("win", "", master, master), "otp", "add")
	if r.copied != want || !strings.Contains(r.stderr, "Choice [2]") {
		t.Errorf("copied=%q stderr=%q", r.copied, r.stderr)
	}
}

func TestClipboardIsCleared(t *testing.T) {
	e := newEnv(t)
	e.seed()
	e.cleared = nil
	r := e.mustRun("", "pass", "github")
	if !strings.Contains(r.stderr, "clearing it in 45s") || !slices.Equal(e.cleared, []string{"hunter2"}) {
		t.Errorf("stderr=%q cleared=%q", r.stderr, e.cleared)
	}
	if e.mustRun("", "pass", "github", "--print"); len(e.cleared) != 1 {
		t.Error("--print scheduled a clear")
	}

	t.Setenv("PASSNOTP_CLEAR_SECONDS", "0")
	if r := e.mustRun("", "otp", "rfc6238"); strings.Contains(r.stderr, "clearing") || len(e.cleared) != 1 {
		t.Errorf("clearing not turned off: stderr=%q", r.stderr)
	}
	t.Setenv("PASSNOTP_CLEAR_SECONDS", "10")
	if r := e.mustRun("", "otp", "rfc6238"); !strings.Contains(r.stderr, "clearing it in 10s") {
		t.Errorf("custom delay: %q", r.stderr)
	}
}

func TestClearIfUnchanged(t *testing.T) {
	for _, tc := range []struct {
		clip  string
		clear bool
	}{{"hunter2", true}, {"something else", false}} {
		written := "untouched"
		read := func() (string, error) { return tc.clip, nil }
		write := func(s string) error { written = s; return nil }
		if err := clearIfUnchanged(hashOf("hunter2"), read, write); err != nil {
			t.Fatal(err)
		}
		if got := written == ""; got != tc.clear {
			t.Errorf("clipboard %q: cleared=%v, want %v", tc.clip, got, tc.clear)
		}
	}
	if got := AliasArgs("pass", []string{clearCmdName, "45"}); got[0] != clearCmdName {
		t.Errorf("AliasArgs = %q", got)
	}
}
