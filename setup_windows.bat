@echo off
REM Tooth Gender Classification - Windows Setup Script
REM Automatically detects and installs Python, conda, and dependencies

echo ==================================================
echo Tooth Gender Classification - Setup for Windows
echo ==================================================
echo.

REM Check if running from correct directory
if not exist "src" (
    echo ERROR: Please run this script from the tooth-gender-classification directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo [1/6] Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python is already installed
    python --version
) else (
    echo ❌ Python not found
    echo.
    echo Python 3.8+ is required for this application.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check Python version
echo [2/6] Verifying Python version...
python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python 3.8 or higher is required
    python --version
    pause
    exit /b 1
) else (
    echo ✓ Python version is compatible
)

REM Check if conda is available
echo [3/6] Checking for conda...
conda --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Conda is available
    conda --version
    set USE_CONDA=1
) else (
    echo ❌ Conda not found, using pip instead
    set USE_CONDA=0
)

REM Create virtual environment
echo [4/6] Setting up virtual environment...

if %USE_CONDA% EQU 1 (
    REM Using conda
    conda env list | findstr "tooth-gender-class" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Conda environment 'tooth-gender-class' already exists
    ) else (
        echo Creating conda environment...
        conda create -n tooth-gender-class python=3.9 -y
        if %ERRORLEVEL% NEQ 0 (
            echo ❌ Failed to create conda environment
            pause
            exit /b 1
        )
        echo ✓ Conda environment created successfully
    )
    
    echo Activating conda environment...
    call conda activate tooth-gender-class
    
) else (
    REM Using venv
    if exist "venv" (
        echo ✓ Virtual environment already exists
    ) else (
        echo Creating virtual environment...
        python -m venv venv
        if %ERRORLEVEL% NEQ 0 (
            echo ❌ Failed to create virtual environment
            pause
            exit /b 1
        )
        echo ✓ Virtual environment created successfully
    )
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo [5/6] Installing required packages...
echo This may take a few minutes...

python -m pip install --upgrade pip

REM Install packages from requirements if available
if exist "requirements.txt" (
    echo Installing from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo Installing individual packages...
    python -m pip install pandas numpy scikit-learn imbalanced-learn
    python -m pip install xgboost lightgbm matplotlib seaborn
    python -m pip install joblib openpyxl xlsxwriter
)

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install some packages
    echo Please check the error messages above
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully

REM Verify installation
echo [6/6] Verifying installation...
python -c "import pandas, numpy, sklearn, joblib; print('✓ Core packages imported successfully')"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Package verification failed
    pause
    exit /b 1
)

echo.
echo ==================================================
echo ✓ Setup completed successfully!
echo ==================================================
echo.

REM Check if model files exist
if exist "models\current\model.pkl" (
    echo ✓ Model files found - Ready to make predictions
) else (
    echo ❌ Model files not found in models\current\
    echo You may need to train the model first using:
    echo   python src\train.py
)

echo.
echo Choose how to run the application:
echo 1. Launch GUI application
echo 2. Launch command line interface  
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Launching GUI application...
    python src\gui_app.py
) else if "%choice%"=="2" (
    echo Launching command line interface...
    python src\predict_working.py
) else (
    echo Goodbye!
)

pause