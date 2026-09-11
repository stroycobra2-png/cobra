#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
IOS_HOME="$HOME/.12d_dil_programi_ios"
VENV="$IOS_HOME/venv"
TITLE="12DDilProgrami"
BUNDLE_ID="${BUNDLE_ID:-tr.okul.dilprogrami12d}"
DEPLOYMENT_TARGET="${DEPLOYMENT_TARGET:-13.0}"
PROJECT_DIR="$IOS_HOME/${TITLE}-ios"
LOG_FILE="$SCRIPT_DIR/ios_build.log"

on_error() {
  code=$?
  echo
  echo "=============================================="
  echo "[HATA] iOS proje olusturma durdu. Kod: $code"
  echo "Log: $LOG_FILE"
  echo "=============================================="
  exit "$code"
}
trap on_error ERR

exec > >(tee "$LOG_FILE") 2>&1

echo "=============================================="
echo "  12/D DIL PROGRAMI - iPHONE/iPAD BUILDER"
echo "=============================================="
echo "Uygulama : $APP_DIR"
echo "Bundle ID: $BUNDLE_ID"
echo "iOS min  : $DEPLOYMENT_TARGET"
echo

if [ "$(uname -s)" != "Darwin" ]; then
  echo "[HATA] iPhone/iPad projesi Apple geregi macOS + Xcode uzerinde olusturulur."
  exit 2
fi

if ! command -v xcodebuild >/dev/null 2>&1; then
  echo "[HATA] Xcode bulunamadi. App Store'dan Xcode'u kurup bir kez ac."
  exit 3
fi

echo "[1/7] Xcode kontrol ediliyor..."
xcodebuild -version
xcode-select -p

echo
echo "[2/7] Kivy-iOS onkosullari kontrol ediliyor..."
if command -v brew >/dev/null 2>&1; then
  brew install autoconf automake libtool pkg-config || true
  brew link libtool || true
else
  echo "[UYARI] Homebrew bulunamadi."
  echo "Kivy iOS icin autoconf, automake, libtool ve pkg-config kurulu olmali."
fi

PY=""
for p in python3.13 python3.12 python3.11 python3; do
  if command -v "$p" >/dev/null 2>&1; then
    PY="$p"
    break
  fi
done

if [ -z "$PY" ]; then
  echo "[HATA] Python 3 bulunamadi."
  exit 4
fi

mkdir -p "$IOS_HOME"

if [ -d "$VENV" ] && [ ! -x "$VENV/bin/python" ]; then
  rm -rf "$VENV"
fi

if [ ! -x "$VENV/bin/python" ]; then
  "$PY" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade "Cython==3.2.0" kivy-ios

export PATH="$VENV/bin:$PATH"

echo
echo "[3/7] Kivy iOS dagitimi derleniyor..."
toolchain build kivy

echo
echo "[4/7] Xcode projesi olusturuluyor..."
rm -rf "$PROJECT_DIR"
cd "$IOS_HOME"
toolchain create "$TITLE" "$APP_DIR"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "[HATA] Xcode proje klasoru olusmadi: $PROJECT_DIR"
  exit 5
fi

XCODEPROJ="$(find "$PROJECT_DIR" -maxdepth 3 -name '*.xcodeproj' -type d | head -n 1 || true)"
if [ -z "$XCODEPROJ" ]; then
  echo "[HATA] .xcodeproj bulunamadi."
  exit 6
fi

echo
echo "[5/7] iPhone/iPad izinleri ve bundle ayarlari uygulanıyor..."

PLIST="$(find "$PROJECT_DIR" -maxdepth 5 -name '*Info.plist' -type f | head -n 1 || true)"
if [ -n "$PLIST" ] && [ -x /usr/libexec/PlistBuddy ]; then
  plist_set() {
    key="$1"
    type="$2"
    value="$3"
    /usr/libexec/PlistBuddy -c "Add :$key $type $value" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :$key $value" "$PLIST"
  }

  plist_set "CFBundleDisplayName" "string" "12/D Dil Programi"
  plist_set "NSMicrophoneUsageDescription" "string" "Speaking pratiklerinde Ingilizce konusma ve dikte icin mikrofon kullanilir."
  plist_set "NSSpeechRecognitionUsageDescription" "string" "Speaking pratiklerinde konusmayi metne cevirmek icin konusma tanima kullanilabilir."
  plist_set "ITSAppUsesNonExemptEncryption" "bool" "false"
  plist_set "CFBundleDevelopmentRegion" "string" "tr"
  /usr/libexec/PlistBuddy -c "Delete :CFBundleLocalizations" "$PLIST" 2>/dev/null || true
  /usr/libexec/PlistBuddy -c "Add :CFBundleLocalizations array" "$PLIST"
  /usr/libexec/PlistBuddy -c "Add :CFBundleLocalizations:0 string tr" "$PLIST"
  /usr/libexec/PlistBuddy -c "Add :CFBundleLocalizations:1 string en" "$PLIST"
fi

PBXPROJ="$(find "$PROJECT_DIR" -maxdepth 4 -name 'project.pbxproj' -type f | head -n 1 || true)"
if [ -n "$PBXPROJ" ]; then
  # macOS BSD sed
  sed -i '' -E "s/PRODUCT_BUNDLE_IDENTIFIER = [^;]+;/PRODUCT_BUNDLE_IDENTIFIER = ${BUNDLE_ID};/g" "$PBXPROJ" || true
  sed -i '' -E "s/IPHONEOS_DEPLOYMENT_TARGET = [^;]+;/IPHONEOS_DEPLOYMENT_TARGET = ${DEPLOYMENT_TARGET};/g" "$PBXPROJ" || true
fi

echo
echo "[6/7] App Store / iPhone / iPad ikonlari ekleniyor..."
ASSET_CATALOG="$(find "$PROJECT_DIR" -type d -name 'Assets.xcassets' | head -n 1 || true)"
if [ -n "$ASSET_CATALOG" ]; then
  rm -rf "$ASSET_CATALOG/AppIcon.appiconset"
  cp -R "$SCRIPT_DIR/AppIcon.appiconset" "$ASSET_CATALOG/AppIcon.appiconset"
else
  echo "[UYARI] Assets.xcassets bulunamadi. Xcode'da App Icon elle secilebilir."
fi

echo
echo "[7/7] Xcode projesi dogrulaniyor..."
xcodebuild -project "$XCODEPROJ" -list

echo
echo "=============================================="
echo "  iPHONE / iPAD XCODE PROJESI HAZIR"
echo "=============================================="
echo "Proje: $XCODEPROJ"
echo
echo "Son adim:"
echo "1) Xcode acilacak."
echo "2) Signing & Capabilities > Team sec."
echo "3) Gercek iPhone/iPad'i sec."
echo "4) Run tusuna bas."
echo
echo "TestFlight/App Store icin Product > Archive kullan."
echo

open "$XCODEPROJ"
