"""
Dashboard Build Script (Alias)
Delegates directly to generate_minimal_dashboard.py to compile the minimalist AI leads matrix.
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    script_path = Path(__file__).parent / "generate_minimal_dashboard.py"
    if script_path.exists():
        sys.exit(subprocess.call([sys.executable, str(script_path)]))
    else:
        print(f"Error: {script_path} not found.")
        sys.exit(1)
