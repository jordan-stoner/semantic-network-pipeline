#!/usr/bin/env python3
"""
MLX Chat Initial Setup
Detects/installs conda and creates mlx-qwa environment with dependencies
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_conda():
    """Check if conda is available"""
    try:
        conda_path = shutil.which('conda')
        if not conda_path:
            return False
        subprocess.run([conda_path, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_miniconda():
    """Install Miniconda automatically"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'darwin':  # macOS
        if 'arm' in machine or 'aarch64' in machine:
            url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
        else:
            url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    elif system == 'linux':
        if 'aarch64' in machine or 'arm64' in machine:
            url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
        else:
            url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    else:
        print(f"❌ Unsupported system: {system}")
        return False
    
    print("📦 Installing Miniconda...")
    home = Path.home()
    installer_path = home / "miniconda_installer.sh"
    
    try:
        # Download installer
        import urllib.request
        urllib.request.urlretrieve(url, installer_path)
        
        # Run installer
        subprocess.run(['bash', str(installer_path), '-b', '-p', str(home / 'miniconda3')], check=True)
        
        # Initialize conda
        conda_path = home / 'miniconda3' / 'bin' / 'conda'
        subprocess.run([str(conda_path), 'init'], check=True)
        
        # Clean up
        installer_path.unlink()
        
        print("✅ Miniconda installed successfully")
        print("🔄 Please restart your terminal and run this script again")
        return False  # Need restart
        
    except Exception as e:
        print(f"❌ Failed to install Miniconda: {e}")
        return False

def check_environment():
    """Check if mlx-qwa environment exists"""
    try:
        conda_path = shutil.which('conda')
        if not conda_path:
            return False
        result = subprocess.run([conda_path, 'env', 'list'], capture_output=True, text=True, check=True)
        return 'mlx-qwa' in result.stdout
    except subprocess.CalledProcessError:
        return False

def create_environment():
    """Create mlx-qwa environment with Python 3.10"""
    print("🚀 Creating mlx-qwa environment...")
    try:
        conda_path = shutil.which('conda')
        if not conda_path:
            print("❌ Conda executable not found")
            return False
        subprocess.run([conda_path, 'create', '-n', 'mlx-qwa', 'python=3.10', '-y'], check=True)
        print("✅ Environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create environment: {e}")
        return False

def create_project_directories():
    """Create all required project directories"""
    base_path = Path(__file__).parent
    directories = [
        'model/training_data',
        'model/lora_training', 
        'model/lora',
        'model/adapters',
        'model/wordcloud',
        'model/model',
        'static/css',
        'static/js',
        'static/fonts',
        'templates'
    ]
    
    print("📁 Creating project directories...")
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")
    
    return True

def install_dependencies():
    """Install Python dependencies in mlx-qwa environment"""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("📦 Installing Python dependencies...")
    try:
        conda_path = shutil.which('conda')
        if not conda_path:
            print("❌ Conda executable not found")
            return False
        subprocess.run([conda_path, 'run', '-n', 'mlx-qwa', 'pip', 'install', '-r', str(requirements_file)], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    try:
        conda_path = shutil.which('conda')
        if not conda_path:
            print("⚠️ Conda not found, skipping NLTK download")
            return True
        subprocess.run([conda_path, 'run', '-n', 'mlx-qwa', 'python', '-c', 
                       "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng'); nltk.download('stopwords'); nltk.download('wordnet')"], 
                      check=True, capture_output=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ NLTK data download failed (will download automatically when needed)")
        return True  # Non-critical failure

def main():
    print("🌋 MLX Chat Initial Setup")
    print("=" * 40)
    print("This will create the mlx-qwa environment and all required directories")
    print()
    
    # Check if conda is available
    if not check_conda():
        print("⚠️ Conda not found")
        response = input("Install Miniconda automatically? (y/n): ").lower().strip()
        if response == 'y':
            if not install_miniconda():
                sys.exit(1)
        else:
            print("❌ Conda is required for MLX Chat")
            print("💡 Please install Anaconda or Miniconda manually")
            sys.exit(1)
    
    print("✅ Conda found")
    
    # Check if environment exists
    if check_environment():
        print("✅ mlx-qwa environment already exists")
    else:
        if not create_environment():
            sys.exit(1)
    
    # Create project directories
    if not create_project_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Download NLTK data
    download_nltk_data()
    
    print("\n🎉 Setup complete!")
    print("💡 To use MLX Chat:")
    print("   conda activate mlx-qwa")
    print("   python config_launcher.py")
    print("\n📝 Next steps:")
    print("   1. Download at least one MLX model to model/model/")
    print("   2. Add training data to model/training_data/ (optional)")
    print("   3. Run: python config_launcher.py")

if __name__ == '__main__':
    main()