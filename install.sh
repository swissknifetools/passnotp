#!/bin/sh
# passnotp installer for Linux and macOS.
#
#   curl -fsSL https://raw.githubusercontent.com/swissknifetools/passnotp/main/install.sh | sh
#   sh install.sh --uninstall
#
# Installs passnotp into ~/.local/bin with `pass` and `otp` shortcuts, the
# clipboard and screenshot tools it uses (Linux), and shell completion.
#
# Environment:
#   PASSNOTP_BIN_DIR       install directory (default ~/.local/bin)
#   PASSNOTP_VERSION       release tag to install (default: latest)
#   PASSNOTP_NO_DEPS=1     do not install system packages
#   PASSNOTP_DOWNLOAD_URL  base URL of the release archives (mirrors, testing)
set -eu

REPO="swissknifetools/passnotp"
BIN_DIR="${PASSNOTP_BIN_DIR:-$HOME/.local/bin}"
VERSION="${PASSNOTP_VERSION:-latest}"
MARK="# added by passnotp"

say() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mwarning:\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

detect_platform() {
    case "$(uname -s)" in
        Linux) OS=linux ;;
        Darwin) OS=darwin ;;
        *) die "unsupported system $(uname -s); on Windows use install.ps1" ;;
    esac
    case "$(uname -m)" in
        x86_64 | amd64) ARCH=amd64 ;;
        aarch64 | arm64) ARCH=arm64 ;;
        *) die "unsupported architecture $(uname -m)" ;;
    esac
}

# Clipboard and screenshot tools. macOS ships its own; on Linux install
# what is missing for both X11 and Wayland, so switching later just works.
install_deps() {
    [ "$OS" = linux ] || return 0
    [ -z "${PASSNOTP_NO_DEPS:-}" ] || return 0
    if [ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
        say "No desktop session detected, skipping clipboard and screenshot tools"
        return 0
    fi

    pkgs=""
    have xclip || pkgs="$pkgs xclip"
    have wl-copy || pkgs="$pkgs wl-clipboard"
    have flameshot || pkgs="$pkgs flameshot"
    case "${XDG_CURRENT_DESKTOP:-}" in
        *sway* | *Hyprland* | *river* | *wlroots*)
            have grim || pkgs="$pkgs grim"
            have slurp || pkgs="$pkgs slurp"
            ;;
    esac
    if [ -z "$pkgs" ]; then
        say "Clipboard and screenshot tools already installed"
        return 0
    fi

    if have apt-get; then update="apt-get update -qq"; install="apt-get install -y -qq"
    elif have dnf; then update=""; install="dnf install -y -q"
    elif have pacman; then update=""; install="pacman -S --needed --noconfirm"
    elif have zypper; then update=""; install="zypper --quiet install -y"
    elif have apk; then update=""; install="apk add -q"
    else
        warn "unknown package manager, please install:$pkgs"
        return 0
    fi

    sudo=""
    if [ "$(id -u)" -ne 0 ]; then
        if ! have sudo; then
            warn "sudo not found, please install:$pkgs"
            return 0
        fi
        sudo="sudo"
    fi
    say "Installing$pkgs (may ask for your password)"
    # shellcheck disable=SC2086
    { [ -z "$update" ] || $sudo $update >/dev/null; } && $sudo $install $pkgs >/dev/null 2>&1 ||
        warn "could not install:$pkgs (copying works without them; install them for QR scanning)"
}

download() {
    if have curl; then curl -fsSL "$1" -o "$2"
    elif have wget; then wget -q "$1" -O "$2"
    else die "curl or wget is required"
    fi
}

sha256() {
    if have sha256sum; then sha256sum "$1" | cut -d' ' -f1
    else shasum -a 256 "$1" | cut -d' ' -f1
    fi
}

# Puts the passnotp binary at $TMP/passnotp: built from this checkout when
# run from one with Go installed, otherwise downloaded from the release.
get_binary() {
    src=""
    case "$0" in *install.sh) src="$(cd "$(dirname "$0")" && pwd)" ;; esac
    if [ -n "$src" ] && [ -f "$src/go.mod" ] && [ -d "$src/cmd/passnotp" ] && have go; then
        say "Building from $src"
        (cd "$src" && CGO_ENABLED=0 go build -trimpath -o "$TMP/passnotp" ./cmd/passnotp)
        return
    fi

    archive="passnotp_${OS}_${ARCH}.tar.gz"
    if [ -n "${PASSNOTP_DOWNLOAD_URL:-}" ]; then base="$PASSNOTP_DOWNLOAD_URL"
    elif [ "$VERSION" = latest ]; then base="https://github.com/$REPO/releases/latest/download"
    else base="https://github.com/$REPO/releases/download/$VERSION"
    fi

    say "Downloading $archive"
    if download "$base/$archive" "$TMP/$archive" && download "$base/checksums.txt" "$TMP/checksums.txt"; then
        want=$(grep " $archive\$" "$TMP/checksums.txt" | cut -d' ' -f1)
        [ -n "$want" ] && [ "$want" = "$(sha256 "$TMP/$archive")" ] || die "checksum mismatch for $archive"
        tar -xzf "$TMP/$archive" -C "$TMP" passnotp
        return
    fi

    if have go; then
        warn "no release download available, building with go install"
        GOBIN="$TMP" go install "github.com/$REPO/cmd/passnotp@latest"
        return
    fi
    die "could not download passnotp, and Go is not installed to build it"
}

install_binary() {
    mkdir -p "$BIN_DIR"
    cp "$TMP/passnotp" "$BIN_DIR/passnotp.new"
    chmod 755 "$BIN_DIR/passnotp.new"
    mv "$BIN_DIR/passnotp.new" "$BIN_DIR/passnotp"
    say "Installed $BIN_DIR/passnotp ($("$BIN_DIR/passnotp" --version))"

    # `pass` and `otp` shortcuts, unless another command already uses the
    # name (e.g. the `pass` password manager).
    for name in pass otp; do
        link="$BIN_DIR/$name"
        if [ -L "$link" ] && [ "$(readlink "$link")" = passnotp ]; then continue; fi
        other=$(command -v "$name" 2>/dev/null || true)
        if [ -e "$link" ] || { [ -n "$other" ] && [ "$other" != "$link" ]; }; then
            warn "'$name' is already taken by ${other:-$link}; use 'passnotp $name' instead"
            continue
        fi
        ln -s passnotp "$link"
    done
}

# Appends a line to a shell startup file once, tagged so --uninstall can
# remove it.
add_line() {
    file=$1 line=$2
    [ -f "$file" ] && grep -qF "$line" "$file" && return 0
    mkdir -p "$(dirname "$file")"
    printf '%s %s\n' "$line" "$MARK" >>"$file"
    say "Updated $file"
}

setup_shell() {
    on_path=true
    case ":$PATH:" in *":$BIN_DIR:"*) ;; *) on_path=false ;; esac

    case "$(basename "${SHELL:-sh}")" in
        bash)
            rc="$HOME/.bashrc"
            $on_path || add_line "$rc" "export PATH=\"$BIN_DIR:\$PATH\""
            add_line "$rc" 'command -v passnotp >/dev/null && source <(passnotp completion bash)'
            ;;
        zsh)
            rc="${ZDOTDIR:-$HOME}/.zshrc"
            $on_path || add_line "$rc" "export PATH=\"$BIN_DIR:\$PATH\""
            add_line "$rc" 'command -v passnotp >/dev/null && command -v compdef >/dev/null && source <(passnotp completion zsh)'
            ;;
        fish)
            rc="$HOME/.config/fish/conf.d/passnotp.fish"
            $on_path || add_line "$rc" "fish_add_path $BIN_DIR"
            add_line "$rc" 'command -q passnotp; and passnotp completion fish | source'
            ;;
        *)
            $on_path || warn "add $BIN_DIR to your PATH"
            ;;
    esac
}

uninstall() {
    for name in pass otp; do
        link="$BIN_DIR/$name"
        if [ -L "$link" ] && [ "$(readlink "$link")" = passnotp ]; then rm -f "$link"; fi
    done
    rm -f "$BIN_DIR/passnotp"
    for rc in "$HOME/.bashrc" "${ZDOTDIR:-$HOME}/.zshrc" "$HOME/.config/fish/conf.d/passnotp.fish"; do
        [ -f "$rc" ] && grep -qF "$MARK" "$rc" || continue
        kept=$(grep -vF "$MARK" "$rc" || true)
        if [ -z "$kept" ]; then rm -f "$rc"; else printf '%s\n' "$kept" >"$rc"; fi
        say "Cleaned $rc"
    done
    say "passnotp removed. Your vault was kept; delete it yourself if you no longer need it."
}

main() {
    if [ "${1:-}" = "--uninstall" ]; then
        uninstall
        return
    fi
    detect_platform
    TMP=$(mktemp -d)
    trap 'rm -rf "$TMP"' EXIT INT TERM

    install_deps
    get_binary
    install_binary
    setup_shell

    cat <<EOF

$(say "Done! Open a new terminal, then:")
    pass add       save a password
    pass <name>    copy it
    otp add        save a 2FA account (select its QR code on screen)
    otp <name>     copy the current code
EOF
}

main "$@"
