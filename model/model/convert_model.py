#!/usr/bin/env python3
"""
MLX Model Converter
Converts HuggingFace models to MLX format for use with MLX Chat
"""

import subprocess
import sys
from pathlib import Path

def check_mlx_lm():
    """Check if mlx-lm is available"""
    try:
        subprocess.run(['python', '-m', 'mlx_lm.convert', '--help'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_model(hf_path, output_name, quantize_bits=4):
    """Convert HuggingFace model to MLX format"""
    output_path = f"./{output_name}"
    
    print(f"\n🔄 Converting {hf_path} to MLX format...")
    print(f"Output: {output_path}")
    print(f"Quantization: {quantize_bits}-bit")
    print("This may take several minutes...\n")
    
    try:
        cmd = [
            'python', '-m', 'mlx_lm.convert',
            '--hf-path', hf_path,
            '--mlx-path', output_path,
            '--q-bits', str(quantize_bits)
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ Model converted successfully to {output_path}/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e}")
        return False

def main():
    print("🔧 MLX Model Converter")
    print("=" * 40)
    print("Convert HuggingFace models to MLX format for use with MLX Chat")
    print()
    
    # Check if we're in the right directory
    if not Path('../training_data').exists():
        print("❌ Please run this script from the model/model/ directory")
        sys.exit(1)
    
    # Check for mlx-lm
    if not check_mlx_lm():
        print("❌ mlx-lm not found")
        print("💡 Install with: pip install mlx-lm")
        print("💡 Or activate mlx-qwa environment: conda activate mlx-qwa")
        sys.exit(1)
    
    print("📋 Common conversion examples:")
    print("1. microsoft/DialoGPT-medium")
    print("2. microsoft/DialoGPT-small") 
    print("3. deepseek-ai/deepseek-coder-1.3b-instruct")
    print("4. mistralai/Mistral-7B-Instruct-v0.1")
    print("5. Custom HuggingFace model path")
    print()
    print("📖 MLX Documentation:")
    print("   https://github.com/ml-explore/mlx")
    print("   https://github.com/ml-explore/mlx/tree/main/docs")
    print()
    
    # Get model path
    while True:
        choice = input("Select example (1-4) or enter custom HuggingFace path: ").strip()
        
        if choice == "1":
            hf_path = "microsoft/DialoGPT-medium"
            output_name = "DialoGPT-Medium-MLX"
            break
        elif choice == "2":
            hf_path = "microsoft/DialoGPT-small"
            output_name = "DialoGPT-Small-MLX"
            break
        elif choice == "3":
            hf_path = "deepseek-ai/deepseek-coder-1.3b-instruct"
            output_name = "Deepseek-Coder-1.3B-MLX"
            break
        elif choice == "4":
            hf_path = "mistralai/Mistral-7B-Instruct-v0.1"
            output_name = "Mistral-7B-MLX"
            break
        elif choice and "/" in choice:  # Custom path
            hf_path = choice
            # Generate output name from model path
            model_name = hf_path.split("/")[-1]
            output_name = f"{model_name}-MLX"
            break
        else:
            print("❌ Invalid choice. Please select 1-4 or enter a HuggingFace model path")
    
    # Get quantization bits
    while True:
        bits_input = input("Quantization bits (4, 8, 16) [4]: ").strip()
        if not bits_input:
            quantize_bits = 4
            break
        try:
            quantize_bits = int(bits_input)
            if quantize_bits in [4, 8, 16]:
                break
            else:
                print("❌ Please choose 4, 8, or 16 bits")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Check if output exists
    if Path(output_name).exists():
        print(f"⚠️ {output_name} already exists")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("👋 Conversion cancelled")
            sys.exit(0)
    
    # Convert the model
    if convert_model(hf_path, output_name, quantize_bits):
        print(f"\n🎉 Model ready! Launch MLX Chat with:")
        print(f"   cd ../..")
        print(f"   conda activate mlx-qwa")
        print(f"   python config_launcher.py")
        print(f"\n📁 Model location: model/model/{output_name}/")
    else:
        print("\n❌ Conversion failed. Check the model path and try again.")
        print("\n💡 Tips:")
        print("   • Ensure the HuggingFace model exists and is accessible")
        print("   • Some models may not be compatible with MLX")
        print("   • Try a different quantization level (8 or 16 bits)")

if __name__ == "__main__":
    main()