#!/usr/bin/env python3
"""
MLX Model + LoRA Fusion Script
Combines a base model from model/model/ with a LoRA adapter from model/adapters/
"""

import os
import sys
import platform
from pathlib import Path
import subprocess

def check_mlx_compatibility():
    """Check if system can run MLX"""
    if platform.system() != "Darwin":
        print("❌ MLX requires macOS with Apple Silicon")
        return False
    
    try:
        import mlx
        return True
    except ImportError:
        print("❌ MLX not available - install with: pip install mlx")
        return False

def discover_models():
    """Find available models in model/model directory"""
    models = []
    model_dir = Path("model/model")
    
    if model_dir.exists():
        for item in model_dir.iterdir():
            if item.is_dir():
                config_file = item / "config.json"
                if config_file.exists():
                    models.append(item)
    
    return models

def discover_adapters():
    """Find available LoRA adapters in model/adapters directory"""
    adapters = []
    adapter_dir = Path("model/adapters")
    
    if adapter_dir.exists():
        for item in adapter_dir.iterdir():
            if item.suffix in [".npz", ".safetensors"] and "adapter" in item.name.lower():
                adapters.append(item)
    
    return adapters

def select_model(models):
    """Let user select a model"""
    if not models:
        print("❌ No models found in model/model/")
        print("💡 Copy a model to model/model/ first")
        return None
    
    print("\nAvailable models:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model.name}")
    
    while True:
        try:
            choice = int(input(f"\nSelect model (1-{len(models)}): ")) - 1
            if 0 <= choice < len(models):
                return models[choice]
            print("Invalid choice")
        except ValueError:
            print("Please enter a number")

def select_adapter(adapters):
    """Let user select a LoRA adapter"""
    if not adapters:
        print("❌ No LoRA adapters found in model/adapters/")
        print("💡 Train a LoRA adapter first using create_lora.py")
        return None
    
    print("\nAvailable LoRA adapters:")
    for i, adapter in enumerate(adapters, 1):
        size_kb = adapter.stat().st_size // 1024
        # Identify adapter type
        if adapter.name == "adapters.safetensors":
            adapter_type = "(Final)"
        elif adapter.name.startswith("0") and "adapters" in adapter.name:
            adapter_type = "(Checkpoint)"
        else:
            adapter_type = ""
        
        print(f"{i}. {adapter.name} {adapter_type} ({size_kb} KB)")
    
    while True:
        try:
            choice = int(input(f"\nSelect adapter (1-{len(adapters)}): ")) - 1
            if 0 <= choice < len(adapters):
                return adapters[choice]
            print("Invalid choice")
        except ValueError:
            print("Please enter a number")

def fuse_model(model_path, adapter_path, output_name):
    """Fuse model and LoRA adapter using MLX fuse script"""
    output_path = Path("model/model") / output_name
    
    # Convert to absolute paths since we'll run from MLX directory
    model_abs = model_path.absolute()
    adapter_abs = adapter_path.absolute()
    output_abs = output_path.absolute()
    
    # Use MLX fuse via mlx-lm package
    cmd = [
        "python", "-m", "mlx_lm.fuse",
        "--model", str(model_abs),
        "--adapter-file", str(adapter_abs),
        "--save-path", str(output_abs)
    ]
    
    print(f"\n🔥 Fusing model...")
    print(f"Base model: {model_path.name}")
    print(f"LoRA adapter: {adapter_path.name}")
    print(f"Output: {output_path}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Model fusion completed successfully!")
            print(f"Fused model saved to: {output_path}")
            return True
        else:
            print(f"❌ Fusion failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error running fusion: {e}")
        return False

def main():
    print("MLX Model + LoRA Fusion Tool")
    print("=" * 40)
    
    if not check_mlx_compatibility():
        return
    
    # Check if mlx-lm is available
    try:
        import mlx_lm
    except ImportError:
        print("❌ mlx-lm package not found")
        print("💡 Install with: pip install mlx-lm")
        return
    
    # Discover available models and adapters
    models = discover_models()
    adapters = discover_adapters()
    
    # Select model
    selected_model = select_model(models)
    if not selected_model:
        return
    
    # Select adapter
    selected_adapter = select_adapter(adapters)
    if not selected_adapter:
        return
    
    # Get output name
    default_name = f"{selected_model.name}_fused"
    output_name = input(f"\nOutput model name [{default_name}]: ").strip()
    if not output_name:
        output_name = default_name
    
    # Perform fusion
    success = fuse_model(selected_model, selected_adapter, output_name)
    
    if success:
        print(f"\n🎉 Fused model '{output_name}' is now available in MLX Chat!")
    else:
        print("\n❌ Fusion failed. Check error messages above.")

if __name__ == "__main__":
    main()
