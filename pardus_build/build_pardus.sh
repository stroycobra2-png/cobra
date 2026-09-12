#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"
VERSION="1.0.0"
ARCH="amd64"
OUT="$ROOT/out"
rm -rf build dist "$OUT" AppDir debroot
mkdir -p "$OUT"

python -m PyInstaller --noconfirm --clean 12D_Dil_Programi_Pardus.spec
APPDIST="$ROOT/dist/12D_Dil_Programi"
test -x "$APPDIST/12D_Dil_Programi"

# ---------- .deb ----------
DEBROOT="$ROOT/debroot"
mkdir -p "$DEBROOT/DEBIAN" "$DEBROOT/opt/12d-dil-programi" "$DEBROOT/usr/bin" \
         "$DEBROOT/usr/share/applications" "$DEBROOT/usr/share/icons/hicolor/scalable/apps"
cp -a "$APPDIST/." "$DEBROOT/opt/12d-dil-programi/"
cat > "$DEBROOT/DEBIAN/control" <<EOF
Package: 12d-dil-programi
Version: $VERSION
Section: education
Priority: optional
Architecture: $ARCH
Maintainer: 12/D Dil Programı
Depends: libgl1, libegl1, libxkbcommon-x11-0, libxcb-cursor0, libxcb-xinerama0, libportaudio2, espeak-ng
Description: 12/D Dil Programı - A1-C2 İngilizce öğrenme uygulaması
 PySide6 tabanlı masaüstü İngilizce öğrenme uygulaması.
EOF
cat > "$DEBROOT/usr/bin/12d-dil-programi" <<'EOF'
#!/bin/sh
exec /opt/12d-dil-programi/12D_Dil_Programi "$@"
EOF
chmod 755 "$DEBROOT/usr/bin/12d-dil-programi"
cp packaging/12d-dil-programi.desktop "$DEBROOT/usr/share/applications/"
cp packaging/12d-dil-programi.svg "$DEBROOT/usr/share/icons/hicolor/scalable/apps/"
dpkg-deb --build --root-owner-group "$DEBROOT" "$OUT/12D_Dil_Programi_${VERSION}_pardus_amd64.deb"

# ---------- AppImage ----------
A="$ROOT/AppDir"
mkdir -p "$A/usr/lib/12d-dil-programi" "$A/usr/bin" "$A/usr/lib" "$A/usr/share"
cp -a "$APPDIST/." "$A/usr/lib/12d-dil-programi/"
cp packaging/12d-dil-programi.svg "$A/12d-dil-programi.svg"
cat > "$A/12d-dil-programi.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=12/D Dil Programı
Comment=A1-C2 İngilizce öğrenme uygulaması
Exec=12D_Dil_Programi
Icon=12d-dil-programi
Terminal=false
Categories=Education;Languages;
EOF

# Bundle espeak-ng binary/data and the most important audio runtime libs when present.
if command -v espeak-ng >/dev/null 2>&1; then cp -L "$(command -v espeak-ng)" "$A/usr/bin/espeak-ng"; fi
for D in /usr/lib/x86_64-linux-gnu/espeak-ng-data /usr/share/espeak-ng-data; do
  if [ -d "$D" ]; then cp -a "$D" "$A/usr/share/espeak-ng-data"; break; fi
done
for LIB in libportaudio.so.2 libespeak-ng.so.1 libpcaudio.so.0 libsonic.so.0; do
  P="$(ldconfig -p 2>/dev/null | awk -v n="$LIB" '$1==n {print $NF; exit}')"
  [ -n "${P:-}" ] && [ -f "$P" ] && cp -L "$P" "$A/usr/lib/" || true
done

cat > "$A/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="$HERE/usr/bin:$PATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:${LD_LIBRARY_PATH:-}"
if [ -d "$HERE/usr/share/espeak-ng-data" ]; then
  export ESPEAK_DATA_PATH="$HERE/usr/share/espeak-ng-data"
fi
exec "$HERE/usr/lib/12d-dil-programi/12D_Dil_Programi" "$@"
EOF
chmod 755 "$A/AppRun"
ln -sf usr/lib/12d-dil-programi/12D_Dil_Programi "$A/12D_Dil_Programi"

APPIMAGETOOL="$ROOT/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
  curl -L --fail --retry 3 -o "$APPIMAGETOOL" \
    https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
  chmod +x "$APPIMAGETOOL"
fi
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" "$A" "$OUT/12D_Dil_Programi_${VERSION}_Pardus_x86_64.AppImage"
chmod +x "$OUT/12D_Dil_Programi_${VERSION}_Pardus_x86_64.AppImage"

cat > "$OUT/OKU_BENI_PARDUS.txt" <<'EOF'
12/D Dil Programı - Pardus

DEB KURULUMU:
  sudo apt install ./12D_Dil_Programi_1.0.0_pardus_amd64.deb
Sonra uygulama menüsünden "12/D Dil Programı" açılır.

APPIMAGE (kurulumsuz):
  chmod +x 12D_Dil_Programi_1.0.0_Pardus_x86_64.AppImage
  ./12D_Dil_Programi_1.0.0_Pardus_x86_64.AppImage

Kullanıcı verileri:
  ~/.local/share/12d-dil-programi/fluentpath.db
EOF
sha256sum "$OUT"/*.deb "$OUT"/*.AppImage > "$OUT/SHA256SUMS.txt"
ls -lh "$OUT"
