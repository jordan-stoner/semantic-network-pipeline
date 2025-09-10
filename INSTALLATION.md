# MLX Chat Installation Guide

## Quick Start (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mlx-chat.git
   cd mlx-chat
   ```

2. **Run initial setup:**
   ```bash
   python initial_setup.py
   ```
   This will:
   - Install Miniconda if not present
   - Create the `mlx-qwa` conda environment
   - Install all required dependencies

3. **Download at least one model:**
   ```bash
   conda activate mlx-qwa
   huggingface-cli download mlx-community/Meta-Llama-3-8B-Instruct-4bit --local-dir ./model/model/Llama-3-8B-MLX
   ```

4. **Launch the application:**
   ```bash
   # Option 1: Configuration interface (recommended)
   python config_launcher.py
   
   # Option 2: Direct launch with defaults
   python web_chat.py
   ```

## System Requirements

- **Operating System:** macOS (primary), Linux (should work)
- **Memory:** 16GB+ RAM recommended for larger models
- **Storage:** 5GB+ free space (models can be 2-8GB each)
- **Python:** 3.10 (automatically installed in conda environment)

## Manual Installation

If the automatic setup fails, follow these steps:

### 1. Install Conda
Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution).

### 2. Create Environment
```bash
conda create -n mlx-qwa python=3.10 -y
conda activate mlx-qwa
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
```

## Adding Content for Analysis

### Text Analysis Files
Place your text files in the `model/training_data/` directory:

```
model/training_data/
├── document1.txt
├── document2.txt
├── report.docx
└── notes.txt
```

**Supported formats:**
- `.txt` files (UTF-8 encoding)
- `.docx` files (Microsoft Word documents)

### Running Text Analysis
```bash
conda activate mlx-qwa
python create_wordcloud.py
```

This will:
1. Analyze all files in `model/training_data/`
2. Generate an interactive word cloud visualization
3. Optionally create LoRA training datasets

## Model Management

### Downloading Models
Models must be MLX-compatible. Recommended models:

```bash
# Llama 3 8B (4-bit quantized) - Recommended
huggingface-cli download mlx-community/Meta-Llama-3-8B-Instruct-4bit --local-dir ./model/model/Llama-3-8B-MLX

# Deepseek Coder 1.3B - Lightweight option
python -m mlx_lm.convert --hf-path deepseek-ai/deepseek-coder-1.3b-instruct --mlx-path ./model/model/Deepseek-Coder-1.3B-MLX --q-bits 4

# Mistral 7B
python -m mlx_lm.convert --hf-path mistralai/Mistral-7B-Instruct-v0.1 --mlx-path ./model/model/Mistral-7B-MLX --q-bits 4
```

### Model Directory Structure
```
model/model/
├── Llama-3-8B-MLX/
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer.json
└── Deepseek-Coder-1.3B-MLX/
    ├── config.json
    ├── model.safetensors
    └── tokenizer.json
```

## LoRA Training Workflow

1. **Add source materials** to `model/training_data/`
2. **Generate training data:**
   ```bash
   python create_wordcloud.py
   # Choose option 3 for both vocabulary and style training
   ```
3. **Train LoRA adapter:**
   ```bash
   python create_lora.py
   ```
4. **Use in chat** - Select adapter in configuration interface

## Troubleshooting

### Common Issues

**"Model not loaded yet" error:**
- Ensure you've downloaded at least one model
- Check that model files are in `model/model/MODEL_NAME/`
- Verify the model has `config.json`, `.safetensors`, and tokenizer files

**Port conflicts:**
- Close existing MLX Chat instances
- Check if ports 5000 or 5001 are in use by other applications

**Memory issues:**
- Use smaller models (1.3B instead of 8B)
- Close other memory-intensive applications
- Consider using 4-bit quantized models

**Environment issues:**
- Always activate the conda environment: `conda activate mlx-qwa`
- If environment is corrupted, delete and recreate:
  ```bash
  conda env remove -n mlx-qwa
  python initial_setup.py
  ```

### Getting Help

1. Check the [documentation](README.md) for detailed information
2. Review [troubleshooting guides](CSS_TROUBLESHOOTING.md)
3. Ensure you're using the correct conda environment
4. Verify all dependencies are installed correctly

## Next Steps

After installation:
1. Launch the configuration interface: `python config_launcher.py`
2. Select your model and any LoRA adapters
3. Start chatting with your AI assistant
4. Explore text analysis features with your own documents

## Third-Party Dependencies

### Core Frameworks
- **[MLX](https://github.com/ml-explore/mlx)** - Apple's machine learning framework
- **[MLX-LM](https://github.com/ml-explore/mlx-examples/tree/main/llms)** - Language model support
- **[Flask](https://flask.palletsprojects.com/)** - Web framework for chat interface
- **[Anaconda](https://www.anaconda.com/)** - Python environment management

### Text Processing & Analysis
- **[NLTK](https://www.nltk.org/)** - Natural Language Toolkit
- **[python-docx](https://python-docx.readthedocs.io/)** - Word document processing
- **[NumPy](https://numpy.org/)** - Numerical computing
- **[Matplotlib](https://matplotlib.org/)** - Data visualization

### Web Technologies
- **[Bootstrap](https://getbootstrap.com/)** - CSS framework
- **[Bootstrap Icons](https://icons.getbootstrap.com/)** - Icon library
- **[Vis.js](https://visjs.org/)** - Network visualization for word relationships

### Model Sources
- **[Hugging Face](https://huggingface.co/)** - Model repository
- **[MLX Community](https://huggingface.co/mlx-community)** - Pre-converted MLX models