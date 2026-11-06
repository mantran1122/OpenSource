#!/usr/bin/env bash
# LinTask Manager - Debian Package (.deb) Builder
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION="${1:-0.1.0}"
ARCH="all"
PKG_NAME="lintask-manager"
BUILD_ROOT="$SCRIPT_DIR/build/deb"
STAGE_DIR="$BUILD_ROOT/${PKG_NAME}_${VERSION}_${ARCH}"
DIST_DIR="$SCRIPT_DIR/dist"
OUTPUT_DEB="$DIST_DIR/${PKG_NAME}_${VERSION}_${ARCH}.deb"

echo "=== Building Debian Package (.deb) for LinTask Manager v${VERSION} ==="

# Check requirements
if ! command -v dpkg-deb &> /dev/null; then
    echo "Error: dpkg-deb is not installed. Please install dpkg on your system."
    exit 1
fi

# Clean previous build
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/DEBIAN"
mkdir -p "$STAGE_DIR/usr/bin"
mkdir -p "$STAGE_DIR/usr/share/lintask"
mkdir -p "$STAGE_DIR/usr/share/applications"
mkdir -p "$STAGE_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$DIST_DIR"

# 1. Copy Application Sources
echo "-> Copying application files..."
cp -r lintask "$STAGE_DIR/usr/share/lintask/"
cp -r assets "$STAGE_DIR/usr/share/lintask/"
cp run.py "$STAGE_DIR/usr/share/lintask/"
cp requirements.txt "$STAGE_DIR/usr/share/lintask/"
chmod +x "$STAGE_DIR/usr/share/lintask/run.py"

# Clean any pycache in stage
find "$STAGE_DIR/usr/share/lintask" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 2. Launcher Binary (/usr/bin/lintask)
echo "-> Creating /usr/bin/lintask executable..."
cat << "EOF" > "$STAGE_DIR/usr/bin/lintask"
#!/bin/bash
exec /usr/bin/python3 /usr/share/lintask/run.py "$@"
EOF
chmod 755 "$STAGE_DIR/usr/bin/lintask"

# 3. Desktop Entry (/usr/share/applications/lintask.desktop)
echo "-> Creating desktop launcher..."
cat << "EOF" > "$STAGE_DIR/usr/share/applications/lintask.desktop"
[Desktop Entry]
Type=Application
Name=LinTask Manager
GenericName=Task Manager
Comment=Modern Windows-style Task Manager for Linux
Exec=lintask
Icon=lintask
Terminal=false
Categories=System;Monitor;
Keywords=task;manager;system;process;performance;monitor;
StartupNotify=true
EOF
chmod 644 "$STAGE_DIR/usr/share/applications/lintask.desktop"

# 4. Icon (/usr/share/icons/hicolor/scalable/apps/lintask.svg)
echo "-> Copying scalable icon..."
cp assets/icons/lintask.svg "$STAGE_DIR/usr/share/icons/hicolor/scalable/apps/lintask.svg"
chmod 644 "$STAGE_DIR/usr/share/icons/hicolor/scalable/apps/lintask.svg"

# 5. Debian Control File
echo "-> Generating DEBIAN/control..."
cat << EOF > "$STAGE_DIR/DEBIAN/control"
Package: ${PKG_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-pip, python3-venv
Maintainer: ManTran <mantran@users.noreply.github.com>
Homepage: https://github.com/mantran1122/OpenSource
Description: Modern Windows 11 Fluent-style Task Manager for Linux
 LinTask Manager is a modern, intuitive system monitor and task manager
 built with Python 3, PyQt6, and QFluentWidgets. Features real-time 60 FPS
 performance sparklines, numeric process sorting, heatmap load highlighting,
 startup app manager, and systemd service controls.
EOF

# 6. Debian Post-Install Script
echo "-> Generating DEBIAN/postinst..."
cat << "EOF" > "$STAGE_DIR/DEBIAN/postinst"
#!/bin/bash
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "$STAGE_DIR/DEBIAN/postinst"

# 7. Debian Post-Remove Script
echo "-> Generating DEBIAN/postrm..."
cat << "EOF" > "$STAGE_DIR/DEBIAN/postrm"
#!/bin/bash
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
    fi
fi
exit 0
EOF
chmod 755 "$STAGE_DIR/DEBIAN/postrm"

# 8. Build Debian Package
echo "-> Building .deb package with dpkg-deb..."
dpkg-deb --build --root-owner-group "$STAGE_DIR" "$OUTPUT_DEB"

echo ""
echo "=== Build Successful! ==="
echo "Debian package created at:"
echo "    $OUTPUT_DEB"
echo ""
echo "To test installation on your system, run:"
echo "    sudo dpkg -i $OUTPUT_DEB"
echo "    # or: sudo apt install ./$OUTPUT_DEB"
