import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Set your CSV file path
filepath = 'C:\\Users\\ycong\\Documents\\FYP\\Dataset\\Final_Augmented_dataset_Diseases_and_Symptoms.csv'
output_path = 'C:\\Users\\ycong\\Documents\\FYP\\Dataset\\Cleaned_Dataset.csv'

# Step 1: Check if file exists
if not os.path.exists(filepath):
    print("❌ File not found:", filepath)
else:
    # Step 2: Load the dataset
    data = pd.read_csv(filepath)
    print("✅ Data loaded successfully.\n")

    # Step 3: Show basic info
    print("📊 Dataset Overview:")
    print(data.info())

    print("\n🔍 First 5 rows:")
    print(data.head())

    # Step 4: Check for missing values
    null_counts = data.isnull().sum()
    total_nulls = null_counts.sum()
    print("\n⚠️ Missing values per column:")
    print(null_counts)

    # Step 5: Check for duplicates
    duplicate_mask = data.duplicated()
    duplicate_count = duplicate_mask.sum()
    print(f"\n🔁 Duplicate rows found: {duplicate_count}")

    if duplicate_count > 0:
        print("\n📋 List of duplicated rows:")
        print(data[duplicate_mask])

        # Optional: Drop duplicates
        data = data.drop_duplicates()
        print("\n✅ Duplicate rows have been removed.")

        # ✅ Save the cleaned dataset to a new CSV file
        data.to_csv(output_path, index=False)
        print(f"💾 Cleaned dataset saved to: {output_path}")

    # Step 6: Check column data types
    print("\n🔎 Column data types:")
    print(data.dtypes)

    # Step 7: Clean column names (optional)
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
    print("\n🧽 Cleaned column names:")
    print(data.columns.tolist())

    # Step 8: Describe numeric columns
    print("\n📈 Statistical summary of numeric columns:")
    print(data.describe())

    # Step 9: Optional: Plot boxplots of numeric columns
    numeric_cols = data.select_dtypes(include='number').columns
    if not numeric_cols.empty:
        print("\n📊 Generating boxplot(s) for numeric columns:")
        for col in numeric_cols:
           plt.figure(figsize=(5, 3))
           sns.boxplot(x=data[col])
           plt.title(f'Boxplot of {col}')
           plt.tight_layout()
           plt.show()
    else:
       print("\nℹ️ No numeric columns to plot.")

    # Step 10: Final null check — show rows with missing data
    null_rows = data[data.isnull().any(axis=1)]
    if not null_rows.empty:
        print("\n⚠️ Rows with missing values:")
        print(null_rows)
    else:
        print("\n✅ No rows with missing values.")

    # ✅ Final check: Clean status
    print("\n📋 Cleanliness Summary:")
    if total_nulls == 0 and duplicate_count == 0:
        print("🎉 The dataset is clean and ready for analysis.")
    else:
        print("🚧 Some cleaning may still be needed.")
        if total_nulls > 0:
            print(f"➡️ There are {total_nulls} missing values in the dataset.")
            print("   Columns with missing values:")
            print(null_counts[null_counts > 0])
        if duplicate_count > 0:
            print(f"➡️ There were {duplicate_count} duplicate rows.")

    print("\n✅ EDA Cleaning Check Completed.")