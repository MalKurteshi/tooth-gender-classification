# User Manual - Tooth Gender Classification

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
