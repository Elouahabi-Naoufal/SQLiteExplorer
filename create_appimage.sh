#!/bin/bash

# Create AppImage for SQLite Manager
set -e

APP_NAME="SQLite-Manager"
APP_VERSION="1.0.0"
ARCH="x86_64"

# Clean previous builds
rm -rf build/ dist/ venv_appimage/ ${APP_NAME}.AppDir/ *.AppImage

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv_appimage
source venv_appimage/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt pyinstaller

# Create PyInstaller spec
cat > sqlite_manager.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources'), ('ui', 'ui'), ('db', 'db'), ('utils', 'utils')],
    hiddenimports=['PyQt6.QtPrintSupport'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SQLiteManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
EOF

# Build executable
echo "🔨 Building executable..."
pyinstaller sqlite_manager.spec

# Create AppDir structure
APPDIR="${APP_NAME}.AppDir"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy executable
cp dist/SQLiteManager "$APPDIR/usr/bin/"
chmod +x "$APPDIR/usr/bin/SQLiteManager"

# Create desktop file
cat > "$APPDIR/sqlite-manager.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=SQLite Manager
Comment=Professional SQLite Database Management Tool
Exec=SQLiteManager
Icon=sqlite-manager
Categories=Development;Database;
Keywords=sqlite;database;sql;manager;gui;
StartupNotify=true
MimeType=application/x-sqlite3;application/vnd.sqlite3;
EOF

# Copy desktop file
cp "$APPDIR/sqlite-manager.desktop" "$APPDIR/usr/share/applications/"

# Create AppRun
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/SQLiteManager" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Copy icon
cp resources/sqlite_manager.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/sqlite-manager.png"
cp resources/sqlite_manager.png "$APPDIR/sqlite-manager.png"

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppImage
ARCH=$ARCH ./appimagetool-x86_64.AppImage "$APPDIR" "${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"

# Make executable
chmod +x "${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"

echo "✅ AppImage created: ${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"

# Cleanup
deactivate
rm -rf venv_appimage/ build/ dist/ ${APP_NAME}.AppDir/