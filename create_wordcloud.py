#!/usr/bin/env python3
"""
Enhanced Word Cloud Generator with Chart.js and Mosaic Design
"""

import os
import re
from collections import Counter, defaultdict
from pathlib import Path
import random
import json
import math

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer, PorterStemmer
    from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
    from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
    from nltk.corpus import wordnet
    from nltk import ne_chunk
    
    # Download required NLTK data only if needed
    try:
        # Test all functionality at once to reduce exception handling overhead
        word_tokenize("test")
        pos_tag(["test"])
        stopwords.words('english')
        wordnet.synsets('test')
    except (LookupError, OSError):
        # Download all required components if any test fails
        for download_name in ['punkt_tab', 'averaged_perceptron_tagger_eng', 'stopwords', 'wordnet']:
            try:
                nltk.download(download_name, quiet=True)
            except (LookupError, OSError, ValueError):
                pass
    
    NLTK_AVAILABLE = True
    print("NLTK loaded successfully")
    
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available, using basic word filtering")

# Try to load spaCy for better acronym detection
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
    print("spaCy loaded for acronym detection")
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    print("spaCy not available, using NLTK only")

def read_docx_file(file_path):
    """Read text content from a .docx file"""
    if not DOCX_AVAILABLE:
        print(f"Warning: python-docx not available, skipping {file_path}")
        return ""
    
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except (IOError, OSError, ValueError, AttributeError) as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def read_files_from_directory(source_dir):
    """Read all text and docx files from directory"""
    source_path = Path(source_dir).resolve()
    text_files = list(source_path.glob("*.txt"))
    docx_files = list(source_path.glob("*.docx")) if DOCX_AVAILABLE else []
    all_files = text_files + docx_files
    
    # Filter files first, then read content for better performance
    valid_files = [f for f in all_files if f.is_relative_to(source_path)]
    
    # Read files separately to avoid unnecessary function calls
    contents = []
    for f in valid_files:
        content = _read_single_file(f)
        if content is not None:
            contents.append(content)
    return contents

def _read_single_file(file_path):
    """Read a single file and return content or None on error"""
    try:
        # Resolve and validate file path to prevent traversal attacks
        resolved_path = Path(file_path).resolve()
        
        if resolved_path.suffix.lower() == '.docx':
            content = read_docx_file(resolved_path)
        else:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
        return content.strip() if content.strip() else None
    except (IOError, OSError, UnicodeDecodeError) as e:
        print(f"Error processing {file_path}: {e}")
        return None

def _passes_character_filter(word, filter_options, alphanumeric_pattern):
    """Check if word passes character composition filters"""
    if not alphanumeric_pattern.match(word):
        return False
    
    if filter_options.get('include_alphanumeric', False):
        # Early return for pure digits
        if word.isdigit():
            return False
        # Check for decimal numbers with single dot
        if '.' in word:
            no_dot = word.replace('.', '')
            if no_dot.isdigit() and word.count('.') <= 1:
                return False
        return True
    else:
        return word.isalpha()

def _passes_length_filter(word, filter_options):
    """Check if word passes length filter"""
    return len(word) >= filter_options.get('min_length', 3)

def _passes_proper_noun_filter(word, filter_options):
    """Check if word passes proper noun filter"""
    return filter_options.get('include_proper_nouns', False) or not word[0].isupper()

def _passes_exclusion_filter(word_lower, user_exclusions):
    """Check if word passes user exclusion filter"""
    return not (user_exclusions and word_lower in user_exclusions)

def _passes_pos_filter(pos, filter_options):
    """Check if POS tag passes filter"""
    return pos in filter_options.get('pos_tags', ['NN', 'NNS', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'])

def _process_content_with_nltk(content, filter_options, alphanumeric_pattern, user_exclusions, all_words, all_pos_tags):
    """Process content using NLTK for POS tagging and spaCy for acronym detection"""
    tokens = word_tokenize(content)
    pos_tags = pos_tag(tokens)
    
    # Find all-caps words that NLTK didn't classify as nouns
    caps_non_nouns = set()
    for word, pos in pos_tags:
        if (word.isupper() and len(word) >= 2 and word.isalpha() and 
            not pos.startswith('NN')):
            caps_non_nouns.add(word)
    
    # Use spaCy only for these problematic all-caps words
    spacy_acronyms = set()
    if SPACY_AVAILABLE and caps_non_nouns:
        try:
            doc = nlp(content)
            spacy_entities = {token.text for token in doc 
                            if token.ent_type_ in ['ORG', 'PERSON', 'GPE'] or token.pos_ in ['PROPN', 'NOUN']}
            spacy_acronyms = caps_non_nouns & spacy_entities
        except (OSError, ValueError) as e:
            print(f"spaCy processing error: {e}")
    
    # Override POS tags only for spaCy-confirmed acronyms
    modified_pos_tags = [(word, 'NNP' if word in spacy_acronyms else pos) 
                       for word, pos in pos_tags]
    
    # Apply filters and collect words
    for word, pos in modified_pos_tags:
        word_lower = word.lower()
        
        if (_passes_character_filter(word, filter_options, alphanumeric_pattern) and
            _passes_length_filter(word, filter_options) and
            _passes_proper_noun_filter(word, filter_options) and
            _passes_exclusion_filter(word_lower, user_exclusions) and
            _passes_pos_filter(pos, filter_options)):
            all_words.append(word_lower)
            all_pos_tags.append((word_lower, pos))

def _process_content_without_nltk(content, filter_options, alphanumeric_pattern, user_exclusions, all_words, all_pos_tags):
    """Process content using basic regex filtering when NLTK is not available"""
    if filter_options.get('include_alphanumeric', False):
        words = re.findall(r'\b\w+\b', content.lower())
        words = [w for w in words if not (w.isdigit() or (w.replace('.', '').isdigit() and w.count('.') <= 1))]
    else:
        words = re.findall(r'\b[a-z]+\b', content.lower())
    
    for word in words:
        if not alphanumeric_pattern.match(word):
            continue
        
        if len(word) < filter_options.get('min_length', 3):
            continue
        
        if not filter_options.get('include_proper_nouns', False):
            if word[0].isupper():
                continue
        
        if user_exclusions and word in user_exclusions:
            continue
        
        all_words.append(word)
        all_pos_tags.append((word, 'NN'))

def perform_linguistic_analysis_with_tags(all_words, source_dir, provided_pos_tags, file_contents=None):
    """Perform NLTK linguistic analysis using provided POS tags"""
    if not NLTK_AVAILABLE:
        return {}, {}, {}
    
    lemmatizer = WordNetLemmatizer()
    
    # Group words by linguistic features
    pos_analysis = defaultdict(list)
    lemma_groups = defaultdict(list)
    
    # Create lookup for POS tags
    pos_lookup = {word: pos for word, pos in provided_pos_tags}
    
    # Analyze each word using provided POS tags
    for word in all_words:
        # Use provided POS tag or default to NN
        word_pos = pos_lookup.get(word, 'NN')

        pos_analysis[word_pos].append(word)
        
        # Lemmatize
        lemma = lemmatizer.lemmatize(word)
        lemma_groups[lemma].append(word)
    
    # Use provided file contents or read from directory
    if file_contents is None:
        file_contents = read_files_from_directory(source_dir)
    combined_text = ' '.join(file_contents)
    
    # Find sentence-level word co-occurrences (same as original)
    sentences = re.split(r'[.!?]+', combined_text)
    collocations = []
    
    for sentence in sentences:
        if len(sentence.strip()) < 20:  # Skip very short sentences
            continue
        sentence_tokens = word_tokenize(sentence.lower())
        sentence_words = [token for token in sentence_tokens if token.isalpha() and len(token) >= 3]
        
        # Create pairs from words in same sentence
        for i, word1 in enumerate(sentence_words):
            for word2 in sentence_words[i+1:]:
                if word1 != word2 and word1 in all_words and word2 in all_words:
                    collocations.append((word1, word2))
    
    # Count co-occurrence frequency and keep top pairs
    from collections import Counter
    collocation_counts = Counter(collocations)
    collocations = [pair for pair, count in collocation_counts.most_common(200) if count >= 2]
    
    return pos_analysis, lemma_groups, collocations

def perform_linguistic_analysis(all_words, source_dir, file_contents=None):
    """Perform NLTK linguistic analysis on words"""
    if not NLTK_AVAILABLE:
        return {}, {}, {}
    
    # Use provided file contents to avoid re-reading
    if file_contents is None:
        file_contents = read_files_from_directory(source_dir)
    combined_text = ' '.join(file_contents)
    tokens = word_tokenize(combined_text.lower())
    pos_tags = pos_tag(tokens)
    
    # Call perform_linguistic_analysis_with_tags with computed POS tags
    return perform_linguistic_analysis_with_tags(all_words, source_dir, pos_tags, file_contents)

def generate_network_chart_data(word_counts, collocations, pos_analysis=None, lemma_groups=None, max_words=100):
    """Generate bubble chart data with word relationships and linguistic analysis"""
    # Constants for positioning
    BASE_RADIUS = 100
    RADIUS_MULTIPLIER = 50
    
    top_words = dict(word_counts.most_common(max_words))
    
    # Guard clause to prevent division by zero
    if not top_words:
        return [], []
    
    # Create efficient lookup dictionaries
    pos_lookup = {}
    lemma_lookup = {}
    if pos_analysis:
        pos_lookup = {word: pos for pos, words in pos_analysis.items() for word in words}
    if lemma_groups:
        lemma_lookup = {word: lemma for lemma, words in lemma_groups.items() for word in words}
    
    # Pre-build collocation lookup for O(1) access
    collocation_lookup = defaultdict(list)
    for word1, word2 in collocations:
        collocation_lookup[word1].append(f"{word1} + {word2}")
        collocation_lookup[word2].append(f"{word1} + {word2}")
    
    # Create word position mapping for bubble chart
    bubble_data = []
    word_positions = {}
    
    # Calculate max count once for efficiency
    max_word_count = max(top_words.values())
    
    # Arrange words in a circular pattern
    for i, (word, count) in enumerate(top_words.items()):
        angle = (i / len(top_words)) * 2 * math.pi
        radius = BASE_RADIUS + (count / max_word_count) * RADIUS_MULTIPLIER
        
        x = 200 + radius * math.cos(angle)
        y = 200 + radius * math.sin(angle)
        
        word_positions[word] = (x, y)
        
        # Use efficient lookups
        pos_tag = pos_lookup.get(word, 'NN')
        lemma = lemma_lookup.get(word, word)
        word_collocations = collocation_lookup[word][:3]  # Limit to 3 collocations
        
        bubble_data.append({
            'x': round(x, 2),
            'y': round(y, 2), 
            'r': max(8, min(25, count * 2)),
            'word': word,
            'count': count,
            'pos': pos_tag,
            'lemma': lemma,
            'collocations': word_collocations
        })
    
    # Add collocation connections
    connections = []
    for word1, word2 in collocations:
        if word1 in word_positions and word2 in word_positions:
            x1, y1 = word_positions[word1]
            x2, y2 = word_positions[word2]
            connections.append({
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2,
                'words': f"{word1} + {word2}"
            })
    
    return bubble_data, connections

def create_wordcloud(source_dir, output_file="wordcloud.html", user_exclusions=None, filter_options=None):
    """Create word cloud with Chart.js and mosaic design"""
    
    # Set default filter options if not provided
    if filter_options is None:
        filter_options = {
            'min_length': 3,
            'include_alphanumeric': True,
            'include_proper_nouns': True,
            'frequency_threshold': 50,
            'pos_tags': ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']
        }
    
    # Validate and secure source directory path
    source_path = Path(source_dir).resolve()
    if not source_path.exists():
        print(f"Error: Directory {source_dir} does not exist")
        return False
    
    # Security: Ensure source path is within allowed directories
    allowed_base = Path(__file__).parent.resolve()
    try:
        source_path.relative_to(allowed_base)
    except ValueError:
        print(f"Error: Access denied to directory outside project: {source_dir}")
        return False
    
    # Collect all text and docx files
    text_files = list(source_path.glob("*.txt"))
    docx_files = list(source_path.glob("*.docx")) if DOCX_AVAILABLE else []
    all_files = text_files + docx_files
    if not all_files:
        print(f"No .txt or .docx files found in {source_dir}")
        return False
    
    print(f"Processing {len(text_files)} .txt files and {len(docx_files)} .docx files...")
    
    # Collect all words and POS tags in single pass
    all_words = []
    all_pos_tags = []
    file_contents = []  # Store file contents to avoid re-reading
    
    # Pre-compile regex patterns for performance
    alphanumeric_pattern = re.compile(r'^[a-zA-Z0-9]+$')
    
    for file_path in all_files:
        try:
            # Validate file path security
            if not file_path.is_relative_to(source_path):
                print(f"Skipping file outside source directory: {file_path}")
                continue
                
            # Read content based on file type
            if file_path.suffix.lower() == '.docx':
                content = read_docx_file(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Store content to avoid re-reading
            if content.strip():
                file_contents.append(content)
                
            if NLTK_AVAILABLE:
                _process_content_with_nltk(content, filter_options, alphanumeric_pattern, user_exclusions, all_words, all_pos_tags)
            else:
                _process_content_without_nltk(content, filter_options, alphanumeric_pattern, user_exclusions, all_words, all_pos_tags)
                        
        except (IOError, OSError, UnicodeDecodeError) as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    if not all_words:
        print("No words found after filtering")
        return False
    
    # Count word frequencies
    word_counts = Counter(all_words)
    
    # Apply frequency threshold - keep top X% most common words
    threshold_percent = filter_options.get('frequency_threshold', 50) / 100.0
    num_words_to_keep = max(1, int(len(word_counts) * threshold_percent))
    filtered_counts = dict(word_counts.most_common(num_words_to_keep))
    
    max_count = max(filtered_counts.values())
    
    print(f"Found {len(word_counts)} unique words, filtered to {len(filtered_counts)}, showing top 100")
    
    # Perform linguistic analysis with collected POS tags (no duplicate processing)
    print("Performing linguistic analysis...")
    pos_analysis, lemma_groups, collocations = perform_linguistic_analysis_with_tags(all_words, None, all_pos_tags, file_contents)
    
    # Generate network chart data with linguistic analysis
    bubble_data, connections = generate_network_chart_data(word_counts, collocations, pos_analysis, lemma_groups)
    print(f"Generated {len(bubble_data)} bubble data points, {len(collocations)} collocations found")
    
    # Generate HTML
    html_content = generate_html(word_counts, filtered_counts, max_count, source_dir, 
                                        pos_analysis, bubble_data, connections)
    
    # Write HTML file (overwrite existing)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Word cloud saved to: {output_path.absolute()}")
    
    # Show top words
    print(f"Top 5 words: {', '.join(f'{word} ({count})' for word, count in word_counts.most_common(5))}")
    
    return True, output_path

def generate_html(word_counts, filtered_counts, max_count, source_dir, 
                         pos_analysis=None, bubble_data=None, connections=None):
    """Generate HTML using template file"""
    
    # Prepare data
    if bubble_data is None:
        bubble_data = []
    if connections is None:
        connections = []
    
    # Read template file with error handling
    template_path = Path(__file__).parent / "templates" / "wordcloud_template.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except (FileNotFoundError, IOError) as e:
        print(f"Error reading template file {template_path}: {e}")
        return f"<html><body><h1>Error: Template file not found</h1><p>{e}</p></body></html>"
    
    # Replace placeholders with actual data using string replacement
    try:
        html_content = template.replace('{total_words}', str(len(word_counts)))
        html_content = html_content.replace('{unique_words}', str(len(filtered_counts)))
        html_content = html_content.replace('{network_data}', json.dumps(bubble_data))
        html_content = html_content.replace('{collocations_data}', json.dumps(connections))
    except (KeyError, ValueError) as e:
        print(f"Error formatting template: {e}")
        return f"<html><body><h1>Error: Template formatting failed</h1><p>{e}</p></body></html>"
    
    return html_content

def get_user_options():
    """Get user-defined filter options"""
    print("\n=== Word Cloud Configuration ===")
    print("Press Enter to use default values shown in [brackets]\n")
    
    # Minimum word length
    while True:
        try:
            response = input("Minimum word length [3]: ").strip()
            min_length = int(response) if response else 3
            if min_length >= 1:
                break
            print("Please enter a number >= 1")
        except ValueError:
            print("Please enter a valid number")
    
    # Include alphanumeric
    response = input("Include alphanumeric words? (y/n) [Y]: ").strip().lower()
    include_alphanumeric = response != 'n'
    
    # Include proper nouns
    response = input("Include proper nouns? (y/n) [Y]: ").strip().lower()
    include_proper_nouns = response != 'n'
    
    # Frequency threshold
    while True:
        try:
            response = input("Frequency threshold % [50]: ").strip()
            freq_threshold = int(response) if response else 50
            if 1 <= freq_threshold <= 100:
                break
            print("Please enter a number between 1-100")
        except ValueError:
            print("Please enter a valid number")
    
    # User exclusions
    exclusions_input = input("Words to exclude (comma-separated) [none]: ").strip()
    user_exclusions = [word.strip().lower() for word in exclusions_input.split(',') if word.strip()] if exclusions_input else None
    
    return {
        'min_length': min_length,
        'include_alphanumeric': include_alphanumeric,
        'include_proper_nouns': include_proper_nouns,
        'frequency_threshold': freq_threshold,
        'pos_tags': ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']
    }, user_exclusions

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = Path(__file__).parent / "model" / "training_data"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "model/wordcloud/wordcloud.html"
    
    # Get user configuration
    filter_options, user_exclusions = get_user_options()
    
    success, output_path = create_wordcloud(source_dir, output_file, user_exclusions, filter_options)
    
    if success:
        # Ask about training data generation
        response = input("\nGenerate LoRA training data? (y/n) [N]: ").strip().lower()
        if response.startswith('y'):
            print("\nTraining Data Options:")
            print("1. Vocabulary training data")
            print("2. Style training data") 
            print("3. Both vocabulary and style training data")
            
            choice = input("Select option [3]: ").strip() or "3"
            
            # Create training data directory
            training_dir = Path(source_dir).parent / "lora_training"
            training_dir.mkdir(exist_ok=True)
            
            print(f"Training data will be saved to: {training_dir}")
            print("Use create_lora.py to generate actual training files from this data.")
    
    if success:
        print(f"✅ Word cloud generated successfully!")
        print(f"Open {output_path} in your browser to view the results.")
    else:
        print("❌ Failed to generate word cloud")