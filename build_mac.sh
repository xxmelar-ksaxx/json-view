#!/bin/bash
echo "============================================"
echo "  Building JSON View for macOS"
echo "============================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install pyinstaller Pillow

# Create icon files
echo ""
echo "Creating icon files..."
python3 create_icon.py

# Create .icns from iconset (macOS only)
if command -v iconutil &> /dev/null; then
    echo "Creating .icns file..."
    iconutil -c icns icon.iconset
    ICON_FLAG="--icon icon.icns"
else
    echo "Warning: iconutil not found, building without custom icon"
    ICON_FLAG=""
fi

# Build with PyInstaller
echo ""
echo "Building application..."
pyinstaller --onefile \
    --windowed \
    --name "JSON View" \
    $ICON_FLAG \
    --add-data "icon.png:." \
    --target-architecture universal2 \
    json_view.py

echo ""
echo "============================================"
echo "  Build complete!"
echo "  Output: dist/JSON View"
echo "============================================"
