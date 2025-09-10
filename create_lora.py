#!/usr/bin/env python3
"""
LoRA Fine-tuning Script for MLX
Processes text files from /q/model/training_data/ and creates a fine-tuned model
"""

import os
import json
import random
import subprocess
import sys
import platform
from pathlib import Path

def check_mlx_compatibility():
    """Check if system can run MLX"""
    if platform.system() != "Darwin":
        print("❌ MLX requires macOS with Apple Silicon")
        print("💡 Training data generation completed - use on Mac for LoRA training")
        return False
    
    try:
        import mlx
        return True
    except ImportError:
        print("❌ MLX not available - install with: pip install mlx")
        return False

def use_existing_training_data():
    """Use existing JSONL training files from lora_training directory"""
    lora_training_dir = Path(__file__).parent / "model" / "lora_training"
    
    if not lora_training_dir.exists():
        print(f"Error: Training directory {lora_training_dir} does not exist")
        print("Run create_wordcloud.py first to generate training data")
        return False
    
    # Look for existing training files
    vocab_file = lora_training_dir / "vocabulary_training.jsonl"
    style_file = lora_training_dir / "style_training.jsonl"
    
    available_files = []
    if vocab_file.exists():
        available_files.append(("vocabulary", vocab_file))
    if style_file.exists():
        available_files.append(("style", style_file))
    
    if not available_files:
        print("No training files found in lora_training directory")
        print("Run create_wordcloud.py first to generate training data")
        return False
    
    print("Available training files:")
    for i, (name, path) in enumerate(available_files, 1):
        with open(path, 'r') as f:
            line_count = sum(1 for _ in f)
        print(f"{i}. {name} training ({line_count} examples)")
    
    # Add combined option if both files exist
    if len(available_files) == 2:
        print(f"{len(available_files) + 1}. Combined (both datasets)")
    
    # Let user choose which file to use
    if len(available_files) == 1:
        choice = 1
        print(f"Using {available_files[0][0]} training data")
    else:
        max_choice = len(available_files) + (1 if len(available_files) == 2 else 0)
        try:
            choice = int(input(f"Choose training option (1-{max_choice}): "))
            if choice < 1 or choice > max_choice:
                print("Invalid choice")
                return False
        except ValueError:
            print("Invalid input")
            return False
    
    # Load the selected training data
    training_data = []
    
    if len(available_files) == 2 and choice == 3:
        # Combined option - load both files
        print("Loading combined training data...")
        for name, path in available_files:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    training_data.append(data)
    else:
        # Single file option
        selected_file = available_files[choice - 1][1]
        with open(selected_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                training_data.append(data)
    
    print(f"Loaded {len(training_data)} training examples")
    
    # Shuffle and split data
    random.shuffle(training_data)
    total = len(training_data)
    train_size = int(total * 0.8)
    valid_size = int(total * 0.1)
    
    train_data = training_data[:train_size]
    valid_data = training_data[train_size:train_size + valid_size]
    test_data = training_data[train_size + valid_size:]
    
    # Create training data directory
    data_dir = Path(__file__).parent / "model" / "lora"
    data_dir.mkdir(exist_ok=True)
    
    # Write JSONL files
    with open(data_dir / "train.jsonl", 'w') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
    
    with open(data_dir / "valid.jsonl", 'w') as f:
        for item in valid_data:
            f.write(json.dumps(item) + '\n')
    
    with open(data_dir / "test.jsonl", 'w') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"Training data prepared: {len(train_data)} train, {len(valid_data)} valid, {len(test_data)} test")
    return str(data_dir)

def process_text_files_fallback(source_dir, weight_keywords=None):
    """Convert text files to JSONL format for LoRA training with optional weighting (fallback method)"""
    source_path = Path(source_dir).resolve()
    
    if not source_path.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return False
    
    # Security: Validate path is within project directory
    allowed_base = Path(__file__).parent.resolve()
    try:
        source_path.relative_to(allowed_base)
    except ValueError:
        print(f"Error: Access denied to directory outside project: {source_dir}")
        return False
    
    # Collect all text files
    text_files = list(source_path.glob("*.txt"))
    if not text_files:
        print(f"No .txt files found in {source_dir}")
        return False
    
    print(f"Found {len(text_files)} text files")
    
    # Default weight keywords if none provided
    if weight_keywords is None:
        weight_keywords = []
    
    # Read and process all text content
    all_texts = []
    weighted_texts = []  # For high-priority content
    max_chars = 1500  # Safe limit for ~400 tokens (4 chars ≈ 1 token)
    
    for file_path in text_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                # Split into chunks that fit within token limits
                chunks = []
                
                # First try splitting on paragraphs
                paragraphs = content.split('\n\n')
                current_chunk = ""
                
                for paragraph in paragraphs:
                    paragraph = paragraph.strip()
                    if not paragraph:
                        continue
                        
                    # If adding this paragraph exceeds limit, save current chunk
                    if len(current_chunk) + len(paragraph) + 2 > max_chars:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = paragraph
                    else:
                        if current_chunk:
                            current_chunk += "\n\n" + paragraph
                        else:
                            current_chunk = paragraph
                
                # Add the last chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If chunks are still too long, split by sentences
                final_chunks = []
                for chunk in chunks:
                    if len(chunk) <= max_chars:
                        final_chunks.append(chunk)
                    else:
                        # Split long chunks by sentences
                        sentences = chunk.replace('. ', '.\n').split('\n')
                        current_chunk = ""
                        
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if not sentence:
                                continue
                                
                            if len(current_chunk) + len(sentence) + 1 > max_chars:
                                if current_chunk:
                                    final_chunks.append(current_chunk.strip())
                                current_chunk = sentence
                            else:
                                if current_chunk:
                                    current_chunk += " " + sentence
                                else:
                                    current_chunk = sentence
                        
                        if current_chunk:
                            final_chunks.append(current_chunk.strip())
                
                # Categorize chunks by importance
                for chunk in final_chunks:
                    if len(chunk) > 50:  # Only include substantial chunks
                        chunk_data = {"text": chunk}
                        
                        # Check if chunk contains weighted keywords
                        is_weighted = False
                        if weight_keywords:
                            chunk_lower = chunk.lower()
                            for keyword in weight_keywords:
                                if keyword.lower() in chunk_lower:
                                    is_weighted = True
                                    break
                        
                        all_texts.append(chunk_data)
                        if is_weighted:
                            weighted_texts.append(chunk_data)
    
    if not all_texts:
        print("No valid text content found")
        return False
    
    # Add weighted content multiple times (3x repetition for emphasis)
    if weighted_texts:
        print(f"Found {len(weighted_texts)} high-priority chunks (will be repeated 3x)")
        all_texts.extend(weighted_texts * 2)  # Add 2 more copies (total 3x)
    
    print(f"Created {len(all_texts)} training examples")
    print(f"Average length: {sum(len(item['text']) for item in all_texts) // len(all_texts)} characters")
    
    # Shuffle and split data
    random.shuffle(all_texts)
    total = len(all_texts)
    train_size = int(total * 0.8)
    valid_size = int(total * 0.1)
    
    train_data = all_texts[:train_size]
    valid_data = all_texts[train_size:train_size + valid_size]
    test_data = all_texts[train_size + valid_size:]
    
    # Create training data directory
    data_dir = Path(__file__).parent / "model" / "lora"
    data_dir.mkdir(exist_ok=True)
    
    # Write JSONL files
    with open(data_dir / "train.jsonl", 'w') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
    
    with open(data_dir / "valid.jsonl", 'w') as f:
        for item in valid_data:
            f.write(json.dumps(item) + '\n')
    
    with open(data_dir / "test.jsonl", 'w') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"Training data created: {len(train_data)} train, {len(valid_data)} valid, {len(test_data)} test")
    return str(data_dir)

def get_next_version(adapter_dir, base_name):
    """Get next version number for LoRA adapter"""
    version = 1
    while True:
        version_name = f"{base_name}_v{version:02d}.npz"
        if not (adapter_dir / version_name).exists():
            return version, version_name
        version += 1

def run_lora_training(data_dir):
    """Run the LoRA training process using mlx_lm"""
    
    # Look for models in model/model directory
    model_dir = Path(__file__).parent / "model" / "model"
    available_models = []
    
    if model_dir.exists():
        for item in model_dir.iterdir():
            if item.is_dir():
                config_file = item / "config.json"
                if config_file.exists():
                    available_models.append(item)
    
    if not available_models:
        print("❌ No models found in model/model directory")
        print("💡 Copy a model to model/model/ first")
        return False
    
    # Select model
    if len(available_models) == 1:
        selected_model = available_models[0]
        print(f"Using model: {selected_model.name}")
    else:
        print("\nAvailable models:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model.name}")
        
        while True:
            try:
                choice = int(input(f"\nSelect model for LoRA training (1-{len(available_models)}): ")) - 1
                if 0 <= choice < len(available_models):
                    selected_model = available_models[choice]
                    break
                print("Invalid choice")
            except ValueError:
                print("Please enter a number")
    
    # Get descriptor from user
    while True:
        descriptor = input("\nEnter a descriptive name for this LoRA (e.g., 'resume', 'creative', 'technical'): ").strip()
        if descriptor and descriptor.replace('-', '').replace('_', '').isalnum():
            break
        print("Please enter a valid descriptor (alphanumeric, hyphens, underscores only)")
    
    # Create model-specific adapter directory
    model_name = selected_model.name
    adapter_base_dir = Path(__file__).parent / "model" / "adapters"
    model_adapter_dir = adapter_base_dir / f"{model_name}_lora"
    model_adapter_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate versioned filename
    base_name = f"{model_name}_lora-{descriptor}"
    version, adapter_filename = get_next_version(model_adapter_dir, base_name)
    adapter_path = model_adapter_dir / adapter_filename
    
    print(f"\n📁 LoRA will be saved as: {adapter_path}")
    
    # Use MLX LoRA training with custom naming
    cmd = [
        "python", "-m", "mlx_lm", "lora",
        "--model", str(selected_model),
        "--data", data_dir,
        "--train",
        "--iters", "100",
        "--batch-size", "1",
        "--num-layers", "4",
        "--adapter-path", str(adapter_path.parent),
        "--save-every", "100"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    print(f"🚀 Starting LoRA training...")
    print(f"Model: {model_name}")
    print(f"Descriptor: {descriptor}")
    print(f"Version: v{version:02d}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ LoRA training completed successfully!")
            
            # Look for the actual output file and rename it to our convention
            adapter_dir = adapter_path.parent
            adapters_file = adapter_dir / "adapters.safetensors"
            
            if adapters_file.exists():
                # Rename to our naming convention
                adapters_file.rename(adapter_path.with_suffix('.safetensors'))
                print(f"📁 Adapter renamed to: {adapter_path.with_suffix('.safetensors')}")
            elif adapter_path.exists():
                print(f"📁 Adapter saved to: {adapter_path}")
            else:
                # Look for any .safetensors files in the directory
                safetensor_files = list(adapter_dir.glob("*.safetensors"))
                if safetensor_files:
                    # Rename the first one found
                    safetensor_files[0].rename(adapter_path.with_suffix('.safetensors'))
                    print(f"📁 Adapter renamed to: {adapter_path.with_suffix('.safetensors')}")
                else:
                    print("⚠️ Warning: Adapter file not found in expected location")
            
            return True
        else:
            print(f"❌ Training failed: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"Error running LoRA training: {e}")
        return False

def main():
    print("MLX LoRA Fine-tuning Script")
    print("=" * 40)
    
    if not check_mlx_compatibility():
        return
    
    # Use existing training data from wordcloud generation
    data_dir = use_existing_training_data()
    if not data_dir:
        print("\nFallback: Processing raw text files...")
        source_dir = str(Path(__file__).parent / "model" / "training_data")
        
        # Optional: Define keywords to emphasize (3x repetition)
        weight_keywords = []
        
        if weight_keywords:
            print(f"Emphasizing content with keywords: {weight_keywords}")
        
        # Process text files as fallback
        data_dir = process_text_files_fallback(source_dir, weight_keywords)
        if not data_dir:
            sys.exit(1)
    
    # Run training
    success = run_lora_training(data_dir)
    
    if success:
        print("\n🎉 Training complete! You can now use the adapter with your MLX chat application.")
    else:
        print("\n❌ Training failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
