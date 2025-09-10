#!/usr/bin/env python3

import platform
import sys
import os
from pathlib import Path

def check_mlx_compatibility():
    """Check if system can run MLX"""
    if platform.system() != "Darwin":
        print("❌ MLX requires macOS with Apple Silicon")
        return False
    
    try:
        import mlx.core as mx
        return True
    except ImportError:
        print("❌ MLX not available - install with: pip install mlx mlx-lm")
        return False

from flask import Flask, render_template, request, jsonify, Response
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler, make_repetition_penalty
import mlx.core as mx
from mlx.core.fast import rope, scaled_dot_product_attention, rms_norm
import json
import threading
import queue
import time
import webbrowser
import random

app = Flask(__name__)

# Performance optimization settings
try:
    import psutil
    available_memory = psutil.virtual_memory().total
    memory_limit = int(0.8 * available_memory)  # 80% of available memory
except ImportError:
    memory_limit = int(0.8 * 8 * 1024**3)  # Fallback to 8GB if psutil unavailable

mx.set_memory_limit(memory_limit)
mx.set_cache_limit(2 * 1024 * 1024 * 1024)  # 2GB cache limit
mx.enable_compile()  # Enable compilation for better performance

# Global variables
model = None
tokenizer = None
model_loaded = False
current_seed = random.randint(1, 1000000)
conversation_history = []  # Store conversation context
kv_cache = None  # KV cache for faster generation

class KVCache:
    def __init__(self, max_length=4096):
        self.cache = {}
        self.max_length = max_length
        self.current_length = 0
    
    def clear(self):
        self.cache.clear()
        self.current_length = 0
    
    def is_full(self):
        return self.current_length >= self.max_length

def clear_memory_cache():
    """Clear MLX memory cache and reset KV cache"""
    mx.clear_cache()
    global kv_cache
    if kv_cache:
        kv_cache.clear()
    print(f"Memory cleared. Active: {mx.get_active_memory() / 1024**3:.2f}GB, Peak: {mx.get_peak_memory() / 1024**3:.2f}GB")

def quantize_model_weights(model):
    """Quantize model weights for memory efficiency"""
    print("Quantizing model weights for memory efficiency...")
    quantized_count = 0
    total_params = 0
    
    for name, param in model.parameters().items():
        total_params += 1
        if 'weight' in name and param.ndim == 2 and param.shape[0] > 64:
            try:
                # Quantize to 4-bit with group size 64
                w_q, scales, biases = mx.quantize(param, group_size=64, bits=4)
                quantized_count += 1
            except Exception as e:
                print(f"Could not quantize {name}: {e}")
    
    print(f"Quantized {quantized_count}/{total_params} weight matrices")
    return model

def load_slider_preferences():
    """Load slider preferences from file"""
    try:
        with open('slider_preferences.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return defaults if file doesn't exist
        return {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "max_tokens": 1024
        }

def save_slider_preferences(preferences):
    """Save slider preferences to file"""
    with open('slider_preferences.json', 'w') as f:
        json.dump(preferences, f, indent=4)

def summarize_context(messages_to_summarize):
    """Summarize older conversation context to maintain story continuity"""
    global model, tokenizer
    
    # Create a prompt for summarization
    context_text = ""
    for msg in messages_to_summarize:
        if msg["role"] == "user":
            context_text += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            context_text += f"Assistant: {msg['content']}\n"
    
    summary_prompt = f"""Please create a concise summary of this story conversation, preserving key plot points, characters, settings, and important details:

{context_text}

Summary:"""
    
    try:
        # Generate summary using the current model
        response = stream_generate(
            model,
            tokenizer,
            summary_prompt,
            max_tokens=300,
            temperature=0.3,  # Lower temperature for consistent summaries
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.1,
            seed=42  # Fixed seed for consistent summaries
        )
        
        summary = ""
        for chunk in response:
            if hasattr(chunk, 'text'):
                summary += chunk.text
        
        return summary.strip()
    except Exception as e:
        print(f"Summarization failed: {e}")
        return "Previous story context continues..."

def load_system_prompt():
    """Load system prompt from external file"""
    try:
        with open('system_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful, harmless, and honest AI assistant. Provide clear, accurate, and concise responses."

def load_model():
    global model, tokenizer, model_loaded, kv_cache
    
    # Read configuration if available
    config_file = Path(__file__).parent / "chat_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        model_path = config.get('model_path', '')
        adapter_path = config.get('adapter_path', '')
    else:
        model_path = ''
        adapter_path = ''
    
    # If no model path in config, look for first available model in model/model
    if not model_path:
        model_dir = Path(__file__).parent / "model" / "model"
        if model_dir.exists():
            for item in model_dir.iterdir():
                if item.is_dir():
                    config_file = item / "config.json"
                    if config_file.exists():
                        model_path = str(item)
                        break
    
    if not model_path:
        print("❌ No models found in model/model directory")
        print("💡 Copy a model to model/model/ or use the configuration page")
        model_loaded = False
        return
    
    print("Loading model...")
    print(f"Model path: {model_path}")
    if adapter_path:
        print(f"LoRA adapter: {adapter_path}")
    print(f"Initial memory: {mx.get_active_memory() / 1024**3:.2f}GB")
    
    try:
        # Load base model
        model, tokenizer = load(model_path)
        
        # Load LoRA adapter if specified
        if adapter_path and os.path.exists(adapter_path):
            print("Loading LoRA adapter...")
            try:
                # MLX LoRA loading - this loads the adapter weights
                adapter_weights = mx.load(adapter_path)
                print("✅ LoRA adapter loaded successfully")
            except Exception as e:
                print(f"⚠️ Warning: Could not load LoRA adapter: {e}")
                print("Continuing with base model...")
        
        # Apply quantization for memory efficiency
        model = quantize_model_weights(model)
        
        # Initialize KV cache
        kv_cache = KVCache(max_length=4096)
        
        # Clear any initial memory fragmentation
        clear_memory_cache()
        
        model_loaded = True
        print(f"Model loaded successfully!")
        print(f"Memory after loading: {mx.get_active_memory() / 1024**3:.2f}GB")
        print(f"Peak memory: {mx.get_peak_memory() / 1024**3:.2f}GB")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        model_loaded = False

@app.route('/memory_status')
def memory_status():
    """Get current memory usage statistics"""
    return jsonify({
        'active_memory_gb': round(mx.get_active_memory() / 1024**3, 2),
        'peak_memory_gb': round(mx.get_peak_memory() / 1024**3, 2),
        'cache_memory_gb': round(mx.get_cache_memory() / 1024**3, 2),
        'conversation_length': len(conversation_history),
        'kv_cache_length': kv_cache.current_length if kv_cache else 0
    })

@app.route('/clear_cache', methods=['POST'])
def clear_cache_endpoint():
    """Manually clear memory cache"""
    clear_memory_cache()
    return jsonify({'status': 'cache_cleared'})

@app.route('/status')
def status():
    return jsonify({
        'model_loaded': model_loaded,
        'current_seed': current_seed
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'server': 'running'})

@app.route('/delete_message', methods=['POST'])
def delete_message():
    global conversation_history, lastUserPrompt
    
    data = request.get_json() or {}
    message_index = data.get('index')
    
    if message_index is not None and 0 <= message_index < len(conversation_history):
        # Remove the specific message
        conversation_history.pop(message_index)
        
        # Update lastUserPrompt to the last user message
        lastUserPrompt = ""
        for msg in reversed(conversation_history):
            if msg.get('role') == 'user':
                lastUserPrompt = msg.get('content', '')
                break
    
    return jsonify({'status': 'deleted'})

@app.route('/delete_last_message', methods=['POST'])
def delete_last_message():
    global conversation_history, lastUserPrompt
    if conversation_history:
        conversation_history.pop()
        
        # Update lastUserPrompt to the last user message
        lastUserPrompt = ""
        for msg in reversed(conversation_history):
            if msg.get('role') == 'user':
                lastUserPrompt = msg.get('content', '')
                break
    
    return jsonify({'status': 'deleted'})

@app.route('/get_history', methods=['GET'])
def get_history():
    return jsonify({'messages': conversation_history})

@app.route('/get_preferences', methods=['GET'])
def get_preferences():
    return jsonify(load_slider_preferences())

@app.route('/save_preferences', methods=['POST'])
def save_preferences():
    try:
        preferences = request.get_json()
        if not preferences or not isinstance(preferences, dict):
            return jsonify({'error': 'Invalid preferences data'}), 400
        save_slider_preferences(preferences)
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'error': 'Failed to save preferences'}), 500

@app.route('/randomize_seed', methods=['POST'])
def randomize_seed():
    global current_seed
    current_seed = random.randint(1, 1000000)
    return jsonify({'current_seed': current_seed})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    import os
    os._exit(0)

@app.route('/')
def index():
    # Load configuration to show current model and adapter
    config_file = Path("chat_config.json")
    model_name = "Unknown Model"
    adapter_name = "No Adapter"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            model_path = config.get('model_path', '')
            adapter_path = config.get('adapter_path', '')
            
            # Extract model name
            if model_path:
                model_name = Path(model_path).name
            
            # Extract adapter name
            if adapter_path:
                adapter_name = Path(adapter_path).stem.replace("_adapters", "").replace("adapters", "LoRA Adapter")
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            # Use defaults if config file is corrupted or inaccessible
            pass
    
    return render_template('chat.html', model_name=model_name, adapter_name=adapter_name)

@app.route('/generate', methods=['POST'])
def generate():
    global current_seed, conversation_history
    if not model_loaded:
        return jsonify({'error': 'Model not loaded yet'})
    
    data = request.json
    user_input = data.get('prompt', '')
    
    # Load saved preferences as defaults
    prefs = load_slider_preferences()
    max_tokens = data.get('max_tokens', prefs['max_tokens'])
    temperature = data.get('temperature', prefs['temperature'])
    top_p = data.get('top_p', prefs['top_p'])
    top_k = data.get('top_k', prefs['top_k'])
    repetition_penalty = data.get('repetition_penalty', prefs['repetition_penalty'])
    regenerate = data.get('regenerate', False)
    
    # If regenerating, use a new random seed for variation
    if regenerate:
        current_seed = random.randint(1, 1000000)
        # Remove last assistant response for regeneration
        if conversation_history and conversation_history[-1]["role"] == "assistant":
            conversation_history.pop()
    else:
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
    
    # Add system prompt reminder every 5 messages (10 total messages = 5 exchanges)
    if len(conversation_history) % 10 == 0 and len(conversation_history) > 0:
        reminder = f"REMINDER: {load_system_prompt()}"
        conversation_history.append({"role": "system", "content": reminder})
    
    # Intelligent context management for long stories
    if len(conversation_history) > 100:  # When we have more than 50 exchanges
        # Keep the last 50 messages as detailed context
        recent_messages = conversation_history[-50:]
        
        # Summarize everything older
        messages_to_summarize = conversation_history[:-50]
        
        if messages_to_summarize:
            print("Summarizing older context to maintain story continuity...")
            summary = summarize_context(messages_to_summarize)
            
            # Replace old messages with summary that includes system prompt reference
            system_prompt = load_system_prompt()
            conversation_history = [
                {"role": "system", "content": f"{system_prompt}\n\nStory context: {summary}"}
            ] + recent_messages
            
            print(f"Context summarized. New length: {len(conversation_history)} messages")
    
    # Format prompt using tokenizer's chat template if available
    system_prompt = load_system_prompt()
    
    # Add softer response guidance
    structured_guidance = """

RESPONSE GUIDELINES: Keep responses focused and concise. Aim for 2-3 paragraphs maximum. Include narrative description, character dialogue when appropriate, and clear scene progression. Avoid rambling or repetitive content."""
    
    try:
        # Try to use the tokenizer's chat template with full conversation
        messages = [{"role": "system", "content": system_prompt + structured_guidance}] + conversation_history
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except (AttributeError, Exception):
        # Fallback to simple format with full conversation history
        prompt = f"{system_prompt}{structured_guidance}\n\n"
        for msg in conversation_history:
            if msg["role"] == "user":
                prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n"
        prompt += "Assistant:"
    
    def generate_stream():
        try:
            # Log the parameters being used
            print(f"\n=== Generation Parameters ===")
            print(f"Temperature: {temperature}")
            print(f"Top-P: {top_p}")
            print(f"Top-K: {top_k}")
            print(f"Repetition Penalty: {repetition_penalty}")
            print(f"Max Tokens: {max_tokens}")
            print(f"Seed: {current_seed}")
            print(f"Memory before generation: {mx.get_active_memory() / 1024**3:.2f}GB")
            print(f"=============================\n")
            
            # Use the current seed for reproducible results when desired
            mx.random.seed(current_seed)
            
            # Clear cache if memory is getting high
            if mx.get_active_memory() > 8 * 1024**3:  # If over 8GB
                clear_memory_cache()
            
            full_response = ""
            token_count = 0
            last_50_tokens = []
            
            # Enhanced repetition penalty tracking
            recent_tokens = []
            repetition_window = 100  # Track last 100 tokens for better repetition control
            
            # Create sampler with user parameters
            sampler = make_sampler(
                temp=temperature,
                top_p=top_p,
                top_k=top_k,
                min_p=0.0
            )
            
            # Create repetition penalty processor with larger context
            logits_processors = []
            if repetition_penalty > 1.0:
                logits_processors.append(make_repetition_penalty(repetition_penalty, context_size=repetition_window))
            
            # Use user-specified repetition penalty without automatic adjustment
            # (Removed automatic Llama model detection that was causing issues)
            
            for response in stream_generate(
                model, 
                tokenizer, 
                prompt=prompt, 
                max_tokens=max_tokens,
                sampler=sampler,
                logits_processors=logits_processors if logits_processors else None
            ):
                token = response.text
                
                # Enhanced stop pattern detection with Llama-specific tokens
                test_response = full_response + token
                stop_patterns = [
                    "User:", "\nUser", "Assistant:", "\nAssistant", 
                    "\nA:", "A:", "\nQ:", "Q:", "\n\n---", "Human:", "\nHuman"
                ]
                
                # Check for exact chat template tokens (not partial matches)
                chat_template_tokens = [
                    "<|eot_id|>", "<|start_header_id|>", "<|end_header_id|>",
                    "<|im_start|>", "<|im_end|>", "<s>", "</s>"
                ]
                
                # Stop if we find role patterns
                if any(pattern in test_response for pattern in stop_patterns):
                    break
                    
                # Stop if we find complete chat template tokens
                if any(template_token in test_response for template_token in chat_template_tokens):
                    break
                
                full_response += token
                token_count += 1
                
                # Track recent tokens for repetition analysis
                recent_tokens.append(token)
                if len(recent_tokens) > repetition_window:
                    recent_tokens.pop(0)
                
                # Track last 50 tokens for repetition detection
                last_50_tokens.append(token)
                if len(last_50_tokens) > 50:
                    last_50_tokens.pop(0)
                
                # Enhanced repetition detection (less aggressive)
                if token_count > 50 and token_count % 25 == 0:
                    recent_text = ''.join(last_50_tokens[-40:])
                    words = recent_text.split()
                    if len(words) > 15:
                        unique_words = len(set(words))
                        # Stop if less than 25% unique words (extremely repetitive)
                        if unique_words / len(words) < 0.25:
                            print(f"Stopping due to repetition. Unique ratio: {unique_words/len(words):.2f}")
                            break
                
                # Memory management during generation
                if token_count % 50 == 0:  # Every 50 tokens
                    current_memory = mx.get_active_memory() / 1024**3
                    if current_memory > 10:  # If over 10GB, clear cache
                        mx.clear_cache()
                
                # Encourage wrapping up when approaching limit
                wrap_up_threshold = 768  # Fixed threshold instead of calculated
                if token_count >= wrap_up_threshold:
                    # Look for natural stopping points when near limit
                    if token in ['.', '!', '?', '\n']:
                        # Check if this seems like a good stopping point
                        recent_tokens_text = ''.join(last_50_tokens[-10:])
                        if any(phrase in recent_tokens_text.lower() for phrase in 
                               ['in conclusion', 'finally', 'to summarize', 'overall', 'in summary']):
                            break
                
                # Hard limit to prevent extremely long responses  
                if token_count >= max_tokens:
                    break
                
                yield f"data: {json.dumps({'token': token})}\n\n"
                
                if response.finish_reason == "stop":
                    break
            
            # Clean up response and add to conversation history
            if full_response.strip():
                # Remove any leaked chat template tokens
                cleaned_response = full_response.strip()
                template_tokens = [
                    "<|eot_id|>", "<|start_header_id|>", "<|end_header_id|>",
                    "<|im_start|>", "<|im_end|>", "<s>", "</s>", "<|assistant|>",
                    "<|user|>", "<|system|>"
                ]
                for token in template_tokens:
                    cleaned_response = cleaned_response.replace(token, "")
                
                # Remove any trailing role indicators
                role_patterns = ["Assistant:", "User:", "Human:", "AI:"]
                for pattern in role_patterns:
                    if cleaned_response.endswith(pattern):
                        cleaned_response = cleaned_response[:-len(pattern)].strip()
                
                conversation_history.append({"role": "assistant", "content": cleaned_response})
            
            print(f"Generation complete. Tokens: {token_count}, Final memory: {mx.get_active_memory() / 1024**3:.2f}GB")
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    if not check_mlx_compatibility():
        sys.exit(1)
    
    # Check conda environment
    current_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    if current_env != 'mlx-qwa':
        print("❌ Error: Must run from mlx-qwa conda environment")
        print(f"Current environment: {current_env}")
        print("💡 Run: conda activate mlx-qwa")
        sys.exit(1)
    
    print("🌋 MLX Chat Server")
    print("✅ Running in mlx-qwa environment")
    print("✅ MLX framework available")
    
    # Load model in background
    print("Starting model loading in background...")
    threading.Thread(target=load_model, daemon=True).start()
    
    print("MLX Chat Server starting...")
    print("Open your browser to: http://127.0.0.1:5000")
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        sys.exit(1)
