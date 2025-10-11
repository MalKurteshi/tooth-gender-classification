# %%
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.model_selection import (
    train_test_split, cross_val_score, StratifiedKFold, 
    RepeatedStratifiedKFold, LeaveOneOut
)
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, RFECV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, VotingClassifier, 
    ExtraTreesClassifier, BaggingClassifier
)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbalancedPipeline

# Advanced models
import xgboost as xgb
import lightgbm as lgb

import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------
# 1️⃣ Load and Process Data
# -----------------------
print("Loading and preprocessing data...")
data_path = os.path.join('data', 'Per ANN.xlsx')
df = pd.read_excel(data_path)

# Data preprocessing steps
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)
df = df.drop(columns=['Nr.'], errors='ignore')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.replace(',', '.', regex=True)

# Process target variable
df['Gjinia'] = df['Gjinia'].astype(str).str.strip()
df['Gjinia'] = df['Gjinia'].replace(['', 'nan', 'NaN', None], pd.NA)
df = df.dropna(subset=["Gjinia"])
df['Gjinia'] = pd.to_numeric(df['Gjinia'], errors='coerce')
df['Gjinia'] = df['Gjinia'].fillna(0).astype(int).astype(bool)

# Convert features to numeric
for col in df.columns:
    if col != 'Gjinia':
        df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"Dataset loaded: {df.shape[0]} samples, {df.shape[1]-1} features")
print(f"Target distribution: {df['Gjinia'].value_counts().to_dict()}")

# -----------------------
# 2️⃣ Smart Feature Engineering
# -----------------------
X = df.drop(columns=['Gjinia'])
y = df['Gjinia']

# Remove features with very high correlation (>0.95) to reduce multicollinearity
correlation_matrix = X.corr().abs()
upper_triangle = correlation_matrix.where(
    np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
)
high_corr_features = [
    column for column in upper_triangle.columns 
    if any(upper_triangle[column] > 0.95)
]
if high_corr_features:
    print(f"Removing {len(high_corr_features)} highly correlated features")
    X = X.drop(columns=high_corr_features)

print(f"Features after correlation filtering: {X.shape[1]}")

# -----------------------
# 3️⃣ Create Robust ML Pipeline
# -----------------------
def create_robust_pipeline(model, feature_selection=True, k_features=10):
    """Create a robust ML pipeline with preprocessing and optional feature selection"""
    steps = []
    
    # Add SMOTE for class balancing
    steps.append(('smote', SMOTE(random_state=42)))
    
    # Add robust scaling
    steps.append(('scaler', RobustScaler()))
    
    # Add feature selection if requested
    if feature_selection:
        steps.append(('selector', SelectKBest(f_classif, k=min(k_features, X.shape[1]))))
    
    # Add the model
    steps.append(('model', model))
    
    return ImbalancedPipeline(steps)

# -----------------------
# 4️⃣ Define Models with Conservative Hyperparameters
# -----------------------
def get_robust_models():
    """Define models with conservative hyperparameters to prevent overfitting"""
    models = {
        'Logistic Regression': LogisticRegression(
            random_state=42, 
            max_iter=1000, 
            C=1.0,  # Less regularization
            class_weight='balanced'
        ),
        'Random Forest': RandomForestClassifier(
            random_state=42, 
            n_estimators=100,  # Reduced from 200
            max_depth=4,       # Reduced from 5
            min_samples_split=10,  # Increased
            min_samples_leaf=5,    # Increased
            class_weight='balanced'
        ),
        'Extra Trees': ExtraTreesClassifier(
            random_state=42, 
            n_estimators=100,
            max_depth=4,
            min_samples_split=8,
            min_samples_leaf=4,
            class_weight='balanced'
        ),
        'XGBoost': xgb.XGBClassifier(
            random_state=42, 
            n_estimators=100,  # Reduced
            max_depth=3,       # Reduced
            learning_rate=0.1,  # Increased
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=1.0,     # Increased regularization
            reg_lambda=1.0,    # Increased regularization
            verbosity=0
        ),
        'LightGBM': lgb.LGBMClassifier(
            random_state=42, 
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            num_leaves=10,     # Reduced
            feature_fraction=0.8,
            bagging_fraction=0.8,
            reg_alpha=1.0,
            reg_lambda=1.0,
            verbosity=-1
        ),
        'SVM': SVC(
            random_state=42, 
            probability=True, 
            C=0.5,  # Reduced C for more regularization
            gamma='scale', 
            kernel='rbf', 
            class_weight='balanced'
        ),
        'KNN': KNeighborsClassifier(
            n_neighbors=7,  # Increased for more smoothing
            weights='distance'
        )
    }
    return models

# -----------------------
# 5️⃣ Robust Model Evaluation
# -----------------------
def evaluate_model_robust(pipeline, X, y, model_name, n_repeats=10):
    """Robust evaluation using multiple validation strategies"""
    
    # 1. Repeated Stratified K-Fold
    rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=n_repeats, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=rskf, scoring='accuracy')
    
    # 2. Leave-One-Out (for small datasets)
    loo = LeaveOneOut()
    loo_scores = cross_val_score(pipeline, X, y, cv=loo, scoring='accuracy')
    
    # 3. Simple train-test split for final test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    # Get prediction probabilities for AUC
    try:
        y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_pred_proba)
    except:
        auc_score = None
    
    return {
        'model_name': model_name,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'loo_mean': loo_scores.mean(),
        'test_accuracy': test_accuracy,
        'auc_score': auc_score,
        'y_test': y_test,
        'y_pred': y_pred,
        'pipeline': pipeline
    }

# -----------------------
# 6️⃣ Train and Evaluate All Models
# -----------------------
print("\\nTraining and evaluating models with robust validation...")
results = []

models = get_robust_models()

for name, model in models.items():
    print(f"Evaluating {name}...")
    
    # Create pipeline with moderate feature selection
    pipeline = create_robust_pipeline(model, feature_selection=True, k_features=12)
    
    # Evaluate robustly
    result = evaluate_model_robust(pipeline, X, y, name, n_repeats=5)
    results.append(result)

# -----------------------
# 7️⃣ Create Conservative Ensemble
# -----------------------
print("\\nCreating ensemble models...")

# Select top 3 models based on cross-validation performance
best_models = sorted(results, key=lambda x: x['cv_mean'], reverse=True)[:3]

print("Top 3 models for ensemble:")
for i, model in enumerate(best_models):
    print(f"{i+1}. {model['model_name']}: {model['cv_mean']:.4f} ± {model['cv_std']:.4f}")

# Create voting ensemble with top 3 models
ensemble_models = [(r['model_name'], r['pipeline'].named_steps['model']) for r in best_models]
voting_pipeline = create_robust_pipeline(
    VotingClassifier(estimators=ensemble_models, voting='soft'),
    feature_selection=True,
    k_features=12
)

# Evaluate ensemble
ensemble_result = evaluate_model_robust(voting_pipeline, X, y, 'Voting_Ensemble', n_repeats=5)
results.append(ensemble_result)

# -----------------------
# 8️⃣ Final Results
# -----------------------
print("\\n" + "="*70)
print("FINAL RESULTS - ROBUST VALIDATION")
print("="*70)

# Sort by cross-validation performance
final_results = sorted(results, key=lambda x: x['cv_mean'], reverse=True)

print(f"{'Model':<20} {'CV Score':<15} {'LOO Score':<12} {'Test Acc':<10} {'AUC':<8}")
print("-" * 70)

best_model = final_results[0]

for result in final_results:
    cv_str = f"{result['cv_mean']:.3f}±{result['cv_std']:.3f}"
    loo_str = f"{result['loo_mean']:.3f}"
    auc_str = f"{result['auc_score']:.3f}" if result['auc_score'] else "N/A"
    
    print(f"{result['model_name']:<20} {cv_str:<15} {loo_str:<12} {result['test_accuracy']:<10.3f} {auc_str:<8}")

print("\\n" + "="*70)
print(f"🏆 BEST MODEL: {best_model['model_name']}")
print(f"   Cross-validation: {best_model['cv_mean']:.4f} ± {best_model['cv_std']:.4f}")
print(f"   Leave-one-out: {best_model['loo_mean']:.4f}")
print(f"   Test accuracy: {best_model['test_accuracy']:.4f}")
if best_model['auc_score']:
    print(f"   AUC Score: {best_model['auc_score']:.4f}")
print("="*70)

# Detailed classification report
print(f"\\nDetailed Results for {best_model['model_name']}:")
print("\\nConfusion Matrix:")
print(confusion_matrix(best_model['y_test'], best_model['y_pred']))
print("\\nClassification Report:")
print(classification_report(best_model['y_test'], best_model['y_pred']))

# Compare with original
print(f"\\n🎯 PERFORMANCE COMPARISON:")
print(f"   Original model: ~77.5% (cross-validation)")
print(f"   Enhanced model: {best_model['cv_mean']*100:.1f}% (cross-validation)")
improvement = (best_model['cv_mean'] - 0.775) * 100
if improvement > 0:
    print(f"   Improvement: +{improvement:.1f} percentage points")
else:
    print(f"   Change: {improvement:.1f} percentage points")

print(f"\\n📊 VALIDATION SUMMARY:")
print(f"   • Cross-validation (5-fold, 5 repeats): {best_model['cv_mean']:.3f} ± {best_model['cv_std']:.3f}")
print(f"   • Leave-one-out validation: {best_model['loo_mean']:.3f}")
print(f"   • Hold-out test set: {best_model['test_accuracy']:.3f}")
print(f"   • Validation shows {'low' if best_model['cv_std'] < 0.1 else 'moderate'} variance")

# Feature importance if available
if hasattr(best_model['pipeline'].named_steps['model'], 'feature_importances_'):
    print("\\nTop 10 Most Important Features:")
    
    # Get selected feature names
    if 'selector' in best_model['pipeline'].named_steps:
        selected_features = X.columns[best_model['pipeline'].named_steps['selector'].get_support()]
    else:
        selected_features = X.columns
        
    importances = pd.Series(
        best_model['pipeline'].named_steps['model'].feature_importances_,
        index=selected_features
    ).sort_values(ascending=False)
    
    for i, (feature, importance) in enumerate(importances.head(10).items()):
        print(f"   {i+1}. {feature}: {importance:.4f}")

print("\\n" + "="*70)

# %%