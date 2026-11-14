# passnotp installer for Windows (PowerShell).
#
#   irm https://raw.githubusercontent.com/swissknifetools/passnotp/main/install.ps1 | iex
#
# Installs passnotp.exe with pass.exe and otp.exe shortcuts into
# %LOCALAPPDATA%\passnotp\bin, adds it to your PATH and sets up completion.
$ErrorActionPreference = 'Stop'

$repo = 'swissknifetools/passnotp'
$arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'amd64' }
$archive = "passnotp_windows_$arch.zip"
$base = if ($env:PASSNOTP_DOWNLOAD_URL) { $env:PASSNOTP_DOWNLOAD_URL } else { "https://github.com/$repo/releases/latest/download" }
$dir = Join-Path $env:LOCALAPPDATA 'passnotp\bin'
$tmp = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $dir, $tmp | Out-Null

try {
    Write-Host "==> Downloading $archive"
    Invoke-WebRequest "$base/$archive" -OutFile "$tmp\$archive" -UseBasicParsing
    Invoke-WebRequest "$base/checksums.txt" -OutFile "$tmp\checksums.txt" -UseBasicParsing

    $want = (Select-String -Path "$tmp\checksums.txt" -Pattern " $([regex]::Escape($archive))$").Line.Split(' ')[0]
    $got = (Get-FileHash "$tmp\$archive" -Algorithm SHA256).Hash.ToLower()
    if (-not $want -or $want -ne $got) { throw "checksum mismatch for $archive" }

    Expand-Archive "$tmp\$archive" -DestinationPath $tmp -Force
    foreach ($name in 'passnotp', 'pass', 'otp') {
        Copy-Item "$tmp\passnotp.exe" "$dir\$name.exe" -Force
    }
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($userPath -split ';') -notcontains $dir) {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$dir", 'User')
    Write-Host "==> Added $dir to your PATH"
}

$line = 'if (Get-Command passnotp -ErrorAction SilentlyContinue) { passnotp completion powershell | Out-String | Invoke-Expression } # added by passnotp'
if (-not (Test-Path $PROFILE)) { New-Item -ItemType File -Force -Path $PROFILE | Out-Null }
if (-not (Select-String -Path $PROFILE -SimpleMatch 'passnotp completion' -Quiet)) {
    Add-Content -Path $PROFILE -Value $line
    Write-Host "==> Updated $PROFILE"
}

Write-Host ''
Write-Host '==> Done! Open a new terminal, then:'
Write-Host '    pass add       save a password'
Write-Host '    pass <name>    copy it'
Write-Host '    otp add        save a 2FA account (screenshot its QR code with Win+Shift+S first)'
Write-Host '    otp <name>     copy the current code'
