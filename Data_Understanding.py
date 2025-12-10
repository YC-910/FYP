import pandas as pd
import numpy as np

# Load dataset
filepath = 'C:\\Users\\ycong\\Documents\\FYP\\Dataset\\Final_Augmented_dataset_Diseases_and_Symptoms.csv'

#filepath = 'C:\\Users\\ycong\\Documents\\FYP\\Dataset\\Cleaned_Dataset.csv'
data = pd.read_csv(filepath)
data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
print("✅ Dataset loaded.\n")

# Basic Structure
print("📏 Dataset Shape:")
print(f"- Rows: {data.shape[0]}, Columns: {data.shape[1]}\n")

# Column Data Types
print("📋 Column Types:")
print(data.dtypes.value_counts())
print("\nDetailed Column Types:")
print(data.dtypes)

# Null Values
print("\n⚠️ Missing Values Per Column:")
nulls = data.isnull().sum()
nulls = nulls[nulls > 0]
if not nulls.empty:
    print(nulls)
else:
    print("✅ No missing values.")

# Constant or Near-Constant Columns
print("\n📌 Constant or Near-Constant Features:")
for col in data.columns:
    ratio = data[col].value_counts(normalize=True).values[0]
    if ratio > 0.95:
        print(f"- {col}: {round(ratio*100, 2)}% same value")

# Unique Counts
print("\n🔢 Unique Value Counts:")
for col in data.columns:
    unique_count = data[col].nunique()
    if unique_count == 1:
        print(f"- {col}: Constant value")
    elif unique_count < 10:
        print(f"- {col}: Low cardinality ({unique_count} unique values)")
    elif unique_count < 100:
        print(f"- {col}: Medium cardinality ({unique_count} unique values)")
    else:
        print(f"- {col}: High cardinality ({unique_count} unique values)")

# Top Values in Categorical Columns
print("\n📌 Top Values in Categorical Columns:")
cat_cols = data.select_dtypes(include='object').columns
for col in cat_cols:
    print(f"\n- {col} (Top 5):")
    print(data[col].value_counts().head(5))

# Text Column Analysis
print("\n📝 Text Columns Pattern Insight:")
for col in cat_cols:
    lengths = data[col].dropna().astype(str).apply(len)
    if lengths.empty:
        continue
    print(f"- {col}:")
    print(f"  Avg length: {lengths.mean():.2f}, Min: {lengths.min()}, Max: {lengths.max()}")

# Numeric Overview
print("\n🔢 Numeric Columns Overview:")
num_cols = data.select_dtypes(include='number').columns
if not num_cols.empty:
    for col in num_cols:
        print(f"\n- {col}:")
        print(f"  Min: {data[col].min()}, Max: {data[col].max()}")
        print(f"  Mean: {data[col].mean():.2f}, Std: {data[col].std():.2f}")
else:
    print("ℹ️ No numeric columns.")

# Correlation Matrix
print("\n🔗 Correlation Matrix (Top Correlated Pairs):")
if len(num_cols) >= 2:
    corr_matrix = data[num_cols].corr().abs()
    np.fill_diagonal(corr_matrix.values, 0)
    top_corrs = corr_matrix.unstack().sort_values(ascending=False).drop_duplicates()
    print(top_corrs.head(5))
else:
    print("ℹ️ Not enough numeric columns for correlation.")

# Duplicate Rows
print("\n🔁 Duplicate Rows:")
dupes = data.duplicated().sum()
if dupes > 0:
    print(f"Found {dupes} duplicate rows.")
else:
    print("✅ No duplicates found.")

# Memory Usage
print("\n💾 Memory Usage:")
mem_usage = data.memory_usage(deep=True) / (1024**2)
print(mem_usage)
print(f"\n🔎 Total Memory Usage: {mem_usage.sum():.2f} MB")

# Dataset Summary
print("\n📦 Dataset Summary:")
print(data.info())