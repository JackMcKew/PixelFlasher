#!/usr/bin/env bash
#rm -rf build dist
VERSION=2.2.0
NAME="PixelFlasher"
DIST_NAME="PixelFlasher"

if [[ $OSTYPE == 'darwin'* ]]; then
    echo "Building for MacOS"
    specfile=build-on-mac.spec
else
    echo "Building for Linux"
    specfile=build-on-linux.spec
fi

pyinstaller --log-level=DEBUG \
            --noconfirm \
            --windowed \
            $specfile

if [[ $OSTYPE == 'darwin'* ]]; then
    # https://github.com/sindresorhus/create-dmg
    create-dmg "dist/$NAME.app"
    mv "$NAME $VERSION.dmg" "dist/$DIST_NAME.dmg"
fi
