"""Start the desktop application, independent of the current directory."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "gui"
    if mode in ("gui", "g", "--gui"):
        from src.gui_app import main as gui_main

        original = sys.argv
        sys.argv = [original[0], *original[2:]] if len(original) > 1 else original
        return gui_main()
    if mode in ("cli", "c", "--cli"):
        return subprocess.call([sys.executable, str(ROOT / "src" / "predict.py"), *sys.argv[2:]])
    print("Usage: python launch.py [gui | cli measurements.csv]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
