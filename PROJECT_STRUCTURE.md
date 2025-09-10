# MLX Chat Project Structure

## Server Architecture

### Launch Process Flow
1. **`Launch MLX Chat.command`** - macOS launcher script
   - Detects and activates `mlx-qwa` conda environment
   - Starts `config_launcher.py` on port 5001
   
2. **`config_launcher.py`** - Configuration server
   - Provides model/LoRA selection interface
   - Launches `web_chat.py` as detached subprocess
   - Shuts down after successful launch
   
3. **`web_chat.py`** - Main chat server
   - Runs independently on port 5000
   - Continues running after config server exits
   - Handles all chat functionality

### Process Independence
- **Detached Subprocess**: `web_chat.py` runs in new session (`start_new_session=True`)
- **No Output Capture**: Uses `subprocess.DEVNULL` to prevent blocking
- **Independent Lifecycle**: Main server survives config server shutdown

### Port Usage
- **Port 5001**: Configuration server (temporary)
- **Port 5000**: Main chat server (persistent)

### CSS Architecture

### File Load Order (Critical)
1. **Bootstrap Icons CSS** - External CDN
2. **`custom-framework.css`** - Framework with `!important` rules
3. **`magma-theme.css`** - Custom theme (loads last)

### CSS Inheritance Issues
- **Message Bubbles**: `.message-bubble` containers create different CSS context
- **Dynamic Content**: JavaScript-created elements may not inherit styles properly
- **Framework Conflicts**: Bootstrap classes (`.me-1`, `.me-2`) override custom styles

### Troubleshooting Methodology
1. **Test CSS Loading**: Add obvious visual changes (red background)
2. **Check Specificity**: Use browser DevTools to inspect computed styles
3. **Verify Element Targeting**: Ensure selectors match actual HTML structure
4. **Consider Context**: Some elements need to be outside message bubbles

## Root Directory Organization

### Core Application Files
- `initial_setup.py` - Environment setup and dependency installation
- `web_chat.py` - Main MLX Chat application (Flask server + MLX integration)
- `config_launcher.py` - Configuration page with model/LoRA selection

- `system_prompt.txt` - Default system prompt for chat

### Data Processing Tools
- `create_wordcloud.py` - Word frequency analysis and visualization
- `create_lora.py` - LoRA training dataset generation
- `fuse_model.py` - Model + LoRA adapter fusion utility

### Launchers & Utilities
- `Launch MLX Chat.command` - macOS double-click launcher with auto-environment setup

### Configuration Files
- `requirements.txt` - Python package dependencies (comprehensive)
- `.gitignore` - Git ignore patterns

### Runtime Files (Generated/Not in Git)
- `chat_config.json` - Runtime configuration (model/adapter selection)
- `slider_preferences.json` - UI preferences storage
- `wordcloud.html` - Generated word cloud visualization
- `model/model/*/` - User-downloaded MLX models (not included)

### Documentation
- `README.md` - Project overview and quick start
- `MLX_CHAT_DOCUMENTATION.md` - Complete application documentation
- `WORDCLOUD_TO_LORA_WORKFLOW.md` - Data processing workflow
- `DARK_MODE_DESIGN_STANDARDS.md` - UI/UX design guidelines
- `PROJECT_STRUCTURE.md` - This file

### Web Assets
```
static/
├── css/
│   ├── magma-theme.css         # Main dark mode theme
│   └── custom-framework.css    # Custom UI framework
├── js/                         # JavaScript files (if any)
└── fonts/                      # Custom fonts (if any)
```

### Templates
```
templates/
├── chat.html                   # Main chat interface template
└── wordcloud_template.html     # Word cloud visualization template
```

### Data & Models
```
model/
├── training_data/              # Source materials for LoRA training (.txt, .docx)
├── lora_training/              # Generated training datasets (.jsonl)
├── lora/                       # MLX training splits (train/valid/test.jsonl)
└── adapters/                   # Organized LoRA adapters by model
    ├── ModelName_lora/         # Model-specific adapter folder
    │   └── ModelName_lora-descriptor_v01.npz
└── training_data/              # Processed training datasets
```

### Generated Files
- `vocabulary_training.jsonl` - Generated vocabulary training data
- `style_training.jsonl` - Generated style training data
- `chat_config.json` - Current model and adapter configuration

## Launch Methods

### Method 1: Initial Setup (Required First Time)
```bash
python initial_setup.py
```

### Method 2: Configuration Launch (Recommended)
- Double-click `Launch MLX Chat.command`
- Activates `mlx-qwa` conda environment
- Opens configuration page for model/adapter selection
- Launches main chat interface with selected configuration

### Method 3: Manual Launch
```bash
conda activate mlx-qwa
python web_chat.py
```

## Environment Management

### Automatic Environment Setup
- **Conda Detection**: Automatically detects or installs Miniconda if needed
- **Environment Creation**: Creates `mlx-qwa` environment with Python 3.10
- **Dependency Installation**: Installs all packages from `requirements.txt`
- **Cross-Platform Support**: Works on macOS and Linux with automatic architecture detection

### Environment Structure
```
mlx-qwa (conda environment)
├── Python 3.10
├── Flask (web framework)
├── MLX + MLX-LM (Apple MLX framework)
├── NLTK (text processing)
├── NumPy, Matplotlib (data processing)
├── WordCloud (visualization)
└── Additional dependencies from requirements.txt
```

## Configuration Workflow

### Model Selection Process
1. **Auto-Discovery**: Scans common MLX model directories
2. **Visual Selection**: Magma-themed configuration interface
3. **Configuration Save**: Stores selection in `chat_config.json`
4. **Model Loading**: web_chat.py reads configuration on startup

### LoRA Adapter Integration
1. **Adapter Discovery**: Scans organized model folders in `model/adapters/`
2. **Optional Selection**: Choose adapter or run with base model
3. **Runtime Loading**: Adapter loaded during model initialization
4. **Seamless Integration**: Works with existing chat interface

## Data Processing Workflow
```bash
# 1. Add source materials
cp source_files.txt model/training_data/

# 2. Generate training data (activate environment first)
conda activate mlx-qwa
python create_wordcloud.py model/training_data/
# Choose option 3 for both vocabulary and style training

# 3. Train LoRA adapter
python create_lora.py

# 4. Use in chat
# Select adapter in configuration page
```

## File Naming Conventions
- **Snake_case** for Python files: `create_wordcloud.py`
- **kebab-case** for CSS/HTML: `magma-theme.css`
- **UPPERCASE** for documentation: `README.md`
- **No versioning suffixes**: Never use `_v2`, `_enhanced`, etc.

## Folder Hierarchy Rules
1. **Root level**: Core application files only
2. **static/**: All web assets (CSS, JS, fonts, images)
3. **templates/**: HTML templates for Flask
4. **model/**: ML models and training data
5. **docs/**: Future documentation folder (if needed)

## Git Repository Preparation
- Remove `.DS_Store` files
- Add `.gitignore` for Python, macOS, and ML files
- Clean up any temporary or generated files
- Ensure all paths are relative, not absolute

## Third-Party Dependencies

### Core Technologies
- **[MLX](https://github.com/ml-explore/mlx)** - Apple's machine learning framework
- **[Flask](https://flask.palletsprojects.com/)** - Web framework for chat interface
- **[Anaconda](https://www.anaconda.com/)** - Python environment management

### Text Processing
- **[NLTK](https://www.nltk.org/)** - Natural Language Toolkit
- **[python-docx](https://python-docx.readthedocs.io/)** - Word document processing
- **[NumPy](https://numpy.org/)** - Numerical computing
- **[Matplotlib](https://matplotlib.org/)** - Data visualization

### Web Technologies
- **[Bootstrap](https://getbootstrap.com/)** - CSS framework
- **[Bootstrap Icons](https://icons.getbootstrap.com/)** - Icon library
- **[Vis.js](https://visjs.org/)** - Network visualization

### Model Sources
- **[Hugging Face](https://huggingface.co/)** - Model repository
- **[MLX Community](https://huggingface.co/mlx-community)** - MLX-compatible models
