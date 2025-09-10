# MLX Chat - Local AI Chat Interface

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![MLX](https://img.shields.io/badge/MLX-Apple-orange.svg)](https://github.com/ml-explore/mlx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

**Goal**: Analyze user-collected documents (job posting descriptions) to identify common vocabulary patterns, extract key terms and their contextual relationships, train custom LoRA adapters from this data, and deploy a local LLM fine-tuned to suggest targeted resume improvements.

### Data Engineering Demonstration

This project serves as a **comprehensive data pipeline demonstration** created during my job search to showcase critical thinking and technical skills across the full data engineering lifecycle:

#### 🔄 **ETL Pipeline** (Extract, Transform, Load)
- **Extract**: Ingest job posting documents from various formats (.txt, .docx)
- **Transform**: Multi-stage text processing with POS tagging, stop word filtering, and frequency analysis
- **Load**: Generate structured training datasets in MLX-compatible JSONL format

#### ✅ **Data Validation & Quality Assurance**
- Input validation with path traversal protection and encoding handling
- Statistical filtering to remove noise (frequency thresholds, length constraints)
- Data integrity checks ensuring sentence boundaries and context preservation

#### 📊 **Analysis & Statistical Modeling**
- Linguistic analysis using NLTK for POS tagging, lemmatization, and collocation detection
- Network graph visualization of word relationships and semantic connections
- Frequency distribution analysis to identify distinctive vocabulary patterns

#### 🤖 **AI/ML Model Training & Inference**
- Custom LoRA (Low-Rank Adaptation) fine-tuning on domain-specific vocabulary
- MLX framework integration for Apple Silicon optimization
- Interactive chat interface for real-time model inference and resume suggestions

### Technical Architecture

A sophisticated web-based chat interface for Apple's MLX framework with advanced text analysis and LoRA fine-tuning capabilities.

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/mlx-chat.git
cd mlx-chat

# 2. Run setup (installs conda + dependencies)
python initial_setup.py

# 3. Download a model
conda activate mlx-qwa
huggingface-cli download mlx-community/Meta-Llama-3-8B-Instruct-4bit --local-dir ./model/model/Llama-3-8B-MLX

# 4. Launch
python config_launcher.py
```

## 🎯 Complete Resume Optimization Workflow

### Step 1: Collect Job Postings (Any OS)
1. **Gather target job descriptions** - Copy/paste job postings into text files
2. **Save to training directory**:
   ```
   model/training_data/
   ├── software_engineer_google.txt
   ├── data_scientist_meta.txt
   ├── ml_engineer_openai.txt
   └── backend_dev_stripe.txt
   ```
3. **Recommended**: 10-20 job postings for best results

### Step 2: Analyze Vocabulary Patterns (Any OS)
```bash
python create_wordcloud.py
```
**Configuration prompts:**
- Minimum word length: `4` (focus on substantial terms)
- Include alphanumeric: `Y` (capture technical terms)
- Include proper nouns: `Y` (company/technology names)
- Frequency threshold: `30%` (top distinctive words)
- Generate LoRA training data: `Y` → Choose `3` (both vocabulary and style)

**Output**: Interactive word cloud showing key terms and relationships

<img width="704" height="617" alt="image" src="https://github.com/user-attachments/assets/50757e88-7689-436d-bb5c-1aa2e2100571" />

### Step 3: Train Custom LoRA (macOS only)
```bash
python create_lora.py
```
**Training prompts:**
- Select your base model (e.g., Llama-3-8B-MLX)
- Enter descriptor: `resume` or `job_match`
- Training completes in 5-10 minutes

**Output**: `model/adapters/Llama-3-8B-MLX_lora/Llama-3-8B-MLX_lora-resume_v01.npz`

### Step 4: Launch Resume Assistant (macOS only)
```bash
python config_launcher.py
```
1. **Select your base model** from the list
2. **Choose your trained LoRA adapter** (e.g., "Llama-3-8B-MLX: resume_v01")
3. **Click "Launch MLX Chat"**
 
<img width="244" height="329" alt="image" src="https://github.com/user-attachments/assets/51bbc88a-0b98-4bb8-9dc2-e14f01b9b5e7" />    

<img width="572" height="329" alt="image" src="https://github.com/user-attachments/assets/b001155f-cbf5-4a3b-893f-e97554554972" />

### Step 5: Optimize Your Resume
**Example prompts for the fine-tuned model:**

```
"Analyze my current resume and suggest improvements based on the job market data you were trained on. Here's my resume: [paste resume]"

"What key technical skills should I emphasize for software engineering roles?"

"Rewrite this experience bullet point to better match industry vocabulary: [paste bullet point]"

"What buzzwords and technical terms are most important in my target job market?"
```

**The model will provide targeted suggestions using vocabulary patterns from your job posting analysis.**



## 📁 Quick File Setup

Drop your job posting files here:
```
model/training_data/
├── job_posting_1.txt
├── job_posting_2.txt
└── job_posting_3.docx
```

## Features

- 🌋 **Dark Mode Interface** - Professional magma-themed UI
- 💬 **Real-time Chat** - Interactive conversation with MLX models
- 🔧 **Model Selection** - Choose from available MLX models
- 🎯 **LoRA Support** - Load fine-tuned LoRA adapters
- 📊 **Advanced Text Analysis** - Word cloud visualization with linguistic analysis and interactive charts
- 🎯 **Dual LoRA Training** - Generate vocabulary and style training datasets
- 🚀 **Easy Setup** - Automatic environment creation and dependency management
- 🔒 **Environment Isolation** - Runs in dedicated Python 3.10 conda environment

## Quick Start

### Method 1: Initial Setup (Required First Time)
```bash
# First time setup - creates mlx-qwa environment
python initial_setup.py

# Download at least one model (required)
conda activate mlx-qwa
huggingface-cli download mlx-community/Meta-Llama-3-8B-Instruct-4bit --local-dir ./model/model/Llama-3-8B-MLX
```

### Method 2: Configuration Launch (Recommended)
1. **Double-click `Launch MLX Chat.command` (macOS only)**
   - Activates `mlx-qwa` conda environment
   - Opens configuration page in default browser
   - Select your preferred model and LoRA adapter
   - Click "Launch MLX Chat" to start

2. **Or run from terminal (macOS with Apple Silicon):**
   ```bash
   conda activate mlx-qwa
   python config_launcher.py
   ```

### Method 3: Direct Launch (Default Settings - macOS only)
```bash
conda activate mlx-qwa
python web_chat.py
```

## Environment Management

### Automatic Setup (First Time)
- **Conda Detection**: Automatically detects or installs Miniconda if needed
- **Environment Creation**: Creates `mlx-qwa` conda environment with Python 3.10
- **Dependency Installation**: Installs all packages from `requirements.txt`
- **Cross-Platform**: Works on macOS and Linux with automatic architecture detection

### Manual Setup (Alternative)
```bash
# Create environment manually
conda create -n mlx-qwa python=3.10 -y
conda activate mlx-qwa
pip install -r requirements.txt
```

## Model and LoRA Management

### Model Setup
- **Download Models**: Users must download their own MLX-compatible models
- **Model Directory**: Place models in `model/model/` directory
- **Supported Models**: Any MLX model with config.json, .safetensors, and tokenizer files
- **Recommended Models**:
  ```bash
  # Llama 3 8B (4-bit quantized)
  conda activate mlx-qwa
  huggingface-cli download mlx-community/Meta-Llama-3-8B-Instruct-4bit --local-dir ./model/model/Llama-3-8B-MLX
  
  # Deepseek-Coder 1.3B
  python -m mlx_lm.convert --hf-path deepseek-ai/deepseek-coder-1.3b-instruct --mlx-path ./model/model/Deepseek-Coder-1.3B-MLX --q-bits 4
  
  # Mistral 7B
  python -m mlx_lm.convert --hf-path mistralai/Mistral-7B-Instruct-v0.1 --mlx-path ./model/model/Mistral-7B-MLX --q-bits 4
  ```

### Detailed Configuration Settings

#### Word Cloud Analysis Settings
- **Minimum word length**: `4` characters (captures substantial terms like "Python", "React")
- **Include alphanumeric**: `Yes` (includes "API", "ML", "AI", "3D")
- **Include proper nouns**: `Yes` (captures "AWS", "Docker", "Kubernetes")
- **Frequency threshold**: `30-50%` (focuses on distinctive vocabulary, not common words)
- **Exclusions**: Add company-specific terms that don't apply broadly

#### LoRA Training Parameters
- **Iterations**: `100` (good balance of training time vs. quality)
- **Batch size**: `1` (memory efficient for consumer hardware)
- **LoRA layers**: `4` (sufficient for vocabulary adaptation)
- **Training time**: 5-10 minutes on Apple Silicon

#### Expected Outcomes

**After Word Cloud Analysis:**
- Visual network of 50-100 key industry terms
- Word relationships showing technical skill clusters
- Training datasets with 200-500 examples each

**After LoRA Training:**
- Model understands industry-specific vocabulary
- Responses use terminology from your target job market
- Suggestions align with current hiring trends

**Resume Optimization Results:**
- Bullet points rewritten with industry buzzwords
- Skills section optimized for ATS systems
- Experience descriptions matching job posting language
- Technical terminology aligned with market expectations

### LoRA Adapter Workflow
1. **Add source materials** to `model/training_data/` folder
2. **Generate training data:**
   ```bash
   conda activate mlx-qwa
   python create_wordcloud.py model/training_data/
   # Choose option 3 for both vocabulary and style training data
   # Files saved to model/lora_training/
   ```
3. **Train LoRA adapter (macOS with Apple Silicon only):**
   ```bash
   python create_lora.py
   # Select model and enter descriptive name
   # Creates organized adapter: model/adapters/ModelName_lora/ModelName_lora-descriptor_v01.npz
   ```
4. **Optional: Fuse adapter with base model (macOS with Apple Silicon only):**
   ```bash
   python fuse_model.py
   # Creates permanent fused model (no runtime adapter loading)
   ```
5. **Use in chat (macOS with Apple Silicon only)** - Select the adapter or fused model in configuration page

## Project Structure

```
mlx-chat/
├── initial_setup.py         # Environment setup and dependency installation
├── config_launcher.py       # Configuration page launcher (macOS only)
├── web_chat.py              # Main MLX Chat application (macOS only)

├── create_wordcloud.py      # Word frequency analysis (cross-platform)
├── create_lora.py           # LoRA dataset generation (macOS only for training)
├── fuse_model.py            # Model + LoRA fusion utility (macOS only)
├── Launch MLX Chat.command  # Double-click launcher (macOS only)
├── requirements.txt         # Python dependencies
├── system_prompt.txt        # Default system prompt
├── static/css/magma-theme.css  # Design system
├── templates/chat.html      # Chat interface
├── templates/wordcloud_template.html  # Word cloud visualization template
└── model/
    ├── training_data/          # Source materials for training
    ├── lora_training/          # Generated training datasets (.jsonl)
    ├── lora/                   # MLX training splits (train/valid/test)
    ├── adapters/               # Organized LoRA adapters by model
    │   ├── ModelName_lora/     # Model-specific adapter folder
    │   │   └── ModelName_lora-descriptor_v01.npz
    ├── wordcloud/              # Generated wordcloud visualizations
    └── model/                  # Base models directory
```

## Configuration Features

### Model Selection
- **Visual Interface**: Magma-themed configuration page
- **Auto-Detection**: Scans `model/model/` directory for MLX models
- **Model Information**: Shows model name, path, and size
- **Default Selection**: Auto-selects first available model
- **No Models Found**: Displays instructions to download models

### LoRA Adapter Selection
- **Optional Loading**: Choose "No Adapter" or select trained adapter
- **Organized Structure**: Adapters organized by model in subfolders
- **Descriptive Names**: Shows model, descriptor, and version (e.g., "Llama-3-8B-MLX: resume_v01")
- **Size Information**: Shows adapter file size and path

### Launch Process
1. **Configuration Page** (port 5001) - Select model and adapter
2. **Main Chat Interface** (port 5000) - Chat with configured model
3. **Auto-Redirect** - Browser automatically navigates to chat page

## Runtime Files

These files are generated during operation and excluded from git:

- **`chat_config.json`** - Current model and adapter selection
- **`slider_preferences.json`** - UI parameter preferences
- **`model/wordcloud/wordcloud.html`** - Generated word frequency visualization

## System Requirements

### Text Analysis Tools (Cross-Platform)
- **Operating System**: Windows, macOS, Linux
- **Python**: 3.10+ with NLTK, pathlib, collections
- **Scripts**: `create_wordcloud.py`, `create_lora.py`, `fuse_model.py`
- **Use Case**: Document analysis, training data generation

### MLX Chat Interface (Apple Silicon Only)
- **Operating System**: macOS with Apple Silicon (M1/M2/M3)
- **Python**: 3.10 (automatically installed in `mlx-qwa` environment)
- **Conda**: Anaconda or Miniconda
- **Memory**: 16GB+ recommended for larger models
- **Storage**: 2GB+ for dependencies and modelsendencies and models

## Dependencies

### Core Dependencies
- `flask>=2.3.0` - Web framework
- `mlx>=0.0.1` - Apple MLX framework
- `mlx-lm>=0.0.1` - MLX language models

### Text Processing
- `nltk>=3.8` - Natural language toolkit (POS tagging, lemmatization, stemming, collocations)
- `python-docx>=0.8.11` - Word document processing

### Visualization
- `vis.js` (CDN) - Network visualization for word relationships
- `bootstrap-icons` (CDN) - Professional icon set

### Data Processing
- `numpy>=1.24.0` - Numerical computing
- `matplotlib>=3.7.0` - Plotting and visualization

### Optional
- `Pillow>=10.0.0` - Image processing
- `beautifulsoup4>=4.12.0` - HTML parsing
- `spacy` - Advanced NLP for acronym detection

## Design System

This project follows strict design standards:

- **Dark Mode Only** - All interfaces use dark backgrounds
- **Magma Color Palette** - Consistent orange/red accent colors (#ff6b35, #ff4500)
- **Bootstrap Icons** - No emoji, professional icons only
- **Single Source Files** - No duplicate or versioned files

## Troubleshooting

### Launch Process Issues
- **403 Error After Launch**: Config server shuts down before main server fully starts
  - **Solution**: Wait 10-12 seconds, then manually go to `http://127.0.0.1:5000`
  - **Root Cause**: Timing issue between config server shutdown and main server startup
  - **Improved**: Extended wait times to reduce occurrence
- **Terminal Won't Close**: Launch script waiting for user input
  - **Fixed**: Automatic terminal closure after successful launch
- **Server Stops After Launch**: Main server dies when config server exits
  - **Fixed**: Main server now runs in detached session

### CSS Styling Issues
- **Button Icon Spacing**: Icons too close to text in buttons
  - **Root Cause**: Bootstrap framework classes (`.me-1`, `.me-2`) override custom styles
  - **Solution**: Use higher CSS specificity or move elements outside message bubbles
  - **See**: [CSS_TROUBLESHOOTING.md](CSS_TROUBLESHOOTING.md) for detailed debugging
- **Dynamic Elements Not Styled**: JavaScript-created buttons don't follow CSS
  - **Root Cause**: Message bubble containers create different CSS inheritance context
  - **Solution**: Move problematic UI elements outside `.message-bubble` containers

### Environment Issues
- **Missing conda**: Install Anaconda or Miniconda first
- **Environment creation fails**: Check conda permissions and disk space
- **Package installation fails**: Try manual installation: `pip install -r requirements.txt`

### Port Conflicts
- **Port 5000 in use**: Close existing MLX Chat instances
- **Port 5001 in use**: Close configuration page and restart

### Model Loading
- **Model not found**: Check model path and MLX compatibility
- **LoRA loading fails**: Verify adapter file format (.npz) and path

## Documentation

- [Complete Documentation](MLX_CHAT_DOCUMENTATION.md)
- [Word Cloud Workflow](WORDCLOUD_TO_LORA_WORKFLOW.md)
- [Design Standards](DARK_MODE_DESIGN_STANDARDS.md)
- [CSS Troubleshooting](CSS_TROUBLESHOOTING.md)
- [Project Structure](PROJECT_STRUCTURE.md)
- [MLX Framework](https://github.com/ml-explore/mlx) - Core MLX framework
- [MLX Documentation](https://github.com/ml-explore/mlx/tree/main/docs) - Complete MLX docs
- [MLX Quickstart](https://github.com/ml-explore/mlx?tab=readme-ov-file#quickstart) - Getting started with MLX

## Contributing

Please follow the established design standards and file organization principles outlined in the documentation.

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) (https://opensource.org/license/mit)

## 📚 Documentation

- [Complete Documentation](MLX_CHAT_DOCUMENTATION.md)
- [Word Cloud Workflow](WORDCLOUD_TO_LORA_WORKFLOW.md)
- [Design Standards](DARK_MODE_DESIGN_STANDARDS.md)
- [Project Structure](PROJECT_STRUCTURE.md)
- [CSS Troubleshooting](CSS_TROUBLESHOOTING.md)
- [MLX Framework](https://github.com/ml-explore/mlx) - Core MLX framework
- [MLX Documentation](https://github.com/ml-explore/mlx/tree/main/docs) - Complete MLX docs
- [MLX Quickstart](https://github.com/ml-explore/mlx?tab=readme-ov-file#quickstart) - Getting started with MLX

## Contributing

Please follow the established design standards and file organization principles outlined in the documentation.

## License

[License information to be added]

## 📚 Third-Party Dependencies

### Core Frameworks
- **[MLX](https://github.com/ml-explore/mlx)** - Apple's machine learning framework for Apple Silicon
- **[MLX-LM](https://github.com/ml-explore/mlx-examples/tree/main/llms)** - Language model support for MLX
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework for the chat interface
- **[Anaconda/Miniconda](https://www.anaconda.com/)** - Python environment management

### Text Processing
- **[NLTK](https://www.nltk.org/)** - Natural Language Toolkit for linguistic analysis
- **[python-docx](https://python-docx.readthedocs.io/)** - Microsoft Word document processing

### Web Technologies
- **[Bootstrap](https://getbootstrap.com/)** - CSS framework for responsive design
- **[Bootstrap Icons](https://icons.getbootstrap.com/)** - Icon library for UI elements
- **[Vis.js](https://visjs.org/)** - Network visualization for word relationships

### Data Processing
- **[NumPy](https://numpy.org/)** - Numerical computing library
- **[Matplotlib](https://matplotlib.org/)** - Plotting and visualization

### Model Sources
- **[Hugging Face](https://huggingface.co/)** - Model repository and MLX-compatible models
- **[MLX Community](https://huggingface.co/mlx-community)** - Pre-converted MLX models

### Development Tools
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD pipeline for testing
