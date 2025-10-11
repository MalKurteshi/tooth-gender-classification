# %%
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler, PowerTransformer, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_classif, RFE, SelectFromModel
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier, ExtraTreesClassifier, BaggingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.combine import SMOTEENN

# Advanced models
import xgboost as xgb
import lightgbm as lgb

# Hyperparameter tuning
import optuna
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

import matplotlib.pyplot as plt
import seaborn as sns

# Suppress optuna logs
optuna.logging.set_verbosity(optuna.logging.WARNING)

# -----------------------
# 1️⃣ Process Data
# -----------------------
print("Loading and preprocessing data...")
data_path = os.path.join('data', 'Per ANN.xlsx')
df = pd.read_excel(data_path)

# --- Step 1: Make the first row the header ---
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# --- Step 2: Drop unnecessary columns ---
df = df.drop(columns=['Nr.'], errors='ignore')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # drop Unnamed columns

# --- Step 3: Clean numeric formats (replace commas with dots) ---
df = df.replace(',', '.', regex=True)

# --- Step 4: Clean and convert 'Gjinia' column safely ---
df['Gjinia'] = df['Gjinia'].astype(str).str.strip()                  # remove spaces
df['Gjinia'] = df['Gjinia'].replace(['', 'nan', 'NaN', None], pd.NA) # handle missing
df = df.dropna(subset=["Gjinia"])
df['Gjinia'] = pd.to_numeric(df['Gjinia'], errors='coerce')          # convert to numbers
df['Gjinia'] = df['Gjinia'].fillna(0).astype(int).astype(bool)       # fill NaN and cast to bool

# --- Step 5: Convert all other columns to numeric ---
for col in df.columns:
    if col != 'Gjinia':
        df[col] = pd.to_numeric(df[col], errors='coerce')

# -----------------------
# 2️⃣ Advanced Feature Engineering
# -----------------------
print("Performing advanced feature engineering...")

X = df.drop(columns=['Gjinia'])
y = df['Gjinia']

# Remove highly correlated features (> 0.95)
correlation_matrix = X.corr().abs()
upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))
high_corr_features = [column for column in upper_triangle.columns if any(upper_triangle[column] > 0.95)]
print(f"Removing {len(high_corr_features)} highly correlated features: {high_corr_features}")
X = X.drop(columns=high_corr_features)

# Create polynomial features (degree 2) for top correlated features
top_features = X.corrwith(y).abs().nlargest(8).index.tolist()
poly_features = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
X_poly = poly_features.fit_transform(X[top_features])
poly_feature_names = [f"poly_{i}" for i in range(X_poly.shape[1] - len(top_features))]

# Combine original features with polynomial features
X_combined = pd.concat([
    X.reset_index(drop=True),
    pd.DataFrame(X_poly[:, len(top_features):], columns=poly_feature_names)
], axis=1)

print(f"Feature engineering complete. Features: {X.shape[1]} -> {X_combined.shape[1]}")

# -----------------------
# 3️⃣ Advanced Preprocessing Pipeline
# -----------------------
def create_advanced_splits(X, y, test_size=0.2, random_state=42):
    """Create train/test splits with advanced sampling strategy"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Apply SMOTEENN for better class balancing
    smote_enn = SMOTEENN(random_state=random_state)
    X_train_balanced, y_train_balanced = smote_enn.fit_resample(X_train, y_train)
    
    # Scale features with power transformer (handles skewness)
    scaler = PowerTransformer(method='yeo-johnson')
    X_train_scaled = scaler.fit_transform(X_train_balanced)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train_balanced, y_test, scaler

X_train, X_test, y_train, y_test, scaler = create_advanced_splits(X_combined, y)

print(f"Training set size after balancing: {X_train.shape[0]} samples")
print(f"Class distribution after balancing: {np.bincount(y_train)}")

# -----------------------
# 4️⃣ Feature Selection
# -----------------------
print("Performing feature selection...")

# 1. Statistical feature selection
selector_stats = SelectKBest(f_classif, k=min(15, X_train.shape[1]))
X_train_selected = selector_stats.fit_transform(X_train, y_train)
X_test_selected = selector_stats.transform(X_test)

# 2. PCA for dimensionality reduction (alternative features)
pca = PCA(n_components=min(10, X_train.shape[1]), random_state=42)
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

print(f"Selected features: {X_train_selected.shape[1]}")
print(f"PCA components: {X_train_pca.shape[1]} (explained variance: {pca.explained_variance_ratio_.sum():.3f})")

# -----------------------
# 5️⃣ Advanced Model Definitions
# -----------------------
def get_base_models():
    """Define base models with optimized hyperparameters"""
    models = {
        'Logistic Regression': LogisticRegression(
            random_state=42, max_iter=2000, C=0.1, penalty='elasticnet', 
            solver='saga', l1_ratio=0.5, class_weight='balanced'
        ),
        'Random Forest': RandomForestClassifier(
            random_state=42, n_estimators=200, max_depth=5, 
            min_samples_split=5, min_samples_leaf=2, class_weight='balanced'
        ),
        'Extra Trees': ExtraTreesClassifier(
            random_state=42, n_estimators=200, max_depth=6, 
            min_samples_split=3, class_weight='balanced'
        ),
        'XGBoost': xgb.XGBClassifier(
            random_state=42, n_estimators=200, max_depth=4, 
            learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=0.1
        ),
        'LightGBM': lgb.LGBMClassifier(
            random_state=42, n_estimators=200, max_depth=4, 
            learning_rate=0.05, num_leaves=20, feature_fraction=0.8,
            bagging_fraction=0.8, reg_alpha=0.1, reg_lambda=0.1, verbosity=-1
        ),
        'SVM': SVC(
            random_state=42, probability=True, C=1.0, gamma='scale', 
            kernel='rbf', class_weight='balanced'
        ),
        'KNN': KNeighborsClassifier(n_neighbors=5, weights='distance'),
        'MLP': MLPClassifier(
            random_state=42, hidden_layer_sizes=(50, 25), max_iter=2000, 
            alpha=0.01, learning_rate_init=0.01
        )
    }
    return models

# -----------------------
# 6️⃣ Hyperparameter Optimization with Optuna
# -----------------------
def optimize_xgboost(X_train, y_train, n_trials=50):
    """Optimize XGBoost hyperparameters using Optuna"""
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 500),
            'max_depth': trial.suggest_int('max_depth', 3, 8),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 1.0),
            'random_state': 42
        }
        
        model = xgb.XGBClassifier(**params)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        return cv_scores.mean()
    
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return study.best_params

print("Optimizing XGBoost hyperparameters...")
best_xgb_params = optimize_xgboost(X_train_selected, y_train, n_trials=30)
print(f"Best XGBoost parameters: {best_xgb_params}")

# -----------------------
# 7️⃣ Model Training and Evaluation
# -----------------------
def evaluate_model(model, X_train, X_test, y_train, y_test, model_name, cv=5):
    """Comprehensive model evaluation"""
    # Fit model
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    # Cross-validation with repeated stratified K-fold
    cv_strategy = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_strategy, scoring='accuracy')
    
    # AUC score
    try:
        auc_score = roc_auc_score(y_test, y_pred_proba) if y_pred_proba is not None else None
    except:
        auc_score = None
    
    return {
        'model_name': model_name,
        'test_accuracy': accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'auc_score': auc_score,
        'y_pred': y_pred,
        'model': model
    }

print("\\nTraining and evaluating models...")
results = []

# Base models with selected features
base_models = get_base_models()

# Add optimized XGBoost
base_models['XGBoost_Optimized'] = xgb.XGBClassifier(**best_xgb_params)

# Evaluate each model
for name, model in base_models.items():
    if name in ['XGBoost', 'XGBoost_Optimized', 'LightGBM']:
        # Use selected features for tree-based models
        result = evaluate_model(model, X_train_selected, X_test_selected, y_train, y_test, name)
    elif name in ['Logistic Regression', 'SVM', 'MLP']:
        # Use PCA features for linear models
        result = evaluate_model(model, X_train_pca, X_test_pca, y_train, y_test, name)
    else:
        # Use selected features for other models
        result = evaluate_model(model, X_train_selected, X_test_selected, y_train, y_test, name)
    
    results.append(result)

# -----------------------
# 8️⃣ Stacking Ensemble
# -----------------------
print("\\nCreating stacking ensemble...")

# Select best performing models for stacking
best_models = sorted(results, key=lambda x: x['cv_mean'], reverse=True)[:5]
print("Top 5 models for stacking:")
for i, model in enumerate(best_models):
    print(f"{i+1}. {model['model_name']}: {model['cv_mean']:.4f} ± {model['cv_std']:.4f}")

# Create stacking classifier
base_estimators = [(result['model_name'], result['model']) for result in best_models]
stacking_classifier = StackingClassifier(
    estimators=base_estimators,
    final_estimator=LogisticRegression(random_state=42, max_iter=1000),
    cv=5,
    stack_method='predict_proba'
)

# Evaluate stacking classifier
stacking_result = evaluate_model(
    stacking_classifier, X_train_selected, X_test_selected, y_train, y_test, 'Stacking_Ensemble'
)
results.append(stacking_result)

# -----------------------
# 9️⃣ Voting Ensemble
# -----------------------
print("\\nCreating voting ensemble...")

# Create voting classifier with top 3 models
voting_estimators = [(result['model_name'], result['model']) for result in best_models[:3]]
voting_classifier = VotingClassifier(
    estimators=voting_estimators,
    voting='soft'
)

voting_result = evaluate_model(
    voting_classifier, X_train_selected, X_test_selected, y_train, y_test, 'Voting_Ensemble'
)
results.append(voting_result)

# -----------------------
# 🔟 Results Summary
# -----------------------
print("\\n" + "="*60)
print("FINAL RESULTS SUMMARY")
print("="*60)

# Sort results by CV score
final_results = sorted(results, key=lambda x: x['cv_mean'], reverse=True)

print(f"{'Model Name':<25} {'Test Acc':<10} {'CV Mean ± Std':<20} {'AUC':<8}")
print("-" * 65)

best_model_result = None
best_cv_score = 0

for result in final_results:
    auc_str = f"{result['auc_score']:.3f}" if result['auc_score'] else "N/A"
    cv_str = f"{result['cv_mean']:.3f} ± {result['cv_std']:.3f}"
    print(f"{result['model_name']:<25} {result['test_accuracy']:<10.3f} {cv_str:<20} {auc_str:<8}")
    
    if result['cv_mean'] > best_cv_score:
        best_cv_score = result['cv_mean']
        best_model_result = result

print("\\n" + "="*60)
print(f"🏆 BEST MODEL: {best_model_result['model_name']}")
print(f"   Cross-validation accuracy: {best_model_result['cv_mean']:.4f} ± {best_model_result['cv_std']:.4f}")
print(f"   Test accuracy: {best_model_result['test_accuracy']:.4f}")
if best_model_result['auc_score']:
    print(f"   AUC Score: {best_model_result['auc_score']:.4f}")
print("="*60)

# Detailed results for best model
print(f"\\nDetailed results for {best_model_result['model_name']}:")
print("Confusion Matrix:")
print(confusion_matrix(y_test, best_model_result['y_pred']))
print("\\nClassification Report:")
print(classification_report(y_test, best_model_result['y_pred']))

# Feature importance for tree-based models
if hasattr(best_model_result['model'], 'feature_importances_'):
    print("\\nTop 10 Feature Importances:")
    if best_model_result['model_name'] in ['XGBoost', 'XGBoost_Optimized', 'LightGBM', 'Random Forest', 'Extra Trees']:
        feature_names = X_combined.columns[selector_stats.get_support()]
        importances = pd.Series(
            best_model_result['model'].feature_importances_, 
            index=feature_names
        ).sort_values(ascending=False)
        print(importances.head(10))

print(f"\n🎯 IMPROVEMENT: From ~69% to {best_model_result['cv_mean']*100:.1f}% accuracy!")
print(f"   Improvement: +{(best_model_result['cv_mean']-0.69)*100:.1f} percentage points")

# -----------------------
# 🔟 Save the Best Model
# -----------------------
import joblib
print(f"\n💾 Saving the best model: {best_model_result['model_name']}")

# Save the best model
joblib.dump(best_model_result['model'], 'best_tooth_gender_model.pkl')

# Save the scaler for preprocessing
joblib.dump(scaler, 'tooth_gender_scaler.pkl')

# Save feature selector
joblib.dump(selector_stats, 'tooth_gender_selector.pkl')

# Save feature names and metadata
model_metadata = {
    'model_name': best_model_result['model_name'],
    'cv_accuracy': best_model_result['cv_mean'],
    'cv_std': best_model_result['cv_std'],
    'test_accuracy': best_model_result['test_accuracy'],
    'auc_score': best_model_result['auc_score'],
    'feature_names': X_combined.columns.tolist(),
    'selected_features': X_combined.columns[selector_stats.get_support()].tolist(),
    'target_classes': ['Female', 'Male'],
    'preprocessing_steps': [
        'Remove highly correlated features',
        'SMOTE balancing',
        'PowerTransformer scaling',
        'SelectKBest feature selection'
    ]
}

import json
with open('model_metadata.json', 'w') as f:
    json.dump(model_metadata, f, indent=2)

print("✅ Model saved successfully!")
print("📁 Saved files:")
print("   • best_tooth_gender_model.pkl - Trained model")
print("   • tooth_gender_scaler.pkl - Feature scaler")
print("   • tooth_gender_selector.pkl - Feature selector")
print("   • model_metadata.json - Model information")

# %%
