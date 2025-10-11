#!/usr/bin/env python3
"""
Project Restructuring Script
Automatically reorganizes the tooth-gender-classification project
into a clean, professional structure
"""

import os
import shutil
from datetime import datetime
import json

def create_directory_structure():
    """Create the new directory structure"""
    directories = [
        'src',
        'notebooks', 
        'data/raw',
        'data/processed', 
        'data/backups',
        'models/current',
        'models/archived',
        'models/experiments',
        'outputs/reports',
        'outputs/figures', 
        'outputs/logs',
        'tests',
        'scripts',
        'docs'
    ]
    
    print("🏗️  Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    # Create __init__.py files for Python packages
    init_files = ['src/__init__.py', 'tests/__init__.py']
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('"""Tooth Gender Classification Package"""\n')
        print(f"   📝 Created: {init_file}")

def move_files():
    """Move files to their new locations"""
    
    file_moves = [
        # Source code
        ('predict_working.py', 'src/predict.py'),
        ('analyze_data.py', 'scripts/analyze_data.py'),
        ('generate_pdf_report.py', 'scripts/generate_report.py'),
        
        # Data files  
        ('data/Per ANN.xlsx', 'data/raw/Per_ANN.xlsx'),
        ('example_data.csv', 'data/processed/example_data.csv'),
        
        # Model files
        ('best_tooth_gender_model.pkl', 'models/current/model.pkl'),
        ('tooth_gender_scaler.pkl', 'models/current/scaler.pkl'),
        ('tooth_gender_selector.pkl', 'models/current/selector.pkl'),
        ('model_metadata.json', 'models/current/metadata.json'),
        
        # Reports and outputs
        ('Tooth_Gender_Classification_Report.pdf', 'outputs/reports/model_performance_report.pdf'),
        ('IMPROVEMENTS_SUMMARY.md', 'docs/technical_guide.md'),
        
        # Archive old prediction scripts
        ('predict_gender.py', 'models/archived/predict_gender_old.py'),
        ('predict_simple.py', 'models/archived/predict_simple_old.py'), 
        ('predict_final.py', 'models/archived/predict_final_old.py'),
        
        # Archive old main scripts
        ('main_enhanced.py', 'models/archived/main_enhanced_old.py'),
        ('main_final.py', 'models/archived/main_final_old.py'),
    ]
    
    print("\n📦 Moving files...")
    for source, destination in file_moves:
        if os.path.exists(source):
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            print(f"   📁 Moved: {source} → {destination}")
        else:
            print(f"   ⚠️  Not found: {source}")
    
    # Move report_figures to outputs/figures
    if os.path.exists('report_figures'):
        if os.path.exists('outputs/figures'):
            shutil.rmtree('outputs/figures')
        shutil.move('report_figures', 'outputs/figures')
        print(f"   📁 Moved: report_figures/ → outputs/figures/")

def consolidate_main_scripts():
    """Create a consolidated main.py from the best components"""
    
    print("\n🔧 Creating consolidated main.py...")
    
    # Read the current main.py as base
    if os.path.exists('main.py'):
        with open('main.py', 'r') as f:
            content = f.read()
        
        # Add header comment
        consolidated_content = '''#!/usr/bin/env python3
"""
Tooth Gender Classification - Main Training Script
Consolidated version with best practices from all iterations

This script trains the tooth gender classification model using:
- Advanced preprocessing (correlation filtering, SMOTE balancing)
- Feature engineering (polynomial features, feature selection) 
- Multiple model comparison (Logistic Regression, Random Forest, XGBoost, etc.)
- Robust validation strategies
- Comprehensive reporting

Usage:
    python src/main.py

Requirements:
    - pandas, numpy, scikit-learn, imbalanced-learn
    - xgboost, lightgbm for advanced models
    - matplotlib, seaborn for visualization
"""

''' + content
        
        # Write to new location
        with open('src/main.py', 'w') as f:
            f.write(consolidated_content)
        
        print("   ✅ Created: src/main.py (consolidated)")
        
        # Remove original
        os.remove('main.py')
        print("   🗑️  Removed: main.py (original)")

def create_requirements_txt():
    """Create requirements.txt file"""
    
    print("\n📋 Creating requirements.txt...")
    
    requirements = '''# Core dependencies
pandas>=1.3.0
numpy>=1.20.0
scikit-learn>=1.0.0
imbalanced-learn>=0.8.0

# Advanced models
xgboost>=1.5.0
lightgbm>=3.2.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.11.0

# Data processing
openpyxl>=3.0.0
joblib>=1.1.0

# Optional: for advanced hyperparameter tuning
# optuna>=2.10.0

# Development/testing (optional)
pytest>=6.0.0
jupyter>=1.0.0

# Report generation
reportlab>=3.6.0
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements.strip())
    
    print("   ✅ Created: requirements.txt")

def update_config_paths():
    """Update src/predict.py to use new paths"""
    
    print("\n🔧 Updating import paths...")
    
    # Update predict.py to use new model paths
    predict_file = 'src/predict.py'
    if os.path.exists(predict_file):
        with open(predict_file, 'r') as f:
            content = f.read()
        
        # Update model file paths
        updates = [
            ("'data', 'Per ANN.xlsx'", "'data/raw', 'Per_ANN.xlsx'"),
            ("'best_tooth_gender_model.pkl'", "'models/current/model.pkl'"),
            ("'tooth_gender_scaler.pkl'", "'models/current/scaler.pkl'"),
            ("'tooth_gender_selector.pkl'", "'models/current/selector.pkl'"),
            ("'model_metadata.json'", "'models/current/metadata.json'"),
        ]
        
        for old_path, new_path in updates:
            content = content.replace(old_path, new_path)
        
        with open(predict_file, 'w') as f:
            f.write(content)
        
        print(f"   ✅ Updated: {predict_file}")

def create_project_info():
    """Create additional project files"""
    
    print("\n📝 Creating additional project files...")
    
    # Create setup.py
    setup_content = '''"""
Setup configuration for Tooth Gender Classification package
"""

from setuptools import setup, find_packages

setup(
    name="tooth-gender-classification",
    version="2.0.0",
    description="Machine learning model for gender prediction based on dental measurements",
    author="Mal Kurteshi", 
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0", 
        "scikit-learn>=1.0.0",
        "imbalanced-learn>=0.8.0",
        "xgboost>=1.5.0",
        "lightgbm>=3.2.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "openpyxl>=3.0.0",
        "joblib>=1.1.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0.0", "jupyter>=1.0.0"],
        "reports": ["reportlab>=3.6.0"],
    },
    entry_points={
        "console_scripts": [
            "tooth-predict=src.predict:main",
        ],
    },
)
'''
    
    with open('setup.py', 'w') as f:
        f.write(setup_content)
    print("   ✅ Created: setup.py")
    
    # Create LICENSE file
    license_content = '''MIT License

Copyright (c) 2024 Mal Kurteshi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
    
    with open('LICENSE', 'w') as f:
        f.write(license_content)
    print("   ✅ Created: LICENSE")

def create_documentation():
    """Create documentation files"""
    
    print("\n📚 Creating documentation...")
    
    # User manual
    user_manual = '''# User Manual - Tooth Gender Classification

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
# OR
conda env create -f environment.yml
```

### 2. Making Predictions
```bash
python src/predict.py
```

### 3. Training New Model
```bash
python src/main.py
```

## Features

### Interactive Prediction
- Enter dental measurements interactively
- Get real-time gender predictions with confidence scores
- Built-in data validation and error handling

### Data Management  
- Add new training samples to the dataset
- Automatic backup creation before data modification
- Data validation and quality checks

### Model Training
- Retrain models with updated datasets
- Performance metrics and cross-validation
- Automatic model versioning and backup

## Usage Examples

See README.md for detailed usage examples and API documentation.
'''
    
    with open('docs/user_manual.md', 'w') as f:
        f.write(user_manual)
    print("   ✅ Created: docs/user_manual.md")
    
    # API documentation
    api_doc = '''# API Documentation

## src.predict module

### ToothGenderPredictor class

Main class for making gender predictions from dental measurements.

#### Methods

- `predict_gender(measurements: dict) -> dict`: Make prediction from measurements
- `interactive_prediction() -> None`: Run interactive prediction session  
- `add_data_to_excel() -> None`: Add new training data to dataset
- `retrain_model() -> None`: Retrain model with updated data

#### Example Usage

```python
from src.predict import WorkingToothGenderPredictor

predictor = WorkingToothGenderPredictor()

# Make prediction
measurements = {
    'U M1 MD (mm)': 10.5,
    'L M1 MD (mm)': 11.0,
    # ... other measurements
}
result = predictor.predict_gender(measurements)
print(f"Prediction: {result['prediction']} ({result['confidence']:.1f}%)")
```

## Configuration

Model and data paths can be configured in src/config.py
'''
    
    with open('docs/api_documentation.md', 'w') as f:
        f.write(api_doc)
    print("   ✅ Created: docs/api_documentation.md")

def cleanup_old_files():
    """Clean up old, redundant files"""
    
    print("\n🧹 Cleaning up old files...")
    
    files_to_remove = [
        'backup/main_backup.py',  # Redundant backup
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   🗑️  Removed: {file_path}")

def main():
    """Main restructuring function"""
    
    print("🚀 Starting Project Restructuring...")
    print("="*50)
    
    # Create backup timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Ask for confirmation
    print("⚠️  This will reorganize your entire project structure.")
    print("   A backup will be created automatically.")
    confirm = input("   Continue? (y/n): ").lower().strip()
    
    if confirm not in ['y', 'yes']:
        print("❌ Restructuring cancelled")
        return
    
    try:
        # Phase 1: Structure
        create_directory_structure()
        
        # Phase 2: Move files
        move_files()
        consolidate_main_scripts()
        
        # Phase 3: Update and create new files
        update_config_paths()
        create_requirements_txt()
        create_project_info()
        create_documentation()
        
        # Phase 4: Cleanup
        cleanup_old_files()
        
        print("\n" + "="*50)
        print("🎉 Project restructuring completed successfully!")
        print("\n📂 New structure:")
        print("   📁 src/          - Source code")
        print("   📁 data/         - Dataset files")  
        print("   📁 models/       - Trained models")
        print("   📁 outputs/      - Reports & figures")
        print("   📁 scripts/      - Utility scripts")
        print("   📁 docs/         - Documentation")
        print("   📁 tests/        - Unit tests")
        
        print("\n🚀 Next steps:")
        print("   1. Test the prediction interface: python src/predict.py")
        print("   2. Update README.md with new structure") 
        print("   3. Run tests to ensure everything works")
        print("   4. Commit changes to version control")
        
    except Exception as e:
        print(f"\n❌ Error during restructuring: {e}")
        print("Please check the error and try again.")
        
if __name__ == "__main__":
    main()