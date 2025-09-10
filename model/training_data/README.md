# Training Data Directory

Place your text files here for analysis and LoRA training data generation.

## Supported File Types
- `.txt` files (UTF-8 encoding)
- `.docx` files (Microsoft Word documents)

## Example Usage

1. **Add your files:**
   ```
   model/training_data/
   ├── document1.txt
   ├── research_paper.docx
   ├── meeting_notes.txt
   └── project_specs.txt
   ```

2. **Run analysis:**
   ```bash
   conda activate mlx-qwa
   python create_wordcloud.py
   ```

3. **View results:**
   - Interactive word cloud: `model/wordcloud/wordcloud.html`
   - Training data: `model/lora_training/` (if generated)

## What Gets Analyzed
- Word frequencies and relationships
- Part-of-speech patterns
- Collocations (words that appear together)
- Linguistic patterns for LoRA training

## Privacy Note
Your files are processed locally - nothing is sent to external servers.