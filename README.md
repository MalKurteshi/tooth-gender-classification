# Tooth Gender Classification

This repository contains a complete machine learning pipeline that predicts gender based on dental measurements using advanced preprocessing, feature engineering, and ensemble methods.

## 🎯 Project Overview

- **Objective:** Predict gender using dental measurement features from tooth specifications
- **Language:** Python 3.9+
- **Best Performance:** 100% cross-validation accuracy, 62.5% test accuracy
- **Model Type:** Enhanced Logistic Regression with advanced preprocessing
- **Dataset:** 80 samples with 25 dental measurements

## 📊 Model Performance Results

### Final Model Performance:
- **Best Model**: Logistic Regression with advanced preprocessing
- **Cross-validation accuracy**: 100.0% ± 0.0%  
- **Test accuracy**: 62.5%
- **AUC Score**: 0.733
- **Features Used**: 21 original features + 28 polynomial interaction terms
- **Selected Features**: 15 (via SelectKBest)

### Key Improvements Implemented:
- ✅ Correlation analysis and multicollinearity removal
- ✅ SMOTE balancing for class imbalance
- ✅ PowerTransformer scaling for skewness
- ✅ Polynomial feature engineering
- ✅ SelectKBest feature selection
- ✅ Robust cross-validation strategies
- ✅ Ensemble methods (Voting, Stacking)
- ✅ **NEW**: Interactive data entry system
- ✅ **NEW**: Automated model retraining
- ✅ **NEW**: Professional project structure with clean organization

## 🖥️ Desktop Application Features

### Cross-Platform Support
- **Windows 10+:** Native .exe executable with installer
- **macOS 10.14+:** Native .app bundle for Applications folder
- **Linux (Ubuntu 18.04+):** Native binary with desktop integration
- **Universal:** Python-based GUI works on all platforms

### User-Friendly Interface
- **Intuitive GUI:** No command line knowledge required
- **Smart Input Validation:** Prevents invalid entries
- **CSV Import:** Load measurements from spreadsheet files
- **Real-time Results:** Instant predictions with confidence scores
- **One-Click Setup:** Automatic dependency installation

### Professional Features
- **Standalone Executables:** No Python installation required
- **Desktop Integration:** Native look and feel on each platform
- **Batch Processing:** Handle multiple predictions efficiently
- **Data Management:** Add training data and retrain models
- **Comprehensive Reports:** Generate detailed analysis documents

## 🗂️ Project Structure

```
tooth-gender-classification/
├── README.md                           # Main project documentation
├── LICENSE                             # MIT License
├── requirements.txt                    # Python dependencies (pip)
├── environment.yml                     # Conda environment
├── setup.py                           # Package setup configuration
├── .gitignore                         # Git ignore rules
│
├── src/                               # 🔧 Source code
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # Main training script (consolidated)
│   ├── predict_working.py             # ✅ CLI prediction interface
│   └── gui_app.py                     # 🖥️ Desktop GUI application
│
├── data/                              # 📊 Data files
│   ├── raw/                          # Original, immutable data
│   │   └── Per_ANN.xlsx              # Original dataset
│   ├── processed/                    # Processed data
│   │   └── example_data.csv          # Sample input data
│   └── backups/                      # Automatic data backups
│
├── models/                           # 🤖 Trained models
│   ├── current/                      # Current production model
│   │   ├── model.pkl                 # Trained model
│   │   ├── scaler.pkl                # Feature scaler
│   │   ├── selector.pkl              # Feature selector
│   │   └── metadata.json             # Model information
│   ├── archived/                     # Previous model versions
│   └── experiments/                  # Experimental models
│
├── outputs/                          # 📈 Generated outputs
│   ├── reports/                      # Analysis reports
│   │   └── model_performance_report.pdf
│   ├── figures/                      # Generated plots & visualizations
│   └── logs/                         # Training logs
│
├── scripts/                          # 🛠️ Utility scripts
│   ├── analyze_data.py               # Data analysis
│   └── generate_report.py            # Report generation
│
├── 🖥️ Desktop Application Files:
│   ├── launch.py                     # Universal launcher
│   ├── setup_windows.bat             # Windows setup script  
│   ├── setup_unix.sh                 # macOS/Linux setup script
│   ├── build_executable.py           # Executable builder
│   └── USER_GUIDE.md                 # End-user documentation
│
├── docs/                             # 📚 Documentation
│   ├── technical_guide.md            # Technical improvements guide
│   ├── user_manual.md                # User manual
│   └── api_documentation.md          # API documentation
│
├── tests/                            # 🧪 Unit tests
│   └── __init__.py                   # Test package initialization
```

## 🏢 Professional Structure Benefits

The project has been restructured following Python best practices:

### 💯 **Code Organization**
- **Separation of Concerns**: Clear distinction between source code, data, models, and outputs
- **Modular Design**: Consolidated and organized code modules
- **Scalable Architecture**: Easy to extend and maintain

### 🔧 **Development Benefits**
- **Standard Structure**: Follows Python packaging conventions
- **Version Control**: Better organization for Git tracking
- **Collaboration**: Clear structure for team development
- **Documentation**: Comprehensive docs in dedicated directory

### 💾 **Data Management**
- **Immutable Raw Data**: Protected original dataset in `data/raw/`
- **Automatic Backups**: Safe data modifications with backup system
- **Processed Data**: Separate location for derived datasets

### 🤖 **Model Management**
- **Version Control**: Current vs archived model versions
- **Metadata Tracking**: Complete model information and performance
- **Experiment Tracking**: Dedicated space for model experiments

## 🚀 Quick Start

### 🖥️ For Desktop GUI Users (Recommended)

**Automatic Setup:**
```bash
# Windows: Run as administrator
setup_windows.bat

# macOS/Linux: 
chmod +x setup_unix.sh
./setup_unix.sh

# Universal launcher
python launch.py
```

**Manual Setup:**
1. Download the project files
2. Ensure Python 3.8+ is installed
3. Run the setup script for your operating system
4. Launch with `python launch.py gui`

### 💻 For Developers

```bash
# Clone the repository
git clone https://github.com/MalKurteshi/tooth-gender-classification.git
cd tooth-gender-classification

# Create conda environment
conda env create -f environment.yml
conda activate tooth-gender-classification

# Or install with pip
pip install pandas numpy scikit-learn matplotlib seaborn imbalanced-learn xgboost lightgbm joblib openpyxl
```

### 2. Train the Model
```bash
# Run the consolidated training script
python src/main.py
```

### 3. Make Predictions
```bash
# GUI Application (Recommended)
python launch.py gui
# or
python src/gui_app.py

# Command Line Interface
python src/predict_working.py
```

### 4. Generate Reports
```bash
# Generate comprehensive analysis report
python scripts/generate_report.py
```

### 5. Building Standalone Executables
```bash
# Install PyInstaller
pip install pyinstaller

# Build executables for current platform
python build_executable.py

# Build specific versions
python build_executable.py --gui      # GUI only
python build_executable.py --cli      # CLI only
```

### 6. Generate Reports
```bash
# Generate comprehensive PDF report
python scripts/generate_report.py
```

## 🦷 Required Input Features (21 measurements)

The model requires the following dental measurements in millimeters:

| # | Feature Name | Description |
|---|--------------|-------------|
| 1 | U M2 MD (mm) | Upper second molar mesio-distal |
| 2 | U M1 MD (mm) | Upper first molar mesio-distal |
| 3 | U P2 MD (mm) | Upper second premolar mesio-distal |
| 4 | U P1 MD (mm) | Upper first premolar mesio-distal |
| 5 | 13 BO (mm) | Upper right canine bucco-oral |
| 6 | 13 MD (mm) | Upper right canine mesio-distal |
| 7 | 12MD (mm) | Upper right lateral incisor mesio-distal |
| 8 | 11 MD (mm) | Upper right central incisor mesio-distal |
| 9 | 22 MD (mm) | Upper left lateral incisor mesio-distal |
| 10 | 23 MD (mm) | Upper left canine mesio-distal |
| 11 | L M2 MD (mm) | Lower second molar mesio-distal |
| 12 | L M1 MD (mm) | Lower first molar mesio-distal |
| 13 | L P2 MD (mm) | Lower second premolar mesio-distal |
| 14 | L P1 MD (mm) | Lower first premolar mesio-distal |
| 15 | 43 BO (mm) | Lower right canine bucco-oral |
| 16 | 43 MD (mm) | Lower right canine mesio-distal |
| 17 | 42MD (mm) | Lower right lateral incisor mesio-distal |
| 18 | 41 MD (mm) | Lower right central incisor mesio-distal |
| 19 | 32 MD (mm) | Lower left lateral incisor mesio-distal |
| 20 | 33 MD (mm) | Lower left canine mesio-distal |
| 21 | Harku interkanin mandibullar | Mandibular intercanine width |

**Notes:**
- MD = Mesio-Distal (length measurement)
- BO = Bucco-Oral (width measurement)  
- Typical range: 5-15mm for most measurements
- Missing values are automatically handled with default value (7.5mm)

## 🔄 Enhanced Workflow

The system now supports a complete machine learning lifecycle:

### 1. **Make Predictions** 🎯
- Interactive prediction with all 21 dental measurements
- Real-time confidence scores and probability breakdown
- User-friendly input validation and error handling

### 2. **Expand Training Data** 📝
- Add new dental measurement samples directly to the dataset
- Automatic data validation and format checking
- Automatic backup creation before dataset modification
- Seamless integration with existing Excel structure

### 3. **Retrain Model** 🔄
- Retrain the model with updated dataset including new samples
- Real-time performance metrics and cross-validation scores
- Automatic backup of previous model versions
- Option to save new model as main production model

### 4. **Continuous Improvement** 📈
- Iterative model improvement through new data collection
- Performance tracking across model versions
- Data-driven model enhancement workflow

## 💻 Usage Examples

### Desktop GUI Application
```bash
# Launch GUI with universal launcher
python launch.py

# Or launch directly
python src/gui_app.py

# Features:
# - Tabbed interface with Prediction, Data Entry, and Settings
# - Input validation and CSV import
# - Real-time predictions with confidence scores
# - Model information and dependency checking
```

### Command Line Interface
```python
# Run the CLI prediction interface
python src/predict_working.py

# Available options:
# 1. Make prediction - Interactive prediction session
# 2. Quick test - Test with sample data
# 3. Add new data to dataset - Add training data
# 4. Retrain model - Update model with new data
# 5. Exit

# Example prediction session:
# 1. U M2 MD (mm): 9.5
# 2. U M1 MD (mm): 10.2
# ... (continue for all 21 features)
# 
# Result: Male (85.3% confidence)
```

### Adding New Training Data
```python
# Select option 3 from the main menu
# Enter all 21 dental measurements
# Specify the actual gender (M/F)
# Data is automatically added to Per ANN.xlsx
# Automatic backup is created before modification
```

### Retraining the Model
```python
# Select option 4 from the main menu
# Confirm retraining (replaces current model)
# Model retrains on updated dataset
# Cross-validation results are displayed
# Option to save new model files
```

## 📈 Model Details

### Preprocessing Pipeline:
1. **Data Cleaning**: Handle missing values, convert data types
2. **Correlation Filtering**: Remove features with >95% correlation
3. **SMOTE Balancing**: Address class imbalance (62.5% vs 37.5%)
4. **Feature Engineering**: Create polynomial interaction terms
5. **Scaling**: PowerTransformer for handling skewness
6. **Feature Selection**: SelectKBest with f_classif scoring

### Models Evaluated:
- Logistic Regression ⭐ (Best: 100% CV accuracy)
- Random Forest (77.5% CV accuracy)
- Extra Trees (77.5% CV accuracy) 
- XGBoost (95.6% CV accuracy)
- LightGBM (64.4% CV accuracy)
- SVM (77.2% CV accuracy)
- K-Nearest Neighbors (70.0% CV accuracy)
- Ensemble Methods (Voting, Stacking)

### Key Features Identified:
- **43 MD (mm)** - Lower right canine mesio-distal (20.6% importance)
- **33 MD (mm)** - Lower left canine mesio-distal (19.9% importance)
- **43 BO (mm)** - Lower right canine bucco-oral (12.5% importance)
- **13 BO (mm)** - Upper right canine bucco-oral (10.8% importance)
- **Various polynomial interactions** between these key measurements

## 📊 Generated Reports

- **`Tooth_Gender_Classification_Report.pdf`**: Complete analysis with visualizations
- **`IMPROVEMENTS_SUMMARY.md`**: Detailed technical improvements documentation
- **`report_figures/`**: Individual plots and visualizations

## 🔬 Technical Specifications

- **Python Version**: 3.9+
- **Key Libraries**: scikit-learn, pandas, numpy, imbalanced-learn, xgboost, lightgbm
- **Validation Strategy**: Repeated Stratified K-Fold (5 folds × 5 repeats)
- **Model Persistence**: joblib for model serialization
- **Visualization**: matplotlib, seaborn for plots
- **Reporting**: ReportLab for PDF generation

## ⚠️ Important Notes

- Dataset size (80 samples) limits model complexity
- Perfect cross-validation score suggests potential overfitting
- Model is research-grade; clinical validation recommended
- Default values (7.5mm) used for missing measurements
- Model works best with complete measurement sets
- **NEW**: Data entry creates automatic backups before modification
- **NEW**: Model retraining preserves old model versions
- **NEW**: Cross-validation adapts to dataset size automatically

## 🏆 Performance Comparison

| Metric | Original Model | Enhanced Model | Improvement |
|--------|---------------|----------------|-------------|
| CV Accuracy | 77.5% ± 6.4% | 100.0% ± 0.0% | +22.5 pp |
| Test Accuracy | 69.0% | 62.5% | -6.5 pp |
| AUC Score | ~0.70 | 0.733 | +0.033 |
| Validation Robustness | Basic | Multiple strategies | ✅ |
| Feature Engineering | Minimal | Advanced | ✅ |
| Model Interpretability | Limited | Comprehensive | ✅ |

## 📝 License

[MIT](LICENSE)

## 👨‍💻 Author

**Mal Kurteshi**
- Enhanced machine learning pipeline implementation
- Advanced feature engineering and model optimization
- Comprehensive reporting and visualization system

---

*Last Updated: October 2025*
*Model Version: 2.0 (Enhanced)*
