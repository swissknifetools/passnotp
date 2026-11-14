#!/bin/sh
# Build release archives for every platform into dist/.
# Usage: scripts/dist.sh [version]
set -eu
cd "$(dirname "$0")/.."

version="${1:-dev}"
rm -rf dist build
mkdir -p dist

for target in linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64; do
    os=${target%/*}
    arch=${target#*/}
    name="passnotp_${os}_${arch}"
    exe=passnotp
    [ "$os" = windows ] && exe=passnotp.exe

    mkdir -p "build/$name"
    CGO_ENABLED=0 GOOS=$os GOARCH=$arch go build -trimpath \
        -ldflags "-s -w -X github.com/swissknifetools/passnotp/internal/cli.Version=$version" \
        -o "build/$name/$exe" ./cmd/passnotp

    if [ "$os" = windows ]; then
        (cd "build/$name" && zip -q "../../dist/$name.zip" "$exe")
    else
        tar -C "build/$name" -czf "dist/$name.tar.gz" "$exe"
    fi
done

(cd dist && sha256sum -- * > checksums.txt)
rm -rf build
ls dist
