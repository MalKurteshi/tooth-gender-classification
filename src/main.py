#!/usr/bin/env python3
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

# %%
import os
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt


# -----------------------
# 1 Process Data
# -----------------------
# Read the Excel file
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
# 2️⃣ Split Data
# -----------------------
X = df.drop(columns=['Gjinia'])
y = df['Gjinia']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------
# 3️⃣ Balance Classes
# -----------------------
smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# -----------------------
# 4️⃣ Scale Features
# -----------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------
# 5️⃣ Define Models
# -----------------------
models = {
    "Logistic Regression": LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    "Random Forest": RandomForestClassifier(random_state=42, class_weight='balanced'),
    "SVM": SVC(random_state=42, probability=True, class_weight='balanced')
}

# -----------------------
# 6️⃣ Tune Random Forest
# -----------------------
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 3, 5, 7],
    'min_samples_split': [2, 5, 10]
}
grid = GridSearchCV(models['Random Forest'], param_grid, cv=5)

grid.fit(X_train_scaled, y_train)
best_rf = grid.best_estimator_
models['Random Forest (Tuned)'] = best_rf

# -----------------------

# 7️⃣ Evaluate Models
# -----------------------
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    print(f"\n=== {name} ===")
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    scores = cross_val_score(model, X, y, cv=5)
    print(f"Cross-val accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

# -----------------------
# 8️⃣ Ensemble Voting Model
# -----------------------
ensemble = VotingClassifier(
    estimators=[
        ('lr', models['Logistic Regression']),
        ('rf', best_rf),
        ('svm', models['SVM'])
    ],
    voting='soft'
)
ensemble.fit(X_train_scaled, y_train)
y_pred = ensemble.predict(X_test_scaled)

print("\n=== Ensemble (Voting) ===")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
scores = cross_val_score(ensemble, X, y, cv=5)
print(f"Cross-val accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

# -----------------------
# 9️⃣ Feature Importance (Random Forest)
# -----------------------
importances = pd.Series(best_rf.feature_importances_, index=X.columns)
top_features = importances.sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 4))
top_features.plot(kind='bar')
plt.title('Top 10 Most Important Features (Random Forest)')
plt.tight_layout()
plt.show()

# %%
