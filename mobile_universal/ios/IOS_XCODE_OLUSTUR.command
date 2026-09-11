#!/bin/bash
set -e
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$HERE"
chmod +x BUILD_IOS_XCODE.sh
./BUILD_IOS_XCODE.sh
echo
echo "Bu pencereyi kapatmak icin Enter'a bas."
read -r
