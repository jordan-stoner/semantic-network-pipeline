#!/usr/bin/env python3

import os
import sys
import platform
import json
import subprocess
import webbrowser
import time
import threading
import socket
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

def check_mlx_compatibility():
    """Check if system can run MLX"""
    if platform.system() != "Darwin":
        print("❌ MLX requires macOS with Apple Silicon")
        return False
    
    try:
        import mlx
        return True
    except ImportError:
        print("❌ MLX not available - install with: pip install mlx")
        return False

app = Flask(__name__)

def check_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Quick timeout
            result = s.connect_ex(('127.0.0.1', port))
            return result != 0  # Port is available if connection fails
    except:
        return True  # Assume available if check fails

def discover_models():
    """Discover available MLX models in model/model directory"""
    models = []
    
    # Only scan the centralized model directory
    model_dir = os.path.join(os.path.dirname(__file__), "model", "model")
    
    if os.path.exists(model_dir):
        for item in os.listdir(model_dir):
            item_path = os.path.join(model_dir, item)
            if os.path.isdir(item_path):
                # Check if it's a valid MLX model directory
                config_file = os.path.join(item_path, "config.json")
                safetensors_files = [f for f in os.listdir(item_path) if f.endswith('.safetensors')]
                
                if os.path.exists(config_file) and safetensors_files:
                    # Check for tokenizer files
                    tokenizer_files = [f for f in os.listdir(item_path) if 'tokenizer' in f.lower()]
                    if tokenizer_files:
                        models.append({
                            "name": item,
                            "path": item_path,
                            "size": "Unknown"
                        })
    
    return models

def discover_lora_adapters(selected_model_name=None):
    """Discover available LoRA adapters, optionally filtered by model"""
    adapters = []
    adapter_base_dir = Path(__file__).parent / "model" / "adapters"
    
    if adapter_base_dir.exists():
        # Scan model-specific subdirectories
        for model_dir in adapter_base_dir.iterdir():
            if model_dir.is_dir() and model_dir.name.endswith('_lora'):
                # Extract model name from directory
                dir_model_name = model_dir.name.replace('_lora', '')
                
                # Skip if filtering and model doesn't match
                if selected_model_name and dir_model_name != selected_model_name:
                    continue
                
                # Look for our custom naming convention first (both .npz and .safetensors)
                custom_files = []
                for ext in ['*.npz', '*.safetensors']:
                    custom_files.extend([f for f in model_dir.glob(ext) if '_lora-' in f.name])
                
                for adapter_file in custom_files:
                    # Extract from filename using our naming convention
                    name_parts = adapter_file.stem.split('_lora-')
                    if len(name_parts) == 2:
                        model_name = name_parts[0]
                        descriptor_version = name_parts[1]
                        display_name = f"{model_name}: {descriptor_version}"
                    else:
                        display_name = adapter_file.stem
                    
                    adapters.append({
                        "name": display_name,
                        "path": str(adapter_file),
                        "size": f"{adapter_file.stat().st_size // 1024} KB",
                        "model": dir_model_name
                    })
                
                # If no custom named files, look for standard MLX-LM output
                if not custom_files:
                    adapters_file = model_dir / "adapters.safetensors"
                    if adapters_file.exists():
                        adapters.append({
                            "name": f"{dir_model_name}: LoRA Adapter",
                            "path": str(adapters_file),
                            "size": f"{adapters_file.stat().st_size // 1024} KB",
                            "model": dir_model_name
                        })
        
        # Also check for legacy adapters in root directory (only if no model filter)
        if not selected_model_name:
            legacy_files = list(adapter_base_dir.glob("*.npz")) + list(adapter_base_dir.glob("*.safetensors"))
            for adapter_file in legacy_files:
                adapters.append({
                    "name": f"Legacy: {adapter_file.stem}",
                    "path": str(adapter_file),
                    "size": f"{adapter_file.stat().st_size // 1024} KB",
                    "model": "unknown"
                })
    
    return adapters

@app.route('/')
def config_page():
    """Serve the configuration page"""
    models = discover_models()
    adapters = discover_lora_adapters()  # Get all adapters initially
    
    # Check if no models found
    no_models = len(models) == 0
    
    template = '''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLX Chat Configuration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {
            background: #0a0a0a;
            color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .config-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        .config-card {
            background: #1a1a1a;
            border: 2px solid #ff6b35;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
            max-width: 800px;
            width: 100%;
        }
        .config-title {
            color: #ff6b35;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
        }
        .section-title {
            color: #ff6b35;
            font-size: 1.2rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #ff6b35;
            padding-bottom: 0.5rem;
        }
        .model-option, .adapter-option {
            background: #2a2a2a;
            border: 1px solid #4a4a4a;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .model-option:hover, .adapter-option:hover {
            border-color: #ff6b35;
            background: #3a3a3a;
        }
        .model-option.selected, .adapter-option.selected {
            border-color: #ff6b35;
            background: #ff6b35;
            color: #0a0a0a;
        }
        .launch-btn {
            background: linear-gradient(135deg, #ff6b35, #ff4500);
            border: none;
            color: white;
            font-size: 1.2rem;
            font-weight: bold;
            padding: 1rem 2rem;
            border-radius: 10px;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .launch-btn i {
            margin-right: 10px;
        }
        .launch-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 53, 0.6);
        }
        .launch-btn:disabled {
            opacity: 0.6;
            transform: none;
            cursor: not-allowed;
        }
        .model-info {
            font-size: 0.9rem;
            color: #aaa;
            margin-top: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="config-container">
        <div class="config-card">
            <div class="config-title">
                <i class="bi bi-gear me-2"></i>MLX Chat Configuration
            </div>
            
            <div class="section-title">
                <i class="bi bi-cpu me-2"></i>Select Model
            </div>
            <div id="modelSelection">
                {% if models %}
                {% for model in models %}
                <div class="model-option" data-path="{{ model.path }}" onclick="selectModel(this)">
                    <div class="fw-bold">{{ model.name }}</div>
                    <div class="model-info">{{ model.path }}</div>
                </div>
                {% endfor %}
                {% else %}
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>No models found in model/model directory</strong>
                    <br><br>
                    To use MLX Chat, copy an MLX model to: <code>model/model/</code>
                    <br><br>
                    <small>Models should contain config.json and .safetensors files</small>
                </div>
                {% endif %}
            </div>
            
            <div class="section-title mt-4">
                <i class="bi bi-layers me-2"></i>LoRA Adapter (Optional)
            </div>
            <div id="adapterSelection">
                <div class="adapter-option selected" data-path="" onclick="selectAdapter(this)">
                    <div class="fw-bold">No Adapter</div>
                    <div class="model-info">Use base model without fine-tuning</div>
                </div>
                {% for adapter in adapters %}
                <div class="adapter-option" data-path="{{ adapter.path }}" onclick="selectAdapter(this)">
                    <div class="fw-bold">{{ adapter.name }}</div>
                    <div class="model-info">{{ adapter.path }} ({{ adapter.size }})</div>
                </div>
                {% endfor %}
            </div>
            
            <button id="launchBtn" class="btn launch-btn" onclick="launchChat()">
                <i class="bi bi-rocket-takeoff me-2"></i>Launch MLX Chat
            </button>
        </div>
    </div>

    <script>
        let selectedModel = null;
        let selectedAdapter = "";
        
        function selectModel(element) {
            // Remove previous selection
            document.querySelectorAll('.model-option').forEach(el => el.classList.remove('selected'));
            // Add selection to clicked element
            element.classList.add('selected');
            selectedModel = element.dataset.path;
            
            // Extract model name from path for adapter filtering
            const modelName = element.querySelector('.fw-bold').textContent;
            updateAdaptersForModel(modelName);
            updateLaunchButton();
        }
        
        async function updateAdaptersForModel(modelName) {
            try {
                const response = await fetch(`/get_adapters/${encodeURIComponent(modelName)}`);
                const adapters = await response.json();
                
                const adapterContainer = document.getElementById('adapterSelection');
                
                // Clear existing adapters except "No Adapter" option
                const noAdapterOption = adapterContainer.querySelector('.adapter-option[data-path=""]');
                adapterContainer.innerHTML = '';
                adapterContainer.appendChild(noAdapterOption);
                
                // Add compatible adapters
                adapters.forEach(adapter => {
                    const adapterDiv = document.createElement('div');
                    adapterDiv.className = 'adapter-option';
                    adapterDiv.dataset.path = adapter.path;
                    adapterDiv.onclick = () => selectAdapter(adapterDiv);
                    
                    adapterDiv.innerHTML = `
                        <div class="fw-bold">${adapter.name}</div>
                        <div class="model-info">${adapter.path} (${adapter.size})</div>
                    `;
                    
                    adapterContainer.appendChild(adapterDiv);
                });
                
                // Reset adapter selection to "No Adapter"
                selectAdapter(noAdapterOption);
                
                // Show message if no compatible adapters found
                if (adapters.length === 0) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'alert alert-info mt-2';
                    messageDiv.innerHTML = `
                        <i class="bi bi-info-circle me-2"></i>
                        No LoRA adapters found for <strong>${modelName}</strong>.
                        <br><small>Train a LoRA adapter for this model using create_lora.py</small>
                    `;
                    adapterContainer.appendChild(messageDiv);
                }
                
            } catch (error) {
                console.error('Error fetching adapters:', error);
            }
        }
        
        function selectAdapter(element) {
            // Remove previous selection
            document.querySelectorAll('.adapter-option').forEach(el => el.classList.remove('selected'));
            // Add selection to clicked element
            element.classList.add('selected');
            selectedAdapter = element.dataset.path;
        }
        
        function updateLaunchButton() {
            const btn = document.getElementById('launchBtn');
            btn.disabled = !selectedModel;
        }
        
        async function launchChat() {
            if (!selectedModel) return;
            
            const btn = document.getElementById('launchBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Starting MLX Chat...';
            
            try {
                const response = await fetch('/launch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        model_path: selectedModel,
                        adapter_path: selectedAdapter
                    })
                });
                
                if (response.ok) {
                    btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Launching...';
                    // Reduced wait time and add fallback
                    setTimeout(() => {
                        window.location.href = 'http://127.0.0.1:5000';
                    }, 6000);
                    
                    // Show manual link after delay
                    setTimeout(() => {
                        btn.innerHTML = '<i class="bi bi-arrow-right me-2"></i><a href="http://127.0.0.1:5000" style="color: white; text-decoration: none;">Go to Chat</a>';
                    }, 8000);
                } else {
                    throw new Error('Failed to launch');
                }
            } catch (error) {
                btn.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Launch Failed';
                btn.disabled = false;
                setTimeout(() => {
                    btn.innerHTML = '<i class="bi bi-rocket-takeoff me-2"></i>Launch MLX Chat';
                }, 3000);
            }
        }
        
        // Auto-select first model if available
        document.addEventListener('DOMContentLoaded', function() {
            const firstModel = document.querySelector('.model-option');
            if (firstModel) {
                selectModel(firstModel);
            }
        });
    </script>
</body>
</html>
    '''
    
    return render_template_string(template, models=models, adapters=adapters)

@app.route('/get_adapters/<model_name>')
def get_adapters_for_model(model_name):
    """Get LoRA adapters compatible with specific model"""
    adapters = discover_lora_adapters(model_name)
    return jsonify(adapters)

@app.route('/launch', methods=['POST'])
def launch_chat():
    """Launch the main chat application with selected configuration"""
    try:
        config = request.get_json()
        model_path = config.get('model_path')
        adapter_path = config.get('adapter_path', '')
        
        # Save configuration for web_chat.py to read
        config_file = Path(__file__).parent / "chat_config.json"
        with open(config_file, 'w') as f:
            json.dump({
                'model_path': model_path,
                'adapter_path': adapter_path
            }, f)
        
        # Check if port 5000 is available (warning only)
        if not check_port_available(5000):
            print("⚠️ Warning: Port 5000 may be in use")
        
        # Small delay to ensure any previous server is fully stopped
        time.sleep(2)
        
        # Start web_chat.py in background using conda run
        script_dir = os.path.dirname(os.path.abspath(__file__))
        web_chat_path = os.path.join(script_dir, 'web_chat.py')
        
        # Use conda run to ensure proper environment
        cmd = ['conda', 'run', '-n', 'mlx-qwa', 'python', web_chat_path]
        
        print(f"Starting web_chat.py with command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd, 
                cwd=script_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Give process time to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is not None:
                print("❌ web_chat.py process died during startup")
                return jsonify({'error': 'web_chat.py failed to start'}), 500
            
            print("✅ web_chat.py started successfully")
                
        except Exception as e:
            print(f"❌ Error starting web_chat.py: {e}")
            return jsonify({'error': f'Failed to start web_chat.py: {str(e)}'}), 500
        
        # Shutdown this configuration server after launching
        def shutdown_config_server():
            time.sleep(8)  # Reduced wait time
            print("MLX Chat configuration has stopped.")
            os._exit(0)  # Force exit the config server
        
        threading.Thread(target=shutdown_config_server, daemon=True).start()
        
        return jsonify({'status': 'launched'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def check_and_setup_environment():
    """Check for mlx-qwa environment and create if needed"""
    import subprocess
    
    # Check if we're already in mlx-qwa
    current_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    if current_env == 'mlx-qwa':
        print("✅ Running in mlx-qwa environment")
        return True
    
    print("⚠️ Not running in mlx-qwa environment")
    print("🔍 Checking if mlx-qwa environment exists...")
    
    # Check if mlx-qwa environment exists
    try:
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
        if 'mlx-qwa' in result.stdout:
            print("✅ mlx-qwa environment found")
            print("❌ Error: Must run from mlx-qwa conda environment")
            print("💡 Run: conda activate mlx-qwa && python config_launcher.py")
            return False
        else:
            print("❌ mlx-qwa environment not found")
            print("🚀 Run initial_setup.py first to create environment")
            return False
    except FileNotFoundError:
        print("❌ Error: conda not found. Please install Anaconda/Miniconda first.")
        return False

def create_mlx_qwa_environment():
    """Create the mlx-qwa conda environment with required packages"""
    import subprocess
    
    try:
        print("📦 Creating conda environment 'mlx-qwa' with Python 3.10...")
        
        # Create environment
        result = subprocess.run([
            'conda', 'create', '-n', 'mlx-qwa', 'python=3.10', '-y'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to create environment: {result.stderr}")
            return False
        
        print("✅ Environment created successfully")
        print("📦 Installing required packages from requirements.txt...")
        
        # Install from requirements.txt if it exists
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if os.path.exists(requirements_file):
            result = subprocess.run([
                'conda', 'run', '-n', 'mlx-qwa', 'pip', 'install', '-r', requirements_file
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️ Warning: Some packages failed to install: {result.stderr}")
                print("📦 Installing core packages individually...")
                
                # Fallback to individual package installation
                core_packages = ['flask', 'mlx', 'mlx-lm', 'nltk', 'python-docx', 'requests']
                for package in core_packages:
                    print(f"   Installing {package}...")
                    subprocess.run([
                        'conda', 'run', '-n', 'mlx-qwa', 'pip', 'install', package
                    ], capture_output=True, text=True)
            else:
                print("✅ All packages installed successfully")
        else:
            print("⚠️ requirements.txt not found, installing core packages...")
            core_packages = ['flask', 'mlx', 'mlx-lm', 'nltk', 'python-docx', 'requests']
            for package in core_packages:
                print(f"   Installing {package}...")
                subprocess.run([
                    'conda', 'run', '-n', 'mlx-qwa', 'pip', 'install', package
                ], capture_output=True, text=True)
        
        print("✅ Environment setup complete!")
        print("💡 Please restart the launcher - it will now use the mlx-qwa environment")
        return False  # Still need to restart in the environment
        
    except Exception as e:
        print(f"❌ Error creating environment: {e}")
        return False

def main():
    """Main configuration launcher"""
    print("🌋 MLX Chat Configuration")
    print("=" * 40)
    
    if not check_mlx_compatibility():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check and setup environment
    if not check_and_setup_environment():
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("✅ Running in mlx-qwa environment")
    print("🚀 Starting configuration server...")
    
    # Open browser after delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:5001')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("🌐 Configuration page: http://127.0.0.1:5001")
    app.run(host='127.0.0.1', port=5001, debug=False)

if __name__ == '__main__':
    main()
