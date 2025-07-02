import os
import subprocess
import sys
import shutil

venv_name = ".venv_312"

def check_python_version():
    if sys.version_info.major != 3 or sys.version_info.minor != 12:
        print("⚠️ This script must be run with Python 3.12.")
        print("🔁 Try running: py -3.12 setup_env.py")
        sys.exit(1)

def create_virtual_env():
    if os.path.isdir(venv_name):
        print(f"✅ Virtual environment '{venv_name}' already exists.")
    else:
        print(f"📦 Creating virtual environment '{venv_name}'...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_name])
        print("✅ Virtual environment created.")

def install_dependencies():
    pip_exe = os.path.join(venv_name, "Scripts", "pip.exe")
    print("📦 Installing packages: yfinance, pymongo")
    subprocess.check_call([pip_exe, "install", "yfinance", "pymongo"])

def print_instructions():
    activate_cmd = f"{venv_name}\\Scripts\\activate"
    print("\n✅ Setup complete.")
    print(f"👉 To activate the environment, run:")
    print(f"   {activate_cmd}")
    print("Then run your script as usual.")

if __name__ == "__main__":
    check_python_version()
    create_virtual_env()
    install_dependencies()
    print_instructions()
