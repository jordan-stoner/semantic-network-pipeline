# Word Cloud to LoRA Training Workflow

## SYSTEM OVERVIEW
This workflow analyzes text files to identify distinctive vocabulary, then extracts sentences containing those words to create targeted LoRA training data for MLX fine-tuning.

## WORKFLOW SEQUENCE

### PHASE 1: Text Analysis & Word Cloud Generation
**Script:** `/Volumes/Media/AI/q/create_wordcloud.py`
**Input:** Text files in `/Volumes/Media/AI/q/model/training_data/` (or specified directory)
**Output:** HTML word cloud + optional LoRA training data

#### Step 1.1: Text Processing
- **Read all .txt files** from source directory
- **Tokenize text** using NLTK (with fallback to regex)
- **Apply POS tagging** to identify parts of speech

#### Step 1.2: Multi-Layer Filtering
**Filter 1 - POS Tags:** Keep only descriptive words
- `NN, NNS` (nouns)
- `JJ, JJR, JJS` (adjectives, comparative, superlative)
- `RB, RBR, RBS` (adverbs, comparative, superlative)

**Filter 2 - Length & Format:**
- Minimum 4 characters
- Letters only (no numbers/symbols)
- No proper nouns (capitalized words)

**Filter 3 - Stop Words:** Remove common non-descriptive words
- Standard English stop words (NLTK corpus)
- Time words: time, often, always, today, morning, etc.
- Quantity words: much, many, enough, quite, extremely, etc.
- Direction words: away, back, around, toward, etc.
- Generic verbs: make, take, come, find, think, etc.
- Generic adjectives: good, bad, big, small, old, new, etc.

**Filter 4 - Frequency:** Remove overly common words
- Exclude words appearing in >5% of total word instances
- Focuses on distinctive vocabulary

#### Step 1.3: Word Cloud Generation
- **Count frequencies** of filtered words
- **Perform linguistic analysis** using NLTK:
  - POS tagging and frequency distribution
  - Lemmatization and stemming analysis
  - Sentence-level collocation detection (not just neighboring words)
  - Word relationship mapping
- **Generate interactive visualization**:
  - Vis.js network chart with word relationships and collocations
  - POS filtering with progressive damping physics
  - Zoom controls with min/max limits (disabled mouse zoom/drag)
  - Word bubble functionality (click to hide/show nodes)
  - Details box with proper word counts and connections
  - Template-based HTML generation for maintainability

### PHASE 2: Dual LoRA Training Data Extraction (Optional)
**Triggered:** User chooses 'y' when prompted after word cloud generation
**Options:** Vocabulary training, Style training, or Both

#### Option 1: Vocabulary Training Data
**Purpose:** Train model on specific vocabulary usage patterns
**Method:** Token-based context extraction around key words

**POS-Aware Token Allocation:**
- **Adverbs (RB*)**: 4 preceding + 2 following tokens (need context for meaning)
- **Adjectives (JJ*)**: 2 preceding + 4 following tokens (modify what follows)
- **Nouns (NN*)**: 3 preceding + 3 following tokens (balanced context)
- **Default**: 3 preceding + 3 following tokens
- **Maximum**: 6 total tokens per context

**Output Format (MLX-compatible):**
```json
{"text": "analyze the data effectively"}
```

**Quality Controls:**
- Minimum 4 tokens per context
- Maximum 50 contexts total
- Top 20 most frequent distinctive words
- Filters out contexts that are too short

#### Option 2: Style Training Data
**Purpose:** Train model on writing style, rhythm, and sentence structure
**Method:** Complete sentence/paragraph extraction

**Chunk Parameters:**
- **Maximum size**: 1500 characters (~400 tokens for MLX compatibility)
- **Minimum size**: 100 characters (meaningful content)
- **Maximum chunks**: 100 total
- **Sentence-aware**: Splits on sentence boundaries, preserves natural flow

**Output Format (MLX-compatible):**
```json
{"text": "The data revealed fascinating patterns, each number telling its own story in the grand narrative of discovery. Through careful analysis, we uncovered trends that would reshape our understanding of the underlying processes."}
```

**Quality Controls:**
- Preserves complete sentences
- Maintains natural writing flow
- Respects MLX token limits
- Filters out chunks that are too short

#### Option 3: Both Training Types
**Generates both vocabulary and style training files simultaneously**

**File Outputs:**
- `model/lora_training/vocabulary_training.jsonl` - Token contexts for vocabulary learning
- `model/lora_training/style_training.jsonl` - Complete chunks for style learning

**Training Statistics Provided:**
- Token allocation summary by POS tag
- Average chunk lengths and ranges
- Total contexts/chunks extracted
- File paths for MLX training
**Target:** Top 50 most distinctive words from analysis

#### Step 2.1: Sentence Collection
- **Re-scan all text files** for sentences containing target words
- **Use word boundary matching** (`\b` regex) to avoid partial matches
- **Filter sentence length:** 50+ characters minimum

#### Step 2.2: Smart Chunking (Token Limit Compliance)
**Constraint:** 1500 characters max per chunk (~400 tokens for 2048 token models)

**Chunking Strategy:**
1. **Combine sentences** up to 1500 character limit
2. **Preserve sentence boundaries** - never break mid-sentence
3. **Handle overflow:** If adding sentence exceeds limit, start new chunk
4. **Split long chunks:** Break by sentences if individual chunks too long
5. **Maintain context:** Keep related sentences together when possible

#### Step 2.3: Training Data Generation
- **Shuffle chunks** for randomization
- **Split data:** 80% train, 10% validation, 10% test
- **Output format:** JSONL with `{"text": "chunk_content"}` structure
- **Save location:** `/Volumes/Media/AI/q/model/adapters/ModelName_lora/`

## FILE STRUCTURE
```
/Volumes/Media/AI/q/
├── create_wordcloud.py          # Main analysis script
├── model/
│   ├── lora/                    # Input: Source text files (.txt)
│   └── training_data/           # Output: LoRA training files
│       ├── train.jsonl          # 80% of chunks
│       ├── valid.jsonl          # 10% of chunks
│       └── test.jsonl           # 10% of chunks
└── wordcloud/                   # Generated wordcloud visualizations
    └── wordcloud.html           # Output: Visual analysis
```

## DEPENDENCIES
- **Required:** Python 3.x, pathlib, collections, re, json, random, math
- **Enhanced NLTK Integration:** Advanced linguistic analysis capabilities
  - **Core NLTK**: punkt_tab, averaged_perceptron_tagger_eng, stopwords
  - **Linguistic Analysis**: WordNetLemmatizer, PorterStemmer, BigramCollocationFinder
  - **Fallback**: Graceful degradation to regex-based filtering if NLTK unavailable
  - **Auto-downloads**: All required NLTK corpora and models

## USAGE COMMANDS
```bash
# Basic usage (default directories)
python /Volumes/Media/AI/q/create_wordcloud.py

# Custom source directory
python /Volumes/Media/AI/q/create_wordcloud.py /path/to/text/files

# Custom source and output
python /Volumes/Media/AI/q/create_wordcloud.py /path/to/text/files custom_wordcloud.html
```

## File Organization

```
model/
├── training_data/          # Input: Source materials (.txt, .docx)
├── lora_training/          # Generated: Training datasets (.jsonl)
├── lora/                   # MLX splits: train/valid/test.jsonl
├── wordcloud/              # Generated: Wordcloud visualizations (.html)
└── adapters/               # Output: Final LoRA adapters (.npz)
```

## INTEGRATION WITH MLX LORA TRAINING
**Next Step:** Use generated training data with MLX LoRA

**Automatic Mistral Support:**
The `create_lora.py` script automatically patches the MLX LoRA framework to support Mistral architecture models like MN-Violet-Lotus-12B-MLX.

```bash
# Use MLX LoRA training (install mlx-lm first)
python -m mlx_lm.lora \
    --model microsoft/DialoGPT-medium \
    --data /Volumes/Media/AI/q/model/lora \
    --train --iters 600 --batch-size 2 --lora-layers 8
```

## KEY DESIGN DECISIONS

### Why Multi-Layer Filtering?
- **POS filtering:** Ensures only meaningful descriptive words
- **Stop word removal:** Eliminates grammatical noise
- **Frequency filtering:** Removes generic common words
- **Length filtering:** Focuses on substantial vocabulary

### Why Smart Chunking?
- **Token limits:** MLX models have context length constraints
- **Context preservation:** Keeps related sentences together
- **Sentence integrity:** Never breaks mid-sentence for coherence
- **Training quality:** Maintains natural language flow

### Why Target Word Focus?
- **Style capture:** Sentences with distinctive words carry writing style
- **Efficiency:** Focused dataset trains faster than full corpus
- **Quality over quantity:** Better to train on relevant examples

## ERROR HANDLING
- **Missing NLTK:** Graceful fallback to regex-based processing
- **File conflicts:** Automatic timestamping prevents overwrites
- **Empty results:** Clear error messages for debugging
- **Encoding issues:** UTF-8 handling with error catching

## OUTPUT INTERPRETATION
- **Word cloud:** Visual representation of distinctive vocabulary
- **Training data:** Focused corpus for style-specific fine-tuning
- **Statistics:** Chunk counts and average lengths for quality assessment

## HTML OUTPUT DESIGN

### Visual Layout Structure
The generated HTML file contains four main sections in order:
1. **Word Cloud Visualization**: Frequency-ordered words from top-left to bottom-right
2. **Hover Instructions**: "Hover over words to see frequency counts"
3. **Interactive Bar Chart**: Top 20 words with Chart.js visualization
4. **Linguistic Analysis Bubble Chart**: Interactive Chart.js bubble chart showing word relationships with circular positioning

### CSS Architecture
**Dark Mode Design Philosophy:**
- **All interfaces use dark backgrounds** - consistent with MLX chat application
- **Primary background**: `--obsidian-black` (#0a0a0a) for body
- **Secondary background**: `--deep-charcoal` (#1a1a1a) for containers
- **Tertiary background**: `--volcanic-ash` (#2a2a2a) for content areas
- **Text color**: `--smoke-white` (#f5f5f5) for readability

**Magma Color Scheme:**
- **Highest frequency (>80%)**: `--molten-orange` (#ff6b35)
- **High frequency (>60%)**: `--ember-red` (#ff4500)
- **Medium frequency (>40%)**: `--lava-yellow` (#ffaa44)
- **Low frequency (>20%)**: `--warm-amber` (#ff8c42)
- **Lowest frequency**: `--copper-glow` (#d2691e)

**Layout Components:**
- `.wordcloud-container`: Dark charcoal background, centered, rounded corners
- `.wordcloud`: Volcanic ash background, left-aligned text, frequency-ordered
- `.wordcloud-chart-container`: Chart.js container with dark theme
- `.wordcloud-word`: Frequency-based CSS classes with magma colors
- `.wordcloud-word--high/medium/low`: Gradient from molten-orange to copper-glow

### Interactive Features
- **Word hover effects**: 1.1x scale transform on hover
- **Tooltips**: Show exact word counts on hover
- **Dual Chart.js integration**: 
  - Professional bar chart with magma color scheme
  - Interactive bubble chart with word relationships and linguistic data
- **Bootstrap Icons**: `bi-bar-chart-fill`, `bi-cursor-fill`, `bi-graph-up`, `bi-diagram-3` (no emoji)
- **Responsive design**: Adapts to different screen sizes
- **Visual hierarchy**: Clear separation between sections
- **Linguistic tooltips**: Hover over bubbles shows POS tags, lemmas, stems, and collocations

### Technical Implementation
- **Template System**: Separate HTML template (`templates/wordcloud_template.html`) with placeholder replacement
- **External CSS**: References `static/css/magma-theme.css` for consistency
- **Vis.js CDN**: Network visualization library for word relationships
- **Bootstrap Icons CDN**: Consistent iconography
- **Physics Engine**: Barnes-Hut algorithm with progressive damping
- **CSS variables**: All colors reference magma theme variables
- **Dark mode only**: Consistent with project-wide design standards
- **NLTK Integration**: Advanced linguistic analysis with sentence-level collocations
- **Network positioning**: Frequency-based distance zones with random angles
- **Interactive controls**: Custom zoom, POS filtering, node selection

### File Generation Logic
- **Default name**: `wordcloud.html`
- **Conflict handling**: Appends timestamp if file exists
- **Encoding**: UTF-8 for proper character support
- **Structure**: Complete HTML document with embedded Chart.js configuration
- **No duplicate files**: Overwrites existing file or creates timestamped version

## MLX LORA TRAINING INTEGRATION

### Training Data Formats
Both training data types use MLX-compatible format:
```json
{"text": "training content here"}
```

### Training Commands
**Vocabulary Training:**
```bash
python lora.py --model <model_path> --data vocabulary_training.jsonl --train --batch-size 4 --lora-layers 8
```

**Style Training:**
```bash
python lora.py --model <model_path> --data style_training.jsonl --train --batch-size 2 --lora-layers 16
```

**Sequential Training (Recommended):**
```bash
# First train on vocabulary patterns
python lora.py --model <model_path> --data vocabulary_training.jsonl --train --adapter-path ./vocab_adapter

# Then train on writing style using vocabulary-trained model
python lora.py --model <model_path> --adapter-path ./vocab_adapter --data style_training.jsonl --train --adapter-path ./final_adapter
```

### Training Parameters
**Vocabulary Training:**
- Smaller batch size (4) - shorter contexts
- Fewer LoRA layers (8) - focused learning
- Higher learning rate (1e-4) - specific patterns

**Style Training:**
- Smaller batch size (2) - longer contexts
- More LoRA layers (16) - complex patterns
- Lower learning rate (1e-5) - preserve style nuances

### Expected Outcomes
**Vocabulary Training Results:**
- Improved usage of domain-specific terms
- Better context-appropriate word selection
- Enhanced vocabulary precision

**Style Training Results:**
- Consistent writing tone and rhythm
- Improved sentence structure patterns
- Better genre/style adherence

**Combined Training Benefits:**
- Comprehensive language model adaptation
- Both vocabulary precision and style consistency
- Optimal for domain-specific writing tasks

## DOCUMENTATION MAINTENANCE PROTOCOL

### WHEN TO UPDATE THIS DOCUMENT
**MANDATORY UPDATES:** Any AI agent making changes must update this documentation
- **New functionality added** to any script in the workflow
- **Logic changes** in filtering, chunking, or processing algorithms
- **Parameter modifications** (token limits, thresholds, ratios)
- **New dependencies** or requirements added
- **File structure changes** or new output formats
- **Integration points** with other systems modified
- **Error handling** improvements or new edge cases

### HOW TO UPDATE
**Step 1:** Identify the affected section(s) in this document
**Step 2:** Update the relevant sections with:
- **What changed:** Specific functionality or logic modified
- **Why changed:** Reasoning behind the modification
- **Impact:** How it affects the overall workflow
- **New parameters:** Any new configuration options or limits

**Step 3:** Update related sections:
- **WORKFLOW SEQUENCE:** If process steps changed
- **FILE STRUCTURE:** If new files or directories added
- **DEPENDENCIES:** If new requirements added
- **USAGE COMMANDS:** If command syntax changed
- **INTEGRATION:** If MLX integration points modified

**Step 4:** Add to **CHANGE LOG** section (create if doesn't exist):
```
## CHANGE LOG
### [Date] - [AI Agent/User]
- **Changed:** Brief description
- **Reason:** Why the change was made
- **Impact:** What this affects in the workflow
```

### DOCUMENTATION QUALITY STANDARDS
- **Be specific:** Include exact parameter values, file paths, command syntax
- **Explain reasoning:** Why decisions were made, not just what was done
- **Maintain structure:** Keep the logical flow and section organization
- **Update examples:** Ensure all code examples and commands are current
- **Cross-reference:** Update related sections when making changes

### CRITICAL SECTIONS TO MAINTAIN
1. **WORKFLOW SEQUENCE:** Must reflect actual processing order
2. **Multi-Layer Filtering:** Keep filter criteria and thresholds current
3. **Smart Chunking:** Token limits and chunking logic must be accurate
4. **FILE STRUCTURE:** Paths and file formats must match implementation
5. **USAGE COMMANDS:** All command examples must work as written

### VALIDATION CHECKLIST
Before considering documentation complete:
- [ ] All new functionality documented with examples
- [ ] Parameter values match actual implementation
- [ ] File paths and commands tested and verified
- [ ] Integration steps updated if workflow changed
- [ ] Error handling scenarios documented
- [ ] Change log entry added with reasoning

**REMEMBER:** This document is the single source of truth for understanding the workflow. Incomplete or outdated documentation breaks the system for future AI agents and users.

## THIRD-PARTY DEPENDENCIES

### Core Technologies
- **[MLX](https://github.com/ml-explore/mlx)** - Apple's machine learning framework for Apple Silicon
- **[MLX-LM](https://github.com/ml-explore/mlx-examples/tree/main/llms)** - Language model utilities and examples
- **[NLTK](https://www.nltk.org/)** - Natural Language Toolkit for text processing
  - **Corpora**: punkt_tab, averaged_perceptron_tagger_eng, stopwords, wordnet
  - **Tools**: WordNetLemmatizer, PorterStemmer, BigramCollocationFinder

### Web Visualization
- **[Vis.js](https://visjs.org/)** - Network visualization library for word relationships
  - **Physics Engine**: Barnes-Hut algorithm with progressive damping
  - **Network Features**: Node positioning, edge connections, interactive controls
- **[Bootstrap](https://getbootstrap.com/)** - CSS framework for responsive design
- **[Bootstrap Icons](https://icons.getbootstrap.com/)** - Professional icon library

### Data Processing
- **[NumPy](https://numpy.org/)** - Numerical computing for data analysis
- **[Matplotlib](https://matplotlib.org/)** - Plotting library for data visualization
- **[python-docx](https://python-docx.readthedocs.io/)** - Microsoft Word document processing

### Model Sources
- **[Hugging Face](https://huggingface.co/)** - Model repository and conversion source
- **[MLX Community](https://huggingface.co/mlx-community)** - Pre-converted MLX-compatible models

### Development Environment
- **[Anaconda/Miniconda](https://www.anaconda.com/)** - Python environment management
- **[Flask](https://flask.palletsprojects.com/)** - Web framework for MLX Chat interface
