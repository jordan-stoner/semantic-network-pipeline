#!/usr/bin/env python3
"""
MLX Model Downloader
Downloads recommended MLX models for chat and resume analysis
"""

import subprocess
import sys
from pathlib import Path

# MLX-compatible models from mlx-community
MODELS = {
    "1": {
        "name": "Llama-3-8B-Instruct (MLX 4-bit)",
        "description": "General purpose chat model, excellent for resumes and professional writing",
        "size": "~4.5GB",
        "repo": "mlx-community/Meta-Llama-3-8B-Instruct-4bit",
        "folder": "Llama-3-8B-MLX"
    },
    "2": {
        "name": "Deepseek-Coder-1.3B (MLX 4-bit)",
        "description": "Lightweight coding model, perfect for technical resumes",
        "size": "~800MB",
        "repo": "mlx-community/deepseek-coder-1.3b-instruct-4bit",
        "folder": "Deepseek-Coder-1.3B-MLX"
    },
    "3": {
        "name": "Mistral-7B-Instruct (MLX 4-bit)",
        "description": "Balanced model for professional writing and analysis",
        "size": "~4GB",
        "repo": "mlx-community/Mistral-7B-Instruct-v0.1-4bit",
        "folder": "Mistral-7B-MLX"
    },
    "4": {
        "name": "Qwen2.5-Coder-1.5B (MLX 4-bit)",
        "description": "Code-focused model, excellent for technical documents and resumes",
        "size": "~900MB",
        "repo": "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit",
        "folder": "Qwen2.5-Coder-1.5B-MLX"
    },
    "5": {
        "name": "Phi-3-Mini-4K (MLX 4-bit)",
        "description": "Microsoft's efficient model for text analysis and writing",
        "size": "~2.3GB",
        "repo": "mlx-community/Phi-3-mini-4k-instruct-4bit",
        "folder": "Phi-3-Mini-MLX"
    }
}

def check_huggingface_cli():
    """Check if huggingface-cli is available"""
    try:
        subprocess.run(['huggingface-cli', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_model(model_info):
    """Download a model using huggingface-cli"""
    repo = model_info["repo"]
    folder = model_info["folder"]
    
    print(f"\n📦 Downloading {model_info['name']}...")
    print(f"Size: {model_info['size']}")
    print(f"This may take several minutes...\n")
    
    try:
        cmd = ['huggingface-cli', 'download', repo, '--local-dir', f'./{folder}']
        subprocess.run(cmd, check=True)
        print(f"✅ {model_info['name']} downloaded successfully to {folder}/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download {model_info['name']}: {e}")
        return False

def list_existing_models():
    """List already downloaded models"""
    current_dir = Path('.')
    models = [d for d in current_dir.iterdir() if d.is_dir() and d.name != '__pycache__']
    
    if models:
        print("📁 Already downloaded models:")
        for model in models:
            size = sum(f.stat().st_size for f in model.rglob('*') if f.is_file()) / (1024**3)
            print(f"   • {model.name} ({size:.1f}GB)")
    else:
        print("📁 No models found in this directory")

def main():
    print("🌋 MLX Model Downloader")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('../training_data').exists():
        print("❌ Please run this script from the model/model/ directory")
        sys.exit(1)
    
    # Check for huggingface-cli
    if not check_huggingface_cli():
        print("❌ huggingface-cli not found")
        print("💡 Install with: pip install huggingface_hub")
        print("💡 Or activate mlx-qwa environment: conda activate mlx-qwa")
        sys.exit(1)
    
    # List existing models
    list_existing_models()
    print()
    
    # Show available models
    print("📋 Available models for download:")
    for key, model in MODELS.items():
        print(f"{key}. {model['name']} ({model['size']})")
        print(f"   {model['description']}")
    
    print("\n💡 All models are MLX-compatible with .safetensors format")
    print("💡 Recommended for resume analysis: Options 1, 2, or 4")
    print("💡 For low memory systems: Options 2, 4, or 5")
    print("💡 Need to convert your own model? See convert_model.py")
    
    # Get user choice
    while True:
        choice = input("\nSelect model to download (1-5) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("👋 Goodbye!")
            sys.exit(0)
        
        if choice in MODELS:
            model_info = MODELS[choice]
            
            # Check if already exists
            if Path(model_info["folder"]).exists():
                print(f"⚠️ {model_info['folder']} already exists")
                overwrite = input("Overwrite? (y/n): ").strip().lower()
                if overwrite != 'y':
                    continue
            
            # Download the model
            if download_model(model_info):
                print(f"\n🎉 Ready to use! Launch MLX Chat with:")
                print(f"   cd ../..")
                print(f"   conda activate mlx-qwa")
                print(f"   python config_launcher.py")
                
                # Ask if they want to download another
                another = input("\nDownload another model? (y/n): ").strip().lower()
                if another != 'y':
                    break
            else:
                retry = input("Retry download? (y/n): ").strip().lower()
                if retry != 'y':
                    break
        else:
            print("❌ Invalid choice. Please select 1-5 or 'q'")

if __name__ == "__main__":
    main()