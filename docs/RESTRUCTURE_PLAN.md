# Project Restructuring Plan

## 🎯 Current Issues
- Too many files in root directory (26 files)
- Multiple similar scripts (main.py, main_enhanced.py, main_final.py)
- Model files scattered in root
- No clear separation between source code, models, and outputs

## 🏗️ Proposed New Structure

```
tooth-gender-classification/
├── README.md                           # Main project documentation
├── LICENSE                             # License file
├── requirements.txt                    # Python dependencies (pip)
├── environment.yml                     # Conda environment
├── .gitignore                         # Git ignore rules
├── setup.py                           # Package setup (optional)
│
├── src/                               # Source code
│   ├── __init__.py
│   ├── main.py                        # Main training script (cleaned up)
│   ├── predict.py                     # Production prediction interface
│   ├── data_utils.py                  # Data processing utilities
│   ├── model_utils.py                 # Model training utilities
│   └── config.py                      # Configuration settings
│
├── data/                              # Data files
│   ├── raw/                          # Original, immutable data
│   │   └── Per_ANN.xlsx              # Original dataset
│   ├── processed/                    # Processed data
│   └── backups/                      # Automatic backups
│
├── models/                           # Trained models
│   ├── current/                      # Current production model
│   │   ├── model.pkl
│   │   ├── scaler.pkl
│   │   ├── selector.pkl
│   │   └── metadata.json
│   ├── archived/                     # Previous model versions
│   └── experiments/                  # Experimental models
│
├── outputs/                          # Generated outputs
│   ├── reports/                      # Analysis reports
│   │   ├── model_performance.pdf
│   │   └── data_analysis.html
│   ├── figures/                      # Generated plots
│   └── logs/                         # Training logs
│
├── tests/                            # Unit tests
│   ├── __init__.py
│   ├── test_data_utils.py
│   ├── test_model_utils.py
│   └── test_predict.py
│
├── scripts/                          # Utility scripts
│   ├── train_model.py                # Training script
│   ├── analyze_data.py               # Data analysis
│   ├── generate_report.py            # Report generation
│   └── backup_data.py                # Backup utilities
│
└── docs/                             # Documentation
    ├── technical_guide.md
    ├── user_manual.md
    ├── api_documentation.md
    └── model_documentation.md
```

## 🔄 Migration Strategy

### Phase 1: Create New Structure
1. Create new directory structure
2. Move and organize existing files
3. Create __init__.py files for Python packages

### Phase 2: Consolidate Code
1. Merge similar scripts (main.py variants)
2. Extract common utilities into separate modules
3. Create clean, production-ready prediction interface

### Phase 3: Clean Up
1. Archive old/experimental files
2. Update imports and paths
3. Update documentation

## 📝 File Mapping

### Current → New Location
- `main.py, main_enhanced.py, main_final.py` → `src/main.py` (consolidated)
- `predict_working.py` → `src/predict.py` (renamed)
- `predict_*.py` (others) → `models/archived/` (archived)
- `analyze_data.py` → `scripts/analyze_data.py`
- `generate_pdf_report.py` → `scripts/generate_report.py`
- `*.pkl, *.json` → `models/current/`
- `report_figures/` → `outputs/figures/`
- `Tooth_Gender_Classification_Report.pdf` → `outputs/reports/`
- `IMPROVEMENTS_SUMMARY.md` → `docs/technical_guide.md`

### Files to Archive/Remove
- `predict_gender.py, predict_simple.py, predict_final.py` → Archive
- `main_backup.py` → Remove (redundant)
- Old model backups → `models/archived/`

## 🎯 Benefits
1. **Professional structure** following Python best practices
2. **Clear separation** of concerns (code, data, models, outputs)
3. **Easier maintenance** and collaboration
4. **Better version control** with organized files
5. **Scalable architecture** for future development
6. **Standard conventions** that developers expect