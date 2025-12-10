# Step 1: Import Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from scipy import stats

# Step 2: Load Dataset
filepath = 'C:\\Users\\ycong\\Documents\\FYP\\Dataset\\Final_Augmented_dataset_Diseases_and_Symptoms.csv'
data = pd.read_csv(filepath)
print("✅ Data loaded successfully.\n")

# Step 3: Clean Column Names
data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")
print("📋 Cleaned Columns:", data.columns.tolist(), "\n")

# Step 4: Check & Handle Missing Values
print("⚠️ Missing values:\n", data.isnull().sum(), "\n")

for col in data.columns:
    if data[col].dtype == 'object':
        data[col] = data[col].fillna(data[col].mode()[0])
    else:
        data[col] = data[col].fillna(data[col].mean())

print("✅ Missing values handled.\n")

# Step 5: Drop Duplicates
initial_shape = data.shape
data = data.drop_duplicates()
print(f"🔁 Dropped {initial_shape[0] - data.shape[0]} duplicate rows.\n")

# Step 6: Visual Outlier Detection (Boxplot + Histogram)
numeric_cols = data.select_dtypes(include=np.number).columns.tolist()

if numeric_cols:
    for col in numeric_cols:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        sns.boxplot(x=data[col], ax=axes[0], color='skyblue')
        axes[0].set_title(f'Boxplot: {col}')
        sns.histplot(data[col], kde=True, ax=axes[1], color='orange')
        axes[1].set_title(f'Histogram: {col}')
        plt.suptitle(f"Outlier Detection for '{col}'")
        plt.tight_layout()
        plt.show()
else:
    print("⚠️ No numeric columns found for outlier visualization.\n")

# Step 7: Handle Outliers (IQR Capping)
for col in numeric_cols:
    Q1 = data[col].quantile(0.25)
    Q3 = data[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    data[col] = np.clip(data[col], lower, upper)
print("✅ Outliers capped using IQR.\n")

# Step 8: Encode Categorical Features
cat_cols = data.select_dtypes(include='object').columns.tolist()
le = LabelEncoder()
for col in cat_cols:
    data[col] = le.fit_transform(data[col])
print("🔤 Categorical features encoded.\n")

# Step 9: Standardization (Z-score)
scaler = StandardScaler()
data_standardized = pd.DataFrame(scaler.fit_transform(data[numeric_cols]), columns=[f"{col}_std" for col in numeric_cols])
print("📏 Standardization completed.\n")

# Step 10: Normalization (Min-Max)
normalizer = MinMaxScaler()
data_normalized = pd.DataFrame(normalizer.fit_transform(data[numeric_cols]), columns=[f"{col}_norm" for col in numeric_cols])
print("📉 Normalization completed.\n")

# Step 11: Outlier Summary with Z-Score
print("\n🔍 Z-score Outlier Summary:")
for col in numeric_cols:
    z_scores = stats.zscore(data[col])
    outliers = (np.abs(z_scores) > 3).sum()
    print(f"{col}: {outliers} outlier(s) (Z-score > 3)")

# Step 12: Check Normalized Columns
print("\n📊 Checking for Normalized Columns (0–1 range):")
normalized_cols = [col for col in numeric_cols if data[col].min() >= 0.0 and data[col].max() <= 1.0]
print("Probably Normalized Columns:", normalized_cols)

# Step 13: Check Standardized Columns
means = data[numeric_cols].mean()
stds = data[numeric_cols].std()
standardized_cols = [col for col in numeric_cols if abs(means[col]) < 0.1 and abs(stds[col] - 1) < 0.1]
print("📐 Probably Standardized Columns:", standardized_cols)

# Step 14: Combine All Data
data_final = pd.concat([data.reset_index(drop=True), data_standardized, data_normalized], axis=1)

# Step 15: Final Summary
print("\n✅ Final data shape:", data_final.shape)
print("\n📋 Sample data:")
print(data_final.head())