#!/usr/bin/env python3
"""
Convert the app icon PNG to ICO format for Windows.
Also creates an ICNS file for macOS.
Requires: Pillow (pip install Pillow)
"""

from PIL import Image
import os
import struct
import sys


def create_ico(png_path, ico_path):
    """Create a Windows .ico file from a PNG image."""
    img = Image.open(png_path).convert("RGBA")

    # Create multiple sizes for the ICO
    sizes = [256, 128, 64, 48, 32, 24, 16]
    icons = []
    for size in sizes:
        resized = img.resize((size, size), Image.LANCZOS)
        icons.append(resized)

    # Save as ICO with all sizes
    img.save(ico_path, format='ICO',
             sizes=[(s, s) for s in sizes])
    print(f"Created: {ico_path} (sizes: {sizes})")


def create_iconset_for_mac(png_path, output_dir):
    """Create PNG files needed for macOS .icns generation."""
    img = Image.open(png_path).convert("RGBA")

    iconset_dir = os.path.join(output_dir, "icon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    # macOS icon sizes
    sizes = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }

    for name, size in sizes.items():
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(iconset_dir, name))

    print(f"Created iconset at: {iconset_dir}")
    print("To create .icns on macOS, run:")
    print(f"  iconutil -c icns {iconset_dir}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(script_dir, "icon.png")

    if not os.path.exists(png_path):
        print(f"ERROR: icon.png not found at {png_path}")
        print("Please place your icon.png in the same directory as this script.")
        sys.exit(1)

    # Create ICO for Windows
    ico_path = os.path.join(script_dir, "icon.ico")
    create_ico(png_path, ico_path)

    # Create iconset for macOS
    create_iconset_for_mac(png_path, script_dir)

    print("\nDone! Icon files created successfully.")
