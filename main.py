# %%
print("test")
#%%
import pandas as pd
import numpy as np
import os

def main():
    """
    Main function to read tooth gender classification data and print its shape.
    """
    # Define the path to the data file
    data_path = os.path.join('data', 'Per ANN.xlsx')
    
    try:
        # Read the Excel file
        print(f"Reading data from: {data_path}")
        df = pd.read_excel(data_path)
        
        # Print basic information about the dataset
        print("\n=== Dataset Information ===")
        print(f"Shape: {df.shape}")
        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")
        
        # Print column names
        print("\n=== Column Names ===")
        for i, col in enumerate(df.columns, 1):
            print(f"{i}. {col}")
        
        # Print first few rows to understand the data
        print("\n=== First 5 rows ===")
        print(df.head())
        
        # Print data types
        print("\n=== Data Types ===")
        print(df.dtypes)
        
        # Check for missing values
        print("\n=== Missing Values ===")
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            print(missing_values[missing_values > 0])
        else:
            print("No missing values found.")
            
    except FileNotFoundError:
        print(f"Error: Could not find the file '{data_path}'")
        print("Please make sure the Excel file exists in the data directory.")
    except Exception as e:
        print(f"Error reading the file: {str(e)}")
        print("Please check if the file is a valid Excel file and not corrupted.")

if __name__ == "__main__":
    main()

# %%
