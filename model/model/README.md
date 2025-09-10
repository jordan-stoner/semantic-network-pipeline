# MLX Models Directory

This directory contains your downloaded MLX models for chat and text analysis.

## Quick Download

Run the model downloader to get started:

```bash
conda activate mlx-qwa
cd model/model
python download_models.py
```

## Recommended Models for Resume Analysis

### 🎯 Best for Resumes & Professional Writing
- **Llama-3-8B-Instruct** - Excellent general purpose model
- **Qwen2.5-Coder-1.5B** - Great for technical resumes and coding experience
- **Deepseek-Coder-1.3B** - Lightweight option for technical content

### 💾 Low Memory Options (< 8GB RAM)
- **Deepseek-Coder-1.3B** (~800MB)
- **Qwen2.5-Coder-1.5B** (~900MB) 
- **Phi-3-Mini-4K** (~2.3GB)

### 🚀 High Performance (16GB+ RAM)
- **Llama-3-8B-Instruct** (~4.5GB)
- **Mistral-7B-Instruct** (~4GB)

## Converting Your Own Models

**⚠️ Important: MLX Chat requires MLX-compatible models (.safetensors format)**

To convert HuggingFace models to MLX format:

```bash
# Use the conversion script
python convert_model.py

# Or convert manually
python -m mlx_lm.convert --hf-path MODEL_NAME --mlx-path ./OUTPUT_NAME --q-bits 4
```

**MLX Documentation:**
- [MLX Framework](https://github.com/ml-explore/mlx)
- [MLX Documentation](https://github.com/ml-explore/mlx/tree/main/docs)
- [MLX Quickstart](https://github.com/ml-explore/mlx?tab=readme-ov-file#quickstart)

## Manual Download

For pre-converted MLX models:

```bash
# Example: Llama 3 8B (MLX format)
huggingface-cli download mlx-community/Meta-Llama-3-8B-Instruct-4bit --local-dir ./Llama-3-8B-MLX

# Example: Lightweight coder model (MLX format)
huggingface-cli download mlx-community/deepseek-coder-1.3b-instruct-4bit --local-dir ./Deepseek-Coder-1.3B-MLX
```

## Directory Structure

After downloading, your models will be organized like this:

```
model/model/
├── Llama-3-8B-MLX/
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer.json
├── Deepseek-Coder-1.3B-MLX/
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer.json
└── download_models.py
```

## Using Your Models

1. **Download at least one model** using the script above
2. **Launch MLX Chat:**
   ```bash
   cd ../..
   python config_launcher.py
   ```
3. **Select your model** in the configuration interface
4. **Start chatting!**

## Model Capabilities

All recommended models excel at:
- Resume writing and editing
- Professional document analysis
- Technical writing assistance
- Career advice and job descriptions
- Interview preparation
- Skills assessment and recommendations

## Storage Requirements

- Each model requires 800MB - 4.5GB of storage
- Models are downloaded once and reused
- You can have multiple models installed
- Delete unused model folders to free space

## Troubleshooting

**Download fails:**
- Ensure you're in the mlx-qwa conda environment
- Check internet connection
- Verify huggingface-cli is installed: `pip install huggingface_hub`

**Model not recognized:**
- Ensure the model folder contains config.json and .safetensors files (MLX format)
- GGUF and standard HuggingFace models need conversion (use convert_model.py)
- Restart MLX Chat after downloading new models

**Model conversion issues:**
- Use `python convert_model.py` for guided conversion
- Some models may not be compatible with MLX
- Try different quantization levels (4, 8, or 16 bits)