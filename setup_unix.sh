#!/bin/bash
# Tooth Gender Classification - macOS/Linux Setup Script  
# Automatically detects and installs Python, conda, and dependencies

set -e  # Exit on any error

echo "=================================================="
echo "Tooth Gender Classification - Setup for macOS/Linux"
echo "=================================================="
echo

# Check if running from correct directory
if [[ ! -d "src" ]] || [[ ! -d "models" ]]; then
    echo "❌ ERROR: Please run this script from the tooth-gender-classification directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "[1/6] Checking system requirements..."

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="Linux"
fi
echo "Detected OS: $OS_TYPE"

# Check if Python is installed
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 is installed"
    python3 --version
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" &> /dev/null; then
        echo "✅ Python 3 is installed"
        python --version
        PYTHON_CMD="python"
    else
        echo "❌ Python 3 not found (found Python 2)"
        echo "Please install Python 3.8+ from:"
        if [[ "$OS_TYPE" == "macOS" ]]; then
            echo "  - https://www.python.org/downloads/"
            echo "  - Or using Homebrew: brew install python"
        else
            echo "  - https://www.python.org/downloads/"  
            echo "  - Or using your package manager:"
            echo "    Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
            echo "    CentOS/RHEL: sudo yum install python3 python3-pip"
        fi
        exit 1
    fi
else
    echo "❌ Python not found"
    echo "Please install Python 3.8+ from:"
    if [[ "$OS_TYPE" == "macOS" ]]; then
        echo "  - https://www.python.org/downloads/"
        echo "  - Or using Homebrew: brew install python"
    else
        echo "  - https://www.python.org/downloads/"
        echo "  - Or using your package manager:"
        echo "    Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
        echo "    CentOS/RHEL: sudo yum install python3 python3-pip"
    fi
    exit 1
fi

# Check Python version  
echo "[2/6] Verifying Python version..."
if $PYTHON_CMD -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" &> /dev/null; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8 or higher is required"
    $PYTHON_CMD --version
    exit 1
fi

# Check for pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip not found. Installing pip..."
    if [[ "$OS_TYPE" == "macOS" ]]; then
        echo "Please install pip using: python3 -m ensurepip --default-pip"
    else
        echo "Please install pip using your package manager:"
        echo "  Ubuntu/Debian: sudo apt install python3-pip"
        echo "  CentOS/RHEL: sudo yum install python3-pip"
    fi
    exit 1
else
    echo "✅ pip is available"
fi

# Check if conda is available
echo "[3/6] Checking for conda..."
if command -v conda &> /dev/null; then
    echo "✅ Conda is available"
    conda --version
    USE_CONDA=1
else
    echo "❌ Conda not found, using venv instead"
    USE_CONDA=0
fi

# Create virtual environment
echo "[4/6] Setting up virtual environment..."

if [[ $USE_CONDA -eq 1 ]]; then
    # Using conda
    if conda env list | grep -q "tooth-gender-class"; then
        echo "✅ Conda environment 'tooth-gender-class' already exists"
    else
        echo "Creating conda environment..."
        conda create -n tooth-gender-class python=3.9 -y
        echo "✅ Conda environment created successfully"
    fi
    
    echo "Activating conda environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate tooth-gender-class
    PYTHON_CMD="python"
    
else
    # Using venv
    if [[ -d "venv" ]]; then
        echo "✅ Virtual environment already exists"
    else
        echo "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        echo "✅ Virtual environment created successfully"
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"
fi

# Install dependencies
echo "[5/6] Installing required packages..."
echo "This may take a few minutes..."

$PYTHON_CMD -m pip install --upgrade pip

# Install packages from requirements if available
if [[ -f "requirements.txt" ]]; then
    echo "Installing from requirements.txt..."
    $PYTHON_CMD -m pip install -r requirements.txt
else
    echo "Installing individual packages..."
    $PYTHON_CMD -m pip install pandas numpy scikit-learn imbalanced-learn
    $PYTHON_CMD -m pip install xgboost lightgbm matplotlib seaborn  
    $PYTHON_CMD -m pip install joblib openpyxl xlsxwriter
fi

echo "✅ Dependencies installed successfully"

# Verify installation
echo "[6/6] Verifying installation..."
if $PYTHON_CMD -c "import pandas, numpy, sklearn, joblib; print('✅ Core packages imported successfully')" &> /dev/null; then
    echo "✅ Package verification successful"
else
    echo "❌ Package verification failed"
    exit 1
fi

echo
echo "=================================================="
echo "✅ Setup completed successfully!"
echo "=================================================="
echo

# Check if model files exist
if [[ -f "models/current/model.pkl" ]]; then
    echo "✅ Model files found - Ready to make predictions"
else
    echo "❌ Model files not found in models/current/"
    echo "You may need to train the model first using:"
    echo "  python src/train.py"
fi

echo
echo "Choose how to run the application:"
echo "1. Launch GUI application"
echo "2. Launch command line interface"
echo "3. Exit"
echo
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Launching GUI application..."
        $PYTHON_CMD src/gui_app.py
        ;;
    2)
        echo "Launching command line interface..."
        $PYTHON_CMD src/predict_working.py
        ;;
    *)
        echo "Goodbye!"
        ;;
esac