#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_HOME="$HOME/.12d_mobile_v501_android"
WORK_DIR="$BUILD_HOME/project"
VENV_DIR="$BUILD_HOME/venv"
OUTPUT_DIR="$SOURCE_DIR/bin"
LOG_FILE="$SOURCE_DIR/android_build.log"

on_error() {
  code=$?
  echo
  echo "=============================================="
  echo "[HATA] Android build durdu. Kod: $code"
  echo "Tam log: $LOG_FILE"
  echo "Son 100 satir:"
  echo "----------------------------------------------"
  tail -n 100 "$LOG_FILE" 2>/dev/null || true
  echo "=============================================="
  exit "$code"
}
trap on_error ERR

# Save a complete log while still showing output on screen.
exec > >(tee "$LOG_FILE") 2>&1

echo "=============================================="
echo "  12/D Universal Mobile - Android Builder"
echo "  v5.0.1 CLEAN ARM64 / P4A DEVELOP"
echo "=============================================="
echo "Kaynak : $SOURCE_DIR"
echo "Build  : $WORK_DIR"
echo

if ! command -v sudo >/dev/null 2>&1; then
  echo "[HATA] sudo bulunamadi. Ubuntu/WSL kurulumu tamamlanmamis olabilir."
  exit 10
fi

echo "[1/9] Ubuntu build paketleri kontrol ediliyor..."
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential git zip unzip curl rsync ca-certificates \
  openjdk-17-jdk \
  python3-pip python3-venv python3-dev python3-full python3-virtualenv \
  autoconf automake libtool pkg-config zlib1g-dev \
  libncurses-dev libtinfo6 cmake libffi-dev libssl-dev \
  autopoint gettext

echo
echo "[2/9] Rust kontrol ediliyor..."
if ! command -v cargo >/dev/null 2>&1; then
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi
[ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"
rustc --version
cargo --version

echo
echo "[3/9] Temiz Linux build alani hazirlaniyor..."
mkdir -p "$BUILD_HOME" "$WORK_DIR" "$OUTPUT_DIR"
rsync -a --delete \
  --exclude '.buildozer/' \
  --exclude 'bin/' \
  --exclude '__pycache__/' \
  --exclude 'android_build.log' \
  "$SOURCE_DIR/" "$WORK_DIR/"

echo
echo "[4/9] Python 3.14 build venv hazirlaniyor..."
PYTHON_BIN="$(command -v python3.14 || true)"
if [ -z "$PYTHON_BIN" ]; then
  # Ubuntu 26.04 default python3 is currently 3.14; accept only if it really is 3.14.
  if python3 -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3,14) else 1)'; then
    PYTHON_BIN="$(command -v python3)"
  else
    echo "[HATA] Python 3.14 bulunamadi. Ubuntu 26.04/Python 3.14 builder gerekiyor."
    python3 --version || true
    exit 20
  fi
fi

if [ -d "$VENV_DIR" ] && [ ! -x "$VENV_DIR/bin/python" ]; then
  rm -rf "$VENV_DIR"
fi
if [ ! -x "$VENV_DIR/bin/python" ]; then
  rm -rf "$VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip wheel
python -m pip install --upgrade \
  "git+https://github.com/kivy/buildozer.git" \
  legacy-cgi setuptools "cython==0.29.34" virtualenv

echo
echo "[5/9] Linux OpenJDK 17 PATH sabitleniyor..."
JAVAC_REAL="$(readlink -f "$(command -v javac)")"
export JAVA_HOME="$(dirname "$(dirname "$JAVAC_REAL")")"
export PATH="$VENV_DIR/bin:$HOME/.cargo/bin:$JAVA_HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
hash -r
python --version
java -version
javac -version
buildozer --version

echo
echo "[6/9] Spec dogrulaniyor..."
cd "$WORK_DIR"
grep -E '^(requirements|android\.api|android\.minapi|android\.ndk|android\.archs|p4a\.branch)' buildozer.spec

# Guard against ever launching the obsolete builder configuration again.
if grep -Eq '^requirements[[:space:]]*=.*plyer' buildozer.spec; then
  echo "[HATA] Eski builder tespit edildi: requirements icinde plyer var."
  exit 30
fi
if ! grep -Eq '^android\.archs[[:space:]]*=[[:space:]]*arm64-v8a[[:space:]]*$' buildozer.spec; then
  echo "[HATA] Builder sadece arm64-v8a olmali."
  exit 31
fi
if ! grep -Eq '^p4a\.branch[[:space:]]*=[[:space:]]*develop' buildozer.spec; then
  echo "[HATA] p4a.branch = develop bulunamadi."
  exit 32
fi
if ! grep -Eq '^android\.api[[:space:]]*=[[:space:]]*36' buildozer.spec; then
  echo "[HATA] android.api = 36 bulunamadi."
  exit 33
fi
if ! grep -Eq '^android\.ndk[[:space:]]*=[[:space:]]*29' buildozer.spec; then
  echo "[HATA] android.ndk = 29 bulunamadi."
  exit 34
fi
if ! grep -Eq '^android\.minapi[[:space:]]*=[[:space:]]*24' buildozer.spec; then
  echo "[HATA] android.minapi = 24 bulunamadi."
  exit 35
fi

echo
echo "[7/9] Bu surume ait p4a/build cache temizleniyor..."
# This build-home is unique to v5.0.1, so it cannot reuse the broken old dist.
rm -rf \
  "$WORK_DIR/.buildozer/android/platform/python-for-android" \
  "$WORK_DIR/.buildozer/android/platform/build-arm64-v8a" \
  "$WORK_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a"

echo
echo "[8/9] Android ARM64 debug APK derleniyor..."
echo "Ilk calistirmada SDK/NDK/p4a indirmeleri uzun surebilir."
buildozer -v android debug

echo
echo "[9/9] APK Windows klasorune kopyalaniyor..."
mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR"/*.apk 2>/dev/null || true

mapfile -d '' APK_FILES < <(find "$WORK_DIR/bin" -maxdepth 1 -type f -name '*.apk' -print0 2>/dev/null)
if [ "${#APK_FILES[@]}" -lt 1 ]; then
  echo "[HATA] Buildozer tamamlandi ancak APK bulunamadi."
  exit 40
fi
for apk in "${APK_FILES[@]}"; do
  cp -f "$apk" "$OUTPUT_DIR/"
done

echo
echo "=============================================="
echo " APK HAZIR"
echo "=============================================="
find "$OUTPUT_DIR" -maxdepth 1 -type f -name '*.apk' -print
