# passnotp

Passwords and 2FA codes, one command away. Type `pass github` and the password
is on your clipboard. Type `otp github` and so is the code.

## Install

**Linux / macOS**

```sh
curl -fsSL https://raw.githubusercontent.com/swissknifetools/passnotp/main/install.sh | sh
```

**Windows** (PowerShell)

```powershell
irm https://raw.githubusercontent.com/swissknifetools/passnotp/main/install.ps1 | iex
```

Then open a new terminal. On Linux the installer also sets up the clipboard and
screenshot tools it needs; macOS and Windows already have them.

## Use

```sh
pass add            # save a password
pass github         # copy it
otp add             # save a 2FA account: select its QR code on screen
otp github          # copy the current code
```

`ls`, `update` and `delete` work for both, and everything asks for what you
leave out. Tab completes names.

## Security

Everything lives in one encrypted file (AES-256-GCM), locked with a master
password you choose the first time. Your OS keyring remembers it, so there are
no prompts day to day. Forget the master password and the vault cannot be
opened, so keep it somewhere safe.

Copied secrets are cleared from the clipboard after 45 seconds. Set
`PASSNOTP_CLEAR_SECONDS` to change that, or to `0` to keep them.

## New computer

```sh
passnotp export           # on the old one: saves passnotp-vault.json
passnotp import <file>    # on the new one, after installing
```

The exported file stays encrypted, so it is safe on a USB stick or in the
cloud. Importing into an existing vault adds what is missing.

## More

- `passnotp passwd`: change the master password
- Uninstall: `curl -fsSL https://raw.githubusercontent.com/swissknifetools/passnotp/main/install.sh | sh -s -- --uninstall`
