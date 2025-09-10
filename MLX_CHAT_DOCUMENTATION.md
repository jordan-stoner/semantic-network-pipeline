## DESIGN STANDARDS & VISUAL CONSISTENCY

### Dark Mode Architecture
All MLX Chat interfaces follow strict dark mode design principles:

**Color Hierarchy:**
- **Primary Background**: `--obsidian-black` (#0a0a0a) - Body/page background
- **Secondary Background**: `--deep-charcoal` (#1a1a1a) - Main containers
- **Tertiary Background**: `--volcanic-ash` (#2a2a2a) - Content areas, cards
- **Text Color**: `--smoke-white` (#f5f5f5) - Primary text
- **Secondary Text**: `--ash-gray` (#4a4a4a) - Muted text

**Magma Accent Colors:**
- **Primary Accent**: `--molten-orange` (#ff6b35)
- **Secondary Accent**: `--ember-red` (#ff4500)
- **Tertiary Accent**: `--lava-yellow` (#ffaa44)
- **Supporting**: `--warm-amber` (#ff8c42)
- **Subtle**: `--copper-glow` (#d2691e)

### Icon Standards
- **Bootstrap Icons Only**: No emoji allowed in any interface
- **CDN**: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css`
- **Automatic Spacing**: All `.bi` icons have 10px right margin via CSS
- **Common Icons**: `bi-bar-chart-fill`, `bi-graph-up`, `bi-cursor-fill`, `bi-play-fill`

### File Management Standards
- **No Duplicate Files**: Never create versioned files (`_v2`, `_enhanced`, `_final`)
- **Single Source**: One canonical version of each file
- **Overwrite Policy**: Update existing files instead of creating new versions
- **CSS Variables**: Always use `var(--color-name)` instead of hex codes

### Component Consistency
- **Containers**: `--deep-charcoal` background with rounded corners
- **Content Areas**: `--volcanic-ash` background for distinction
- **Interactive Elements**: Magma colors with hover effects
- **Text Hierarchy**: `--smoke-white` for primary, `--ash-gray` for secondary

## MLX Fine-Tuning Guide

### Fine-Tuning for Writing Styles & Trigger Phrases

#### Overview
MLX supports fine-tuning models to adopt specific writing styles or respond to trigger phrases using LoRA (Low-Rank Adaptation) for efficient training.

#### Prerequisites
```bash
pip install mlx-lm datasets
```

#### Data Preparation

**Dual Training Approach:**
The MLX Chat system supports two complementary training data types:

**1. Vocabulary Training Data:**
```json
{"text": "analyze the data effectively"}
```
- **Purpose**: Train on specific vocabulary usage patterns
- **Method**: Token contexts around key words (4-6 tokens)
- **POS-aware allocation**: Different token counts based on word type
- **Best for**: Domain-specific terminology, word usage patterns

**2. Style Training Data:**
```json
{"text": "The data revealed fascinating patterns, each number telling its own story in the grand narrative of discovery. Through careful analysis, we uncovered trends that would reshape our understanding."}
```
- **Purpose**: Train on writing style, rhythm, sentence structure
- **Method**: Complete sentences/paragraphs (up to 1500 characters)
- **Preserves flow**: Maintains natural writing patterns
- **Best for**: Writing style, tone, genre characteristics

**Generation Process:**
```bash
python create_wordcloud.py model/training_data/
# Choose option 3 for both training types
# Generates: vocabulary_training.jsonl + style_training.jsonl
```

#### Fine-Tuning Process

**1. Generate Training Data:**
```bash
python create_wordcloud.py model/training_data/
# Select option 3 for both vocabulary and style training
```

**2. Sequential Training (Recommended):**
```bash
# First: Train on vocabulary patterns
python -m mlx_lm.lora \
    --model ./base_model \
    --train \
    --data ./vocabulary_training.jsonl \
    --iters 500 \
    --learning-rate 1e-4 \
    --lora-layers 8 \
    --batch-size 4 \
    --adapter-path ./vocab_adapter

# Second: Train on writing style using vocabulary-trained model
python -m mlx_lm.lora \
    --model ./base_model \
    --adapter-path ./vocab_adapter \
    --train \
    --data ./style_training.jsonl \
    --iters 1000 \
    --learning-rate 1e-5 \
    --lora-layers 16 \
    --batch-size 2 \
    --adapter-path ./final_adapter
```

**3. Alternative: Single Training Type:**
```bash
# Vocabulary only
python -m mlx_lm.lora --model ./base_model --data ./vocabulary_training.jsonl --train

# Style only  
python -m mlx_lm.lora --model ./base_model --data ./style_training.jsonl --train
```

**3. Test the Fine-Tuned Model:**
```bash
python -m mlx_lm.generate \
    --model ./base_model \
    --adapter-path ./style_adapter \
    --prompt "Explain artificial intelligence" \
    --max-tokens 100
```

#### Integration with MLX Chat

**Update `web_chat.py` to load custom adapter:**
```python
# Add to model loading section
if os.path.exists("./custom_adapters/style_adapter"):
    model, tokenizer = load_model_and_tokenizer(
        model_path, 
        adapter_path="./custom_adapters/style_adapter"
    )
```

#### Training Tips

**Writing Style Fine-Tuning:**
- Use 50-200 high-quality examples
- Focus on consistent voice, tone, vocabulary
- Include varied topics to prevent overfitting
- Train for 500-1500 iterations

**Trigger Phrase Training:**
- Use clear, consistent trigger formats
- Include both trigger and non-trigger examples
- Test with variations of trigger phrases
- Monitor for trigger phrase bleeding into normal responses

**Quality Control:**
- Validate on held-out test set
- Check for catastrophic forgetting of base capabilities
- Test edge cases and prompt variations
- Monitor response coherence and relevance

#### Common Issues & Solutions

**Overfitting:**
- Reduce iterations or learning rate
- Add more diverse training examples
- Use larger LoRA rank (--lora-layers)

**Trigger Phrase Not Working:**
- Ensure consistent formatting in training data
- Increase trigger phrase frequency in dataset
- Check tokenization of trigger phrases

**Style Not Consistent:**
- Add more examples of target style
- Ensure training examples are high quality
- Consider multi-stage training approach

#### File Locations
- **Base Models**: `./models/`
- **Training Data**: `./training_data/`
- **Custom Adapters**: `./custom_adapters/`
- **Fine-Tuning Scripts**: `./scripts/finetune/`

# MLX Chat Application Documentation

## AI Assistant Workflow & Performance Guide

### Documentation Usage Protocol
1. **ALWAYS READ DOCS FIRST**: Before searching files, check this documentation for known locations
2. **UPDATE DOCS IMMEDIATELY**: When discovering new file locations or patterns, update this documentation
3. **USE FILE INDEX**: Reference the file index below for immediate location lookup
4. **IMPROVE PERFORMANCE**: Add any information that would speed up future problem-solving

### File Index & Quick Reference

#### Styling & UI Issues
- **Font Problems**: `/Volumes/Media/AI/q/static/css/custom-framework.css` (line 11 - main font-family)
- **Color/Theme Issues**: `/Volumes/Media/AI/q/static/css/magma-theme.css` (CSS variables in :root)
- **Layout Problems**: `/Volumes/Media/AI/q/templates/chat.html` (HTML structure)
- **Navbar Layout**: `/Volumes/Media/AI/q/static/css/custom-framework.css` (.container-fluid class - flexbox properties)
- **Button Styling**: `/Volumes/Media/AI/q/static/css/magma-theme.css` (search for .btn-)
- **Loading Screen**: `/Volumes/Media/AI/q/static/css/magma-theme.css` (.loading-overlay, .loading-icon)

#### Backend & Logic Issues
- **Flask Routes**: `/Volumes/Media/AI/q/web_chat.py` (all API endpoints)
- **MLX Integration**: `/Volumes/Media/AI/q/web_chat.py` (model loading, generation functions)
- **System Prompt**: `/Volumes/Media/AI/q/system_prompt.txt`
- **Parameter Defaults**: `/Volumes/Media/AI/q/slider_preferences.json`

#### Launch & Configuration
- **Primary Launcher**: `/Volumes/Media/AI/q/Launch MLX Chat.command`
- **Main Application**: `/Volumes/Media/AI/q/web_chat.py`

#### JavaScript & Client Logic
- **All JS Code**: Embedded in `/Volumes/Media/AI/q/templates/chat.html` (bottom of file)
- **Event Handlers**: Search for `addEventListener` in chat.html
- **AJAX Calls**: Search for `fetch(` in chat.html

### Code Elegance Principles
**Always strive for clean, elegant, simple code reduced to its minimal state through:**

- **Reusable Styles**: Use existing utility classes instead of creating new CSS rules
- **Pattern Consistency**: Match existing patterns rather than inventing new approaches  
- **Minimal Footprint**: Solve problems with the least amount of code possible
- **Class Reuse**: Leverage the framework's utility classes (me-1, d-flex, gap-2, etc.)
- **Avoid Duplication**: Don't create custom CSS when existing classes solve the problem
- **Systematic Fixes**: Address root causes, not symptoms

**Before Adding New Code, Ask:**
- Does an existing utility class solve this?
- Can I match an existing pattern?
- What's the minimal change needed?
- Am I fixing the cause or just the symptom?

### Systematic UI Debugging Approach
**When buttons or elements appear different from others:**

1. **Compare HTML Structure**: Check if elements use the same classes and container structure
2. **Identify Parent Containers**: Look for differences in parent div classes (d-flex, gap-*, etc.)
3. **Check Utility Classes**: Verify spacing classes (me-1, me-2, mt-*, etc.) are consistent
4. **Avoid Inline CSS**: Fix issues by matching existing patterns, not adding new CSS rules
5. **Root Cause Analysis**: Find why elements differ rather than overriding with new styles

**Common UI Inconsistency Patterns:**
- **Missing spacing classes**: Icons without `me-1` class appear cramped
- **Container differences**: Elements in `d-flex` vs regular containers behave differently  
- **Class mismatches**: Same-purpose elements using different class combinations
- **Parent style inheritance**: Flex containers affecting child element alignment

**Debugging Checklist:**
- Compare working vs broken element HTML structure
- Check for missing utility classes (spacing, alignment)
- Verify parent container classes match
- Look for CSS specificity conflicts
- Test minimal changes before adding new CSS rules

### Common Problem → File Mapping
- **Font inconsistencies** → `custom-framework.css` line 11
- **Color not matching theme** → `magma-theme.css` :root variables
- **Button not styled correctly** → `magma-theme.css` .btn- classes
- **Input width/layout issues** → `custom-framework.css` .col-auto class (for button sizing)
- **Input centering issues** → `magma-theme.css` .input-section .container-fluid (parent container controls centering)
- **Slider numbers not updating on load** → `chat.html` loadPreferences function (element ID mismatch)
- **Parameter not saving** → `web_chat.py` /save_preferences route
- **Generation not working** → `web_chat.py` /generate route
- **Memory issues** → `web_chat.py` MLX memory management functions
- **UI not responsive** → `chat.html` Bootstrap classes or `custom-framework.css`
- **Loading screen problems** → `magma-theme.css` .loading- classes

### JavaScript Element ID Patterns
- **Slider Elements**: `creativitySlider`, `diversitySlider`, `focusSlider`, `repetitionSlider`
- **Number Display Elements**: `creativityValueNum`, `diversityValueNum`, `focusValueNum`, `repetitionValueNum`
- **Label Display Elements**: `creativityValue`, `diversityValue`, `focusValue`, `repetitionValue`

### Slider Preference System Architecture
**Critical Dependencies for Preference Persistence:**

1. **JavaScript Functions** (in `chat.html`):
   - `loadPreferences()`: Fetches saved values and updates both sliders AND number displays
   - `savePreferences()`: Sends current slider values to backend via `/save_preferences`
   - Event listeners: Must be attached to correct slider IDs to trigger saving

2. **Backend Integration** (in `web_chat.py`):
   - `/get_preferences` route: Returns saved values from `slider_preferences.json`
   - `/save_preferences` route: Writes current values to `slider_preferences.json`

3. **Common Failure Points**:
   - **Element ID Mismatches**: JavaScript functions using wrong element IDs
   - **Missing Event Listeners**: Sliders not connected to savePreferences function
   - **Backend Route Issues**: Preferences not being saved/loaded from JSON file

### Layout Structure Discoveries
- **Input Section Hierarchy**: `input-section` → `container-fluid` → `row justify-content-center` → `col-12 col-lg-8` → `row g-2` → `col` (textarea) + `col-auto` (button)
- **Centering Control**: The `container-fluid` level controls overall centering, not the inner `row` elements
- **Width Constraints**: The `col-12 col-lg-8` wrapper limits maximum width, so centering must happen at `container-fluid` level

### Documentation Maintenance Rules
- **Add new file locations** when discovered
- **Update problem mappings** when solving issues
- **Include line numbers** for specific fixes
- **Note patterns** that speed up debugging
- **Keep index current** with any file structure changes

This index should eliminate file hunting and enable immediate problem location identification.

## Project Context for AI Assistant

### What This Project Is
A production-ready web-based chat interface for local LLM interaction using Apple's MLX framework. Built collaboratively between user and AI assistant as a comprehensive example of MLX integration with modern web UI.

### Project Goals & Purpose
1. **Local LLM Inference**: Complete local chat interface without cloud dependencies
2. **MLX Performance Optimization**: Leverage Apple's MLX framework for maximum Apple Silicon performance  
3. **Production Quality**: Robust, daily-use application with professional UI/UX
4. **Educational Reference**: Comprehensive MLX integration example for learning
5. **Extensible Foundation**: Base for additional features and model support

### Design Philosophy & Architecture
- **Performance-First**: MLX optimization using documented best practices
- **Layered Architecture**: Clean separation of UI, Flask backend, MLX integration, model management
- **User Experience Priority**: Intuitive interface with responsive design
- **Comprehensive Documentation**: Enable seamless project handoff between chat sessions
- **Modular Design**: Components can be modified/extended independently

### Key Integration Points
- **MLX Framework**: Direct integration with Apple's MLX for inference and memory management
- **Flask Backend**: RESTful API with streaming response support
- **Modern Web UI**: Bootstrap-based responsive interface with custom Magma theme
- **Model Management**: Local model loading, parameter control, conversation persistence

### Development Context
This is an ongoing collaborative project. When starting new chat sessions, reference this documentation to understand project scope, architecture, and current implementation status without requiring re-explanation of project fundamentals.

**CRITICAL CONSTRAINT**: All project files must remain within `/Volumes/Media/AI/q/` folder. No files should be created or modified outside this directory.

## MLX Documentation References

### Local MLX Documentation Path
**Primary Reference**: [MLX Documentation](https://github.com/ml-explore/mlx/tree/main/docs)

### Key MLX Documentation Files
- **Installation & Setup**: [MLX Installation](https://github.com/ml-explore/mlx/tree/main/docs)
- **Quick Start Guide**: [MLX Quickstart](https://github.com/ml-explore/mlx?tab=readme-ov-file#quickstart)
- **Memory Management**: [MLX Memory](https://github.com/ml-explore/mlx/tree/main/docs)
- **Compilation & Performance**: [MLX Performance](https://github.com/ml-explore/mlx/tree/main/docs)
- **Function Transforms**: [MLX Transforms](https://github.com/ml-explore/mlx/tree/main/docs)
- **MLX Operations**: [MLX Operations](https://github.com/ml-explore/mlx/tree/main/docs)
- **Array Operations**: [MLX Arrays](https://github.com/ml-explore/mlx/tree/main/docs)
- **Random Number Generation**: [MLX Random](https://github.com/ml-explore/mlx/tree/main/docs)

### MLX Implementation References Used in Project
- **Core MLX Functions**: [MLX Core](https://github.com/ml-explore/mlx)
- **Memory Management**: [MLX Memory](https://github.com/ml-explore/mlx)
- **Compilation**: [MLX Compilation](https://github.com/ml-explore/mlx)
- **Python Bindings**: [MLX Python](https://github.com/ml-explore/mlx)
- **Examples**: [MLX Examples](https://github.com/ml-explore/mlx/tree/main/examples)

### MLX Best Practices Applied
Based on [MLX documentation](https://github.com/ml-explore/mlx/tree/main/docs):
- Memory allocation strategies (80% system memory limit)
- JIT compilation enablement for performance
- 4-bit quantization for memory efficiency
- Proper cache management and clearing
- Stream-based generation for responsiveness

**Note**: When implementing MLX features, always reference the local documentation first for the most current implementation details and best practices.

## System Requirements
- **Environment**: Conda environment named "mlx-qwa"
- **Model Path**: `/Volumes/Media/AI/LLM Studio/mg/mg_fused_model`
- **Python Framework**: Flask web server with MLX backend
- **Browser**: Default browser (auto-launched)

### MLX Dependencies
```python
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler, make_repetition_penalty
import mlx.core as mx
from mlx.core.fast import rope, scaled_dot_product_attention, rms_norm
```

Key MLX functions used:
- `mx.set_memory_limit()`: System memory allocation control
- `mx.set_cache_limit()`: MLX cache size management  
- `mx.enable_compile()`: JIT compilation enablement
- `mx.quantize()`: 4-bit weight quantization
- `mx.clear_cache()`: Manual cache clearing
- `mx.get_active_memory()`: Real-time memory monitoring
- `mx.random.seed()`: Reproducible generation control

## System Integration & Component Architecture

### How Components Fit Together

#### 1. Application Launch Flow
```
Launch MLX Chat.command → Conda Environment Activation → Flask Server Start → MLX Model Loading → Browser Launch → UI Ready
```

#### 2. Request Processing Flow
```
User Input → Flask Route → MLX Sampler Creation → Stream Generation → WebSocket Response → UI Update
```

#### 3. Memory Management Integration
```
MLX Memory Limits → Dynamic Cache Monitoring → Automatic Cache Clearing → Memory Status Updates → UI Indicators
```

#### 4. Parameter Control Flow
```
UI Sliders → JavaScript Events → Flask API → MLX Sampler Parameters → Real-time Generation Changes
```

### Core Integration Points

#### MLX ↔ Flask Integration
- **Model Loading**: MLX model loaded once at startup, shared across requests
- **Parameter Passing**: UI parameters directly passed to `mlx_lm.sample_utils.make_sampler()`
- **Memory Monitoring**: Real-time MLX memory usage via `mx.get_active_memory()`
- **Stream Generation**: MLX `stream_generate()` yields tokens to Flask streaming response

#### Flask ↔ Frontend Integration
- **RESTful API**: Standard HTTP endpoints for model status, preferences, memory
- **WebSocket Streaming**: Real-time token streaming for responsive chat experience
- **State Management**: Server-side conversation history with client-side UI updates
- **Error Handling**: Graceful error propagation from MLX through Flask to UI

#### UI Component Integration
- **Bootstrap Framework**: Responsive grid system and component library
- **Custom Magma Theme**: Consistent color palette and component styling
- **JavaScript Event System**: Real-time parameter updates and streaming response handling
- **Local Storage**: Conversation persistence and preference management

### Data Flow Architecture

#### Conversation Management
1. **Input Processing**: User message → Flask → MLX tokenization
2. **Context Building**: Previous messages + system prompt → MLX context
3. **Generation**: MLX streaming generation → Flask → WebSocket → UI
4. **Persistence**: Conversation saved to browser localStorage + server memory

#### Parameter Management
1. **UI Changes**: Slider movement → JavaScript event → AJAX request
2. **Server Update**: Flask receives parameters → Validates → Saves to JSON
3. **MLX Integration**: Next generation uses updated parameters in sampler
4. **Persistence**: Parameters saved to `slider_preferences.json`

#### Memory Management
1. **Monitoring**: Periodic checks of `mx.get_active_memory()`
2. **Threshold Detection**: >8GB triggers automatic cache clearing
3. **UI Updates**: Memory status displayed in navbar
4. **Manual Control**: User can trigger cache clearing via UI button

This integrated architecture ensures all components work together seamlessly while maintaining clear separation of concerns and enabling independent modification of each layer.

## Application Architecture

### Core Files
- **`web_chat.py`**: Main Flask application with MLX integration
- **`Launch MLX Chat.command`**: Primary launcher script (macOS executable)

- **`system_prompt.txt`**: System prompt configuration
- **`slider_preferences.json`**: Persistent UI parameter settings

### Web Interface
- **`templates/chat.html`**: Main chat interface template
- **`static/css/magma-theme.css`**: Custom Magma color theme
- **`static/css/bootstrap.min.css`**: Bootstrap framework
- **`static/js/bootstrap.bundle.min.js`**: Bootstrap JavaScript

## Launch Methods

### Method 1: Configuration Launch (Recommended)
**Double-click launcher with full configuration**
```bash
# Double-click: Launch MLX Chat.command
# OR from terminal:
python config_launcher.py  # Auto-activates mlx-qwa environment
```

**Features:**
- **Environment Auto-Setup**: Creates `mlx-qwa` conda environment if missing
- **Dependency Management**: Installs all packages from `requirements.txt`
- **Model Discovery**: Auto-detects MLX models in common directories
- **LoRA Integration**: Scans and loads available LoRA adapters
- **Visual Configuration**: Magma-themed selection interface (port 5001)
- **Auto-Launch**: Starts main chat interface (port 5000) after configuration

**Workflow:**
1. **Environment Check** - Detects/creates `mlx-qwa` environment
2. **Configuration Page** - Opens at `http://127.0.0.1:5001`
3. **Model Selection** - Choose from discovered MLX models
4. **LoRA Selection** - Optional adapter loading
5. **Launch Chat** - Starts main interface at `http://127.0.0.1:5000`

### Method 2: Direct Launch (Skip Configuration)
```bash
conda activate mlx-qwa
python web_chat.py
```
- Uses default model without configuration
- Bypasses model/LoRA selection
- Fast startup for development

### Method 3: Manual Launch
```bash
conda activate mlx-qwa
python web_chat.py
```
- Reads configuration from `chat_config.json` if available
- Falls back to default model if no configuration exists

## MLX Framework Integration

### Core MLX Performance Optimizations
```python
# Memory limits (configured for 16GB system)
mx.set_memory_limit(int(0.8 * 16 * 1024**3))  # 80% of 16GB
mx.set_cache_limit(2 * 1024 * 1024 * 1024)    # 2GB cache limit
mx.enable_compile()                            # Enable JIT compilation
```

### Model Parameters (MLX Sampler Integration)
Parameters are passed directly to MLX's `make_sampler()` function:

- **Temperature (Creativity)**: 0.1-1.0 (default: 0.7)
  - Controls response randomness via `temp=temperature` in sampler
- **Top-P (Diversity)**: 0.5-1.0 (default: 0.9)
  - Nucleus sampling threshold via `top_p=top_p` in sampler
- **Top-K (Focus)**: 10-100 (default: 50)
  - Limits vocabulary consideration via `top_k=top_k` in sampler
- **Repetition Penalty**: 1.0-1.3 (default: 1.1)
  - Uses `make_repetition_penalty(repetition_penalty, context_size=100)`
- **Max Tokens**: Configurable response length limit

### MLX Sampling Implementation
```python
# Create sampler with user parameters
sampler = make_sampler(
    temp=temperature,
    top_p=top_p,
    top_k=top_k,
    min_p=0.0
)

# Create repetition penalty processor
logits_processors = []
if repetition_penalty > 1.0:
    logits_processors.append(
        make_repetition_penalty(repetition_penalty, context_size=100)
    )

# Stream generation with MLX
for response in stream_generate(
    model, 
    tokenizer, 
    prompt=prompt, 
    max_tokens=max_tokens,
    sampler=sampler,
    logits_processors=logits_processors
):
```

### Memory Management & Quantization
- **4-bit Quantization**: Automatic weight quantization for memory efficiency
  ```python
  # Quantize weights with group size 64, 4-bit precision
  w_q, scales, biases = mx.quantize(param, group_size=64, bits=4)
  ```
- **Dynamic Cache Management**: Automatic MLX memory cache clearing when >8GB
- **Memory Monitoring**: Real-time usage via `mx.get_active_memory()`
- **KV Cache**: Custom conversation context caching (4096 token limit)

## User Interface Features

### Magma Theme Color Palette
```css
:root {
    /* Basic Unit - Standard height for buttons and inputs */
    --basicUnit: 40px;
    
    /* Primary Colors - Magma Core */
    --obsidian-black: #0a0a0a     /* Primary background */
    --deep-charcoal: #1a1a1a      /* Secondary background */
    --volcanic-ash: #2a2a2a       /* Tertiary background */
    --molten-orange: #ff6b35      /* Primary accent */
    --ember-red: #ff4500          /* Secondary accent */
    --lava-yellow: #ffaa44        /* Tertiary accent */
    --warm-amber: #ff8c42         /* Supporting color */
    --copper-glow: #d2691e        /* Border accent */
    --ash-gray: #4a4a4a           /* Neutral tone */
    --smoke-white: #f5f5f5        /* Text color */
}
```

**Design System Variables:**
- **--basicUnit (40px)**: Standard height for all buttons and minimum height for inputs
  - Ensures consistent sizing across UI elements
  - Can be adjusted globally by changing this single value
  - Applied to: all buttons, textarea min-height, form controls

### UI Components
- **Fixed Navbar**: Model status, memory usage, seed display, settings
- **Message Bubbles**: Distinct styling for user/assistant messages
- **Settings Sidebar**: Slide-out parameter controls
- **Loading Animation**: Magma-themed loading screen with pulse effect
- **Action Buttons**: Regenerate, delete, stop generation, edit options

### Interactive Features
- **Message Management**: Delete last message, regenerate responses
- **Conversation Persistence**: Automatic history loading/saving
- **Context Summarization**: Intelligent context compression for long conversations
- **Real-time Generation**: Streaming response display with stop capability
- **Parameter Persistence**: Settings saved between sessions

## Advanced Text Analysis Features

### Enhanced Wordcloud Generation
The `create_wordcloud.py` script now includes comprehensive linguistic analysis:

**NLTK-Based Analysis:**
- **POS Tagging**: Identifies parts of speech for each word
- **Lemmatization**: Reduces words to their base dictionary form
- **Stemming**: Reduces words to their root form using Porter Stemmer
- **Collocation Detection**: Finds frequently co-occurring word pairs
- **Frequency Distribution**: Statistical analysis of word usage patterns

**Dual Visualization System:**
- **Traditional Word Cloud**: Frequency-based sizing with magma color scheme
- **Interactive Bubble Chart**: Chart.js visualization with:
  - Circular positioning based on word relationships
  - Bubble size proportional to frequency
  - Rich tooltips showing linguistic data (POS, lemma, stem, collocations)
  - Magma color gradient from molten-orange to copper-glow

**Generated Output:**
- **HTML File**: Complete visualization with embedded Chart.js
- **Linguistic Statistics**: Comprehensive analysis summary
- **Training Data**: Optional vocabulary and style training datasets

## Advanced Features

### MLX-Specific Performance Tuning
Based on MLX documentation best practices:

1. **Memory Allocation Strategy**:
   - 80% system memory allocation prevents OOM crashes
   - 2GB cache limit balances performance vs memory usage
   - Dynamic cache clearing when memory >8GB active

2. **Compilation Optimization**:
   - `mx.enable_compile()` enables JIT compilation for 2-3x speedup
   - Automatic graph optimization for repeated operations
   - Metal Performance Shaders integration on Apple Silicon

3. **Quantization Strategy**:
   - 4-bit quantization with group size 64 for optimal quality/memory balance
   - Only quantizes weight matrices >64 parameters
   - Preserves model accuracy while reducing memory by ~75%

4. **Sampling Parameter Integration**:
   - Direct integration with `mlx_lm.sample_utils.make_sampler()`
   - Real-time parameter adjustment without model reload
   - Advanced repetition penalty with configurable context window

### Conversation Management
- **History Persistence**: Conversations saved and restored on reload
- **Context Summarization**: Automatic summarization when >100 messages
- **Message Deletion**: Remove last message with cascade handling
- **Regeneration**: Re-generate responses with new randomization

### Performance Optimizations
- **Memory Limits**: 80% of 16GB RAM allocation
- **Cache Limits**: 2GB MLX cache limit
- **Compilation**: MLX compilation enabled for performance
- **Quantization**: Automatic 4-bit weight quantization
- **Repetition Detection**: Advanced repetition analysis and stopping

### System Integration
- **Conda Environment**: Automatic environment activation
- **Browser Integration**: Auto-launch default browser with specific URL
- **Process Management**: Clean shutdown and process handling
- **Error Recovery**: Comprehensive error handling and user feedback

## Configuration Files

### System Prompt (`system_prompt.txt`)
```
You are an expert creative writing assistant specializing in collaborative storytelling...
```
- Defines AI personality and behavior
- Focuses on creative writing and storytelling
- Includes response style guidelines

### Preferences (`slider_preferences.json`)
```json
{
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.1,
    "max_tokens": 1024
}
```

## API Endpoints

### Core Endpoints
- `GET /`: Main chat interface
- `POST /generate`: Stream text generation
- `GET /status`: Model loading status and current seed
- `POST /shutdown`: Graceful application shutdown

### Management Endpoints
- `GET /memory_status`: Current memory usage statistics
- `POST /clear_cache`: Manual memory cache clearing
- `POST /randomize_seed`: Generate new random seed
- `POST /delete_last_message`: Remove last conversation message

### Preferences Endpoints
- `GET /get_preferences`: Load saved parameter settings
- `POST /save_preferences`: Persist parameter changes
- `GET /get_history`: Load conversation history

## Troubleshooting

### Common Issues
1. **Model Loading Failure**: Check model path and conda environment
2. **Memory Issues**: Use clear cache button or restart application
3. **Generation Stuck**: Use stop button and try regeneration
4. **Browser Issues**: Works with any modern browser

### MLX-Specific Issues
1. **Out of Memory (OOM)**:
   - Reduce memory limit: `mx.set_memory_limit(int(0.6 * 16 * 1024**3))`
   - Clear cache more frequently: Lower threshold from 8GB to 6GB
   - Enable more aggressive quantization

2. **Slow Generation**:
   - Ensure `mx.enable_compile()` is called
   - Check Metal GPU availability: `mx.metal.is_available()`
   - Verify model quantization completed successfully

3. **Parameter Changes Not Applied**:
   - Parameters passed directly to `make_sampler()` each generation
   - Check slider event listeners are properly bound
   - Verify preferences are saved to `slider_preferences.json`

4. **Memory Leaks**:
   - MLX automatically manages memory, but long conversations may accumulate
   - Use conversation summarization (triggers at >100 messages)
   - Manual cache clearing via `/clear_cache` endpoint

### Performance Tips
- Monitor memory usage via navbar indicator
- Clear cache when memory >8GB
- Use stop button for unwanted long responses
- Adjust max_tokens for shorter responses

## Development Notes

### Code Structure
- **Flask Backend**: RESTful API with streaming responses
- **MLX Integration**: Direct model loading and generation
- **Bootstrap Frontend**: Responsive design with custom theming
- **JavaScript**: Event-driven UI with async/await patterns

### Customization Points
- **System Prompt**: Modify `system_prompt.txt` for different AI personalities
- **Theme Colors**: Adjust CSS variables in `magma-theme.css`
- **Model Path**: Update path in `web_chat.py` for different models
- **Parameters**: Modify default ranges in slider configurations

## User Interface Architecture

### Page Structure & Layout
```html
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <!-- Bootstrap Icons + Custom Framework + Magma Theme -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link href="{{ url_for('static', filename='css/custom-framework.css') }}">
    <link href="{{ url_for('static', filename='css/magma-theme.css') }}?v=2">
</head>
```

### CSS Architecture
- **`custom-framework.css`**: Minimal CSS framework replacing Bootstrap
  - Layout system (container-fluid, row, col-*)
  - Flexbox utilities (d-flex, align-items-center, etc.)
  - Spacing utilities (mb-3, me-2, p-3, etc.)
  - Typography and form controls
  - Base button styles
- **`magma-theme.css`**: Custom theme and component styling
  - Color palette and CSS variables
  - Button system (btn-icon, btn-text, btn-red)
  - Chat interface styling
  - Loading animations

### Container Hierarchy
1. **Fixed Navbar** (60px height)
2. **Chat Container** (`calc(100vh - 60px)` height)
3. **Fixed Footer Input** (auto height, bottom-positioned)
4. **Settings Sidebar** (300px width, slide-out)
5. **Loading Overlay** (fullscreen, dismissible)

### Loading Screen Implementation
```css
.loading-overlay {
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    width: 100vw !important; height: 100vh !important;
    z-index: 9999 !important;
    background: rgba(0,0,0,0.9);
    cursor: pointer;
}

.loading-icon {
    width: 80px; height: 80px;
    border-radius: 50%;
    background: linear-gradient(45deg, #ff6b35, #ff4500);
    box-shadow: 0 0 40px rgba(255,107,53,0.3), 0 0 80px rgba(255,107,53,0.1);
    animation: loadingPulse 5s ease-in-out infinite;
}

@keyframes loadingPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.3); }
}
```

**Loading Screen Behavior:**
- Displays on page load until model status returns `model_loaded: true`
- Clickable to dismiss manually (`onclick="hideLoadingScreen()"`)
- Auto-hides after 10-second fallback timeout
- Disables input controls until dismissed

### Chat Container Layout
```css
.chat-container {
    height: calc(100vh - 140px) !important;
    overflow: hidden !important;
    width: 100vw !important;
    max-width: none !important;
    display: flex !important;
    flex-direction: column !important;
}

.messages-container {
    height: 100% !important;
    width: 100% !important;
    overflow-y: scroll !important;
    overflow-x: hidden !important;
    padding: 1rem !important;
    flex: 1 !important;
}
```

### Message Bubble System
```css
.message-bubble {
    max-width: 70%;
    margin-bottom: 1rem;
    white-space: pre-wrap;
    word-wrap: break-word;
    position: relative;
}

.user-message {
    margin-left: auto;
}

.user-message .card {
    background: #404040 !important;
    border: 1px solid #555555 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.assistant-message .card {
    background: linear-gradient(135deg, #1a1a1a, #2a2a2a) !important;
    border: 1px solid #d2691e !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}
```

### Button System Architecture
**Unified Button Styling:**
```css
/* All buttons use consistent magma theme */
.btn-warning, .btn-outline-warning, .btn-send, .btn-regenerate,
.btn-outline-success, .btn-outline-primary, .btn-outline-danger,
.btn-outline-light, .btn-stop {
    background-color: #ff6b35 !important;
    border-color: #ff6b35 !important;
    color: #0a0a0a !important;
    transition: all 0.2s ease !important;
    transform: translateY(0) !important;
}

/* Hover states with lift effect */
.btn-*:hover {
    background-color: #e55a2b !important;
    border-color: #e55a2b !important;
    color: #f5f5f5 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
}
```

**Button Types & Functions:**
- **Send Button**: `btn-send` with `<i class="bi bi-send"></i>`
- **Regenerate**: `btn-regenerate` with `<i class="bi bi-arrow-clockwise"></i>`
- **Stop Generation**: `btn-stop` with `<i class="bi bi-stop-circle"></i>`
- **Delete Message**: `btn delete-btn` with `<i class="bi bi-trash3"></i>`
- **Settings Toggle**: `btn-outline-light` with `<i class="bi bi-gear"></i>`

**Button Sizing:**
- **Icon-only buttons**: Square `40x40px` - navbar buttons (settings, clear cache, randomize, quit) + send button
- **Text buttons**: Rectangular `120x40px` (3:1 ratio) - Continue, Quit, Regenerate, Try Again, Stop, Edit Message
- Input fields use `min-height: var(--basicUnit)` allowing expansion
- Adjusting `--basicUnit` changes all UI element dimensions proportionally

### Settings Sidebar Implementation
```css
.settings-sidebar {
    position: fixed;
    top: 0; right: -300px;
    width: 300px; height: 100vh;
    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
    border-left: 2px solid #ff6b35;
    z-index: 1000;
    transition: right 0.3s ease;
    overflow-y: auto;
}

.settings-sidebar.open {
    right: 0;
}
```

**Slider Controls:**
```html
<div class="mb-3">
    <label for="creativitySlider" class="form-label">
        <i class="bi bi-lightbulb me-1"></i>Creativity (temp): 
        <span id="creativityValueNum">0.7</span>
    </label>
    <input type="range" id="creativitySlider" min="0.1" max="1.0" 
           step="0.1" value="0.7" class="form-range">
    <div class="d-flex justify-content-between">
        <small>Focused</small>
        <span id="creativityValue" class="badge bg-secondary">Balanced</span>
        <small>Creative</small>
    </div>
</div>
```

### Fixed Navbar Components
```html
<nav class="navbar navbar-dark fixed-top" style="background-color: #2c2c2c;">
    <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">
            <i class="bi bi-chat-dots me-2"></i>MLX Chat
        </span>
        <div class="d-flex align-items-center">
            <span class="navbar-text me-3">
                <i class="bi bi-memory me-1"></i><span id="memoryUsage">--</span>
            </span>
            <span class="navbar-text me-3">
                Seed: <span id="currentSeed">Loading...</span>
            </span>
            <!-- Action buttons -->
        </div>
    </div>
</nav>
```

### Input Section Layout
```css
.input-section {
    background: linear-gradient(90deg, #0a0a0a, #1a1a1a) !important;
    border-top: 2px solid #d2691e !important;
    backdrop-filter: blur(10px);
    position: fixed;
    bottom: 0;
    width: 100%;
    padding: 1rem;
}
```

**Textarea Auto-resize:**
```javascript
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 100) + 'px';
});
```

### Dynamic UI Elements

**Typing Indicator:**
```html
<div class="message-bubble assistant-message" id="typing-indicator">
    <div class="card typing-indicator">
        <div class="card-body">
            <i class="bi bi-three-dots"></i> Thinking...
        </div>
    </div>
</div>
```

**Delete Button (Per Message):**
```javascript
const deleteBtn = document.createElement('button');
deleteBtn.className = 'btn delete-btn';
deleteBtn.innerHTML = '<i class="bi bi-trash3" style="font-size: 12px;"></i>';
deleteBtn.style.cssText = `
    position: absolute; top: 8px; right: 8px;
    background: rgba(220, 53, 69, 0.8) !important;
    border: none !important; border-radius: 50% !important;
    width: 24px !important; height: 24px !important;
    padding: 0 !important; opacity: 0.25;
    transition: opacity 0.2s ease; z-index: 10;
`;
```

### Responsive Behavior
- **Chat Container**: Full viewport width, no Bootstrap container constraints
- **Message Bubbles**: 70% max-width, responsive to screen size
- **Input Section**: Full-width with centered content (col-lg-8)
- **Settings Sidebar**: Fixed 300px width, slides over content

### Scrollbar Customization
```css
.messages-container::-webkit-scrollbar {
    width: 8px;
}
.messages-container::-webkit-scrollbar-track {
    background: #1a1a1a;
}
.messages-container::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff6b35, #ff4500);
    border-radius: 4px;
}
```

### JavaScript Event System
- **Model Status Polling**: Checks `/status` endpoint every 1000ms until loaded
- **Memory Monitoring**: Updates `/memory_status` every 10 seconds
- **Auto-scroll**: `messages.scrollTop = messages.scrollHeight` on new messages
- **Settings Persistence**: Auto-saves slider changes to `/save_preferences`
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for newline

This UI architecture provides a complete foundation for rebuilding the interface with all styling, interactions, and responsive behaviors documented.
