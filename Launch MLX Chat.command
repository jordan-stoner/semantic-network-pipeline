#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🌋 MLX Chat Launcher"
echo "===================="
echo "Initializing conda and environment..."

# Change to the script directory
cd "$SCRIPT_DIR"

# Initialize conda with multiple possible paths
if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    export PATH="/opt/anaconda3/bin:$PATH"
    source /opt/anaconda3/etc/profile.d/conda.sh
    echo "✅ Found conda at /opt/anaconda3"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    export PATH="$HOME/anaconda3/bin:$PATH"
    source $HOME/anaconda3/etc/profile.d/conda.sh
    echo "✅ Found conda at $HOME/anaconda3"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    export PATH="$HOME/miniconda3/bin:$PATH"
    source $HOME/miniconda3/etc/profile.d/conda.sh
    echo "✅ Found conda at $HOME/miniconda3"
else
    echo "❌ Error: Could not find conda installation"
    echo "Please install Anaconda or Miniconda first"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if mlx-qwa environment exists
if "$CONDA_EXE" env list | grep -q "mlx-qwa"; then
    echo "✅ mlx-qwa environment found"
    echo "🚀 Launching MLX Chat Configuration..."
    
    # Launch with conda run to ensure proper environment
    "$CONDA_EXE" run -n mlx-qwa python config_launcher.py
else
    echo "⚠️ mlx-qwa environment not found"
    echo "🚀 Run initial_setup.py first to create environment"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "MLX Chat configuration has stopped."
