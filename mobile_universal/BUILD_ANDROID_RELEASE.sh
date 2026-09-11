#!/usr/bin/env bash
set -Eeuo pipefail
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_HOME="$HOME/.12d_mobile_v501_android"
WORK_DIR="$BUILD_HOME/project"
VENV_DIR="$BUILD_HOME/venv"
if [ ! -x "$VENV_DIR/bin/buildozer" ]; then
  echo "[HATA] Once debug APK builder'i en az bir kez calistir: ANDROID_APK_OLUSTUR.bat"
  exit 1
fi
source "$VENV_DIR/bin/activate"
JAVAC_REAL="$(readlink -f "$(command -v javac)")"
export JAVA_HOME="$(dirname "$(dirname "$JAVAC_REAL")")"
export PATH="$VENV_DIR/bin:$HOME/.cargo/bin:$JAVA_HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd "$WORK_DIR"
grep -E '^android\.archs[[:space:]]*=[[:space:]]*arm64-v8a[[:space:]]*$' buildozer.spec >/dev/null
buildozer -v android release
