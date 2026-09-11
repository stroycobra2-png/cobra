#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_HOME="$HOME/.12d_android_builder"
WORK_DIR="$BUILD_HOME/project"
VENV_DIR="$BUILD_HOME/venv"
OUTPUT_DIR="$SOURCE_DIR/bin"
COMPAT_MARKER="$BUILD_HOME/.py314_p4a_develop_v403"

on_error() {
  code=$?
  echo
  echo "=============================================="
  echo "[HATA] Android derlemesi durdu. Cikis kodu: $code"
  echo "Yukaridaki EN SON hata satirlarini ChatGPT'ye gonderebilirsin."
  echo "=============================================="
  exit "$code"
}
trap on_error ERR

echo "=============================================="
echo "  12/D Dil Programi - Android APK Builder"
echo "  v4.0.3 Python 3.14 / p4a develop fix"
echo "=============================================="
echo "Kaynak proje : $SOURCE_DIR"
echo "Linux build  : $WORK_DIR"
echo

if ! command -v sudo >/dev/null 2>&1; then
  echo "[HATA] sudo bulunamadi."
  exit 11
fi

echo "[1/8] Ubuntu 26.04 build paketleri kuruluyor..."
sudo apt-get update

# Ubuntu surumleri arasinda ncurses paket isimleri degisebildigi icin
# ana paketleri once kurup ncurses uyumluluk paketlerini ayri deniyoruz.
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential git zip unzip curl rsync ca-certificates \
  openjdk-17-jdk \
  python3-pip python3-venv python3-dev python3-full python3-virtualenv \
  autoconf automake libtool pkg-config \
  zlib1g-dev cmake libffi-dev libssl-dev \
  autopoint gettext libtinfo6

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  libncurses-dev || true

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  libncurses5-dev libncursesw5-dev || true

echo
echo "[2/8] Rust toolchain kontrol ediliyor..."
if ! command -v cargo >/dev/null 2>&1; then
  echo "Rust bulunamadi; rustup ile kuruluyor..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi

if [ -f "$HOME/.cargo/env" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.cargo/env"
fi

cargo --version
rustc --version

echo
echo "[3/8] Linux build alani hazirlaniyor..."
mkdir -p "$BUILD_HOME" "$WORK_DIR" "$OUTPUT_DIR"

rsync -a --delete \
  --exclude '.buildvenv/' \
  --exclude '.buildozer/' \
  --exclude 'bin/' \
  --exclude '__pycache__/' \
  "$SOURCE_DIR/" "$WORK_DIR/"

echo "Kaynak proje Linux dosya sistemine kopyalandi."

echo
echo "[4/8] Python 3.14 Buildozer ortami hazirlaniyor..."

# Builder surumu degistigi icin eski venv'i bir kez temizle.
if [ ! -f "$COMPAT_MARKER" ]; then
  echo "Yeni Python 3.14/p4a-develop profili uygulanacak; eski build venv temizleniyor..."
  rm -rf "$VENV_DIR"
fi

if [ -d "$VENV_DIR" ] && [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Yarim kalmis venv bulundu; temizleniyor..."
  rm -rf "$VENV_DIR"
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  python3 -m venv "$VENV_DIR"
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "[HATA] Python venv olusturulamadi: $VENV_DIR"
  exit 30
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip wheel

# Ubuntu 26.04 / Python 3.14 icin guncel Buildozer master + resmi uyumluluklar.
python -m pip install --upgrade \
  "git+https://github.com/kivy/buildozer.git" \
  legacy-cgi setuptools "cython==0.29.34" virtualenv

touch "$COMPAT_MARKER"

echo
echo "[5/8] Java 17 ve Linux PATH sabitleniyor..."

JAVAC_REAL="$(readlink -f "$(command -v javac)")"
export JAVA_HOME="$(dirname "$(dirname "$JAVAC_REAL")")"

# WSL, Windows PATH'ini Linux PATH'ine ekleyebiliyor. Logda Java 8 dahil
# Windows yollarinin gorunmesi bu nedenleydi. Android build sirasinda yalnizca
# Linux araclarini ve OpenJDK 17'yi kullan.
export PATH="$VENV_DIR/bin:$HOME/.cargo/bin:$JAVA_HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

hash -r

echo "Python : $(python --version 2>&1)"
echo "Pip    : $(python -m pip --version)"
echo "Java   :"
java -version
echo "Javac  : $(javac -version 2>&1)"
echo "JAVA_HOME=$JAVA_HOME"
echo "Rust   : $(rustc --version)"
echo "Cargo  : $(cargo --version)"
echo "Buildozer:"
buildozer --version

if ! python --version 2>&1 | grep -Eq 'Python 3\.(1[0-9]|[2-9][0-9])'; then
  echo "[HATA] Desteklenen Python 3.10+ bulunamadi."
  exit 31
fi

echo
echo "[6/8] Eski p4a master cache'i temizleniyor..."

cd "$WORK_DIR"

# Onceki derleme p4a master ile baslamisti. Branch degistirmek tek basina yeterli
# degil; proje cache'indeki eski checkout/dist yeni ayarlari ezebilir.
rm -rf \
  "$WORK_DIR/.buildozer/android/platform/python-for-android" \
  "$WORK_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a" \
  "$WORK_DIR/.buildozer/android/platform/build-arm64-v8a" \
  "$WORK_DIR/.buildozer/android/platform/build-armeabi-v7a"

echo "buildozer.spec Android ayarlari:"
grep -E '^(android\.api|android\.ndk|android\.minapi|android\.archs|p4a\.branch|requirements)' buildozer.spec || true

if ! grep -Eq '^p4a\.branch[[:space:]]*=[[:space:]]*develop' buildozer.spec; then
  echo "[HATA] buildozer.spec icinde p4a.branch = develop bulunamadi."
  exit 32
fi

if ! grep -Eq '^android\.api[[:space:]]*=[[:space:]]*36' buildozer.spec; then
  echo "[HATA] buildozer.spec Android API 36 degil."
  exit 33
fi

echo
echo "[7/8] Android debug APK derleniyor..."
echo "Ilk calistirmada p4a develop / SDK / NDK indirmeleri uzun surebilir."
echo

buildozer -v android debug

echo
echo "[8/8] APK Windows proje klasorune kopyalaniyor..."
mkdir -p "$OUTPUT_DIR"

APK_FILES=()
while IFS= read -r -d '' apk; do
  APK_FILES+=("$apk")
done < <(find "$WORK_DIR/bin" -maxdepth 1 -type f -name "*.apk" -print0 2>/dev/null)

if [ "${#APK_FILES[@]}" -lt 1 ]; then
  echo "[HATA] Buildozer tamamlandi ancak APK bulunamadi."
  exit 40
fi

for apk in "${APK_FILES[@]}"; do
  cp -f "$apk" "$OUTPUT_DIR/"
done

echo
echo "=============================================="
echo "  APK HAZIR"
echo "=============================================="
echo "Windows klasoru:"
echo "$OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.apk" -print
echo
