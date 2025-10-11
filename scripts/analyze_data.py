import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

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

print("=== DATASET OVERVIEW ===")
print(f"Dataset shape: {df.shape}")
print(f"Number of features: {len(df.columns) - 1}")
print(f"Number of samples: {len(df)}")
print()

print("=== TARGET VARIABLE DISTRIBUTION ===")
print(f"Class distribution:")
print(df['Gjinia'].value_counts())
print(f"Class percentages:")
print(df['Gjinia'].value_counts(normalize=True) * 100)
print()

print("=== MISSING VALUES ===")
missing_vals = df.isnull().sum()
missing_percent = (missing_vals / len(df)) * 100
missing_info = pd.DataFrame({
    'Missing Count': missing_vals,
    'Missing %': missing_percent
}).sort_values('Missing %', ascending=False)
print(missing_info[missing_info['Missing Count'] > 0])
print()

print("=== FEATURE STATISTICS ===")
X = df.drop(columns=['Gjinia'])
print(f"Features with zero variance: {len(X.columns[X.var() == 0])}")
print(f"Features with very low variance (< 0.01): {len(X.columns[X.var() < 0.01])}")
print()

# Correlation analysis
print("=== CORRELATION ANALYSIS ===")
correlation_with_target = df.corr()['Gjinia'].drop('Gjinia').abs().sort_values(ascending=False)
print("Top 10 features most correlated with target:")
print(correlation_with_target.head(10))
print()

print("=== HIGH CORRELATION BETWEEN FEATURES ===")
feature_corr = X.corr().abs()
# Find pairs of features with high correlation
high_corr_pairs = []
for i in range(len(feature_corr.columns)):
    for j in range(i+1, len(feature_corr.columns)):
        if feature_corr.iloc[i, j] > 0.9:
            high_corr_pairs.append((feature_corr.columns[i], feature_corr.columns[j], feature_corr.iloc[i, j]))

print(f"Feature pairs with correlation > 0.9: {len(high_corr_pairs)}")
for pair in high_corr_pairs[:10]:  # Show first 10
    print(f"{pair[0]} - {pair[1]}: {pair[2]:.3f}")
print()

print("=== FEATURE RANGES ===")
print("Min and Max values for each feature:")
feature_ranges = pd.DataFrame({
    'Min': X.min(),
    'Max': X.max(),
    'Range': X.max() - X.min(),
    'Mean': X.mean(),
    'Std': X.std()
})
print(feature_ranges.describe())
print()

print("=== OUTLIER DETECTION (IQR Method) ===")
outlier_counts = {}
for col in X.columns:
    Q1 = X[col].quantile(0.25)
    Q3 = X[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = X[(X[col] < lower_bound) | (X[col] > upper_bound)][col]
    outlier_counts[col] = len(outliers)

outlier_df = pd.DataFrame.from_dict(outlier_counts, orient='index', columns=['Outlier_Count'])
outlier_df = outlier_df.sort_values('Outlier_Count', ascending=False)
print("Features with most outliers:")
print(outlier_df.head(10))