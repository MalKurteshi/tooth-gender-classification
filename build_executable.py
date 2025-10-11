#!/usr/bin/env python3
"""
Tooth Gender Classification - Executable Builder
Creates standalone executables for Windows, macOS, and Linux using PyInstaller

Usage:
    python build_executable.py [--gui] [--cli] [--all]
    
Arguments:
    --gui: Build GUI application only
    --cli: Build CLI application only  
    --all: Build both GUI and CLI (default)
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} is available")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_spec_file(app_type="gui"):
    """Create PyInstaller spec file"""
    
    if app_type == "gui":
        script_name = "gui_app.py"
        exe_name = "ToothGenderClassification"
        console = False
    else:
        script_name = "predict_working.py"
        exe_name = "ToothGenderClassification-CLI"
        console = True
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect data files
datas = []

# Add model files if they exist
if os.path.exists('models'):
    datas.append(('models', 'models'))

# Add any data files
if os.path.exists('data'):
    datas.append(('data', 'data'))

# Add assets if they exist
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

# Collect sklearn, xgboost, lightgbm hidden imports
hiddenimports = []
hiddenimports += collect_submodules('sklearn')
hiddenimports += collect_submodules('xgboost')
hiddenimports += collect_submodules('lightgbm')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('matplotlib')
hiddenimports += collect_submodules('seaborn')
hiddenimports += collect_submodules('joblib')
hiddenimports += collect_submodules('openpyxl')

# Additional hidden imports
hiddenimports += [
    'sklearn.utils._cython_blas',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.skiplist',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.scrolledtext',
]

a = Analysis(
    ['src/{script_name}'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(console).lower()},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For macOS, create app bundle
import platform
if platform.system() == 'Darwin' and not {str(console).lower()}:
    app = BUNDLE(
        exe,
        name='{exe_name}.app',
        icon=None,
        bundle_identifier='com.toothgender.classification',
        info_plist={{
            'CFBundleName': 'Tooth Gender Classification',
            'CFBundleDisplayName': 'Tooth Gender Classification',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': 'True',
            'NSAppleScriptEnabled': 'True',
        }},
    )
'''
    
    spec_filename = f"{exe_name.lower().replace('-', '_')}.spec"
    
    with open(spec_filename, 'w') as f:
        f.write(spec_content)
    
    return spec_filename

def build_executable(app_type="gui"):
    """Build executable using PyInstaller"""
    
    print(f"\n📦 Building {app_type.upper()} executable...")
    
    # Create spec file
    spec_file = create_spec_file(app_type)
    print(f"✅ Created spec file: {spec_file}")
    
    # Build command
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        spec_file
    ]
    
    print(f"🔨 Running: {' '.join(build_cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Show output location
        dist_dir = Path("dist")
        if dist_dir.exists():
            executables = list(dist_dir.glob("*"))
            if executables:
                print(f"📁 Executable(s) created in: {dist_dir.absolute()}")
                for exe in executables:
                    print(f"   - {exe.name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    
    finally:
        # Clean up spec file
        if os.path.exists(spec_file):
            os.remove(spec_file)

def create_installer_scripts():
    """Create installer scripts for different platforms"""
    
    system = platform.system().lower()
    
    if system == "windows":
        create_windows_installer()
    elif system == "darwin":  # macOS
        create_macos_installer()
    else:  # Linux
        create_linux_installer()

def create_windows_installer():
    """Create Windows installer script"""
    
    installer_script = """
@echo off
echo Installing Tooth Gender Classification...

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\\ToothGenderClassification
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "dist\\ToothGenderClassification.exe" "%INSTALL_DIR%\\"
copy "dist\\ToothGenderClassification-CLI.exe" "%INSTALL_DIR%\\"

REM Create desktop shortcut (optional)
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\\Desktop
echo @echo off > "%DESKTOP%\\Tooth Gender Classification.bat"
echo cd /d "%INSTALL_DIR%" >> "%DESKTOP%\\Tooth Gender Classification.bat"
echo ToothGenderClassification.exe >> "%DESKTOP%\\Tooth Gender Classification.bat"

echo Installation complete!
echo You can find the application at: %INSTALL_DIR%
pause
"""
    
    with open("install_windows.bat", "w") as f:
        f.write(installer_script)
    
    print("✅ Created Windows installer: install_windows.bat")

def create_macos_installer():
    """Create macOS installer script"""
    
    installer_script = """#!/bin/bash
echo "Installing Tooth Gender Classification for macOS..."

# Create Applications directory entry
INSTALL_DIR="/Applications"
APP_NAME="ToothGenderClassification.app"

if [ -d "dist/$APP_NAME" ]; then
    echo "Copying app to Applications folder..."
    cp -R "dist/$APP_NAME" "$INSTALL_DIR/"
    
    echo "Setting permissions..."
    chmod -R 755 "$INSTALL_DIR/$APP_NAME"
    
    echo "✅ Installation complete!"
    echo "The application has been installed to $INSTALL_DIR/$APP_NAME"
    echo "You can find it in your Applications folder or Launchpad."
else
    echo "❌ App bundle not found in dist/ directory"
    exit 1
fi
"""
    
    with open("install_macos.sh", "w") as f:
        f.write(installer_script)
    
    os.chmod("install_macos.sh", 0o755)
    print("✅ Created macOS installer: install_macos.sh")

def create_linux_installer():
    """Create Linux installer script"""
    
    installer_script = """#!/bin/bash
echo "Installing Tooth Gender Classification for Linux..."

# Create installation directory
INSTALL_DIR="$HOME/.local/share/ToothGenderClassification"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Copy executables
if [ -f "dist/ToothGenderClassification" ]; then
    cp "dist/ToothGenderClassification" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/ToothGenderClassification"
    
    # Create symlink in bin directory
    ln -sf "$INSTALL_DIR/ToothGenderClassification" "$BIN_DIR/tooth-gender-gui"
fi

if [ -f "dist/ToothGenderClassification-CLI" ]; then
    cp "dist/ToothGenderClassification-CLI" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/ToothGenderClassification-CLI"
    
    # Create symlink in bin directory  
    ln -sf "$INSTALL_DIR/ToothGenderClassification-CLI" "$BIN_DIR/tooth-gender-cli"
fi

# Create desktop entry
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/tooth-gender-classification.desktop" << EOF
[Desktop Entry]
Name=Tooth Gender Classification
Comment=Dental measurement analysis for gender classification
Exec=$INSTALL_DIR/ToothGenderClassification
Icon=accessories-calculator
Terminal=false
Type=Application
Categories=Science;Education;
EOF

echo "✅ Installation complete!"
echo "GUI Application: $INSTALL_DIR/ToothGenderClassification"
echo "CLI Application: $INSTALL_DIR/ToothGenderClassification-CLI"
echo "You can also run: tooth-gender-gui or tooth-gender-cli from terminal"
"""
    
    with open("install_linux.sh", "w") as f:
        f.write(installer_script)
    
    os.chmod("install_linux.sh", 0o755)
    print("✅ Created Linux installer: install_linux.sh")

def main():
    parser = argparse.ArgumentParser(description="Build standalone executables")
    parser.add_argument("--gui", action="store_true", help="Build GUI application only")
    parser.add_argument("--cli", action="store_true", help="Build CLI application only")
    parser.add_argument("--all", action="store_true", help="Build both applications (default)")
    parser.add_argument("--no-installer", action="store_true", help="Skip creating installer scripts")
    
    args = parser.parse_args()
    
    # Default to building all if no specific option given
    if not (args.gui or args.cli):
        args.all = True
    
    print("🏗️  Tooth Gender Classification - Executable Builder")
    print(f"Platform: {platform.system()} {platform.release()}")
    print("=" * 50)
    
    # Check if running from correct directory
    if not os.path.exists('src'):
        print("❌ ERROR: Please run this script from the tooth-gender-classification root directory")
        return 1
    
    # Check PyInstaller
    if not check_pyinstaller():
        return 1
    
    success = True
    
    # Build GUI application
    if args.gui or args.all:
        if not build_executable("gui"):
            success = False
    
    # Build CLI application
    if args.cli or args.all:
        if not build_executable("cli"):
            success = False
    
    # Create installer scripts
    if success and not args.no_installer:
        print("\n📦 Creating installer scripts...")
        create_installer_scripts()
    
    if success:
        print("\n✅ All builds completed successfully!")
        print("\nNext steps:")
        print("1. Test the executables in the 'dist/' directory")
        print("2. Use the installer scripts to install on target systems")
        print("3. Distribute the executables to end users")
    else:
        print("\n❌ Some builds failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())