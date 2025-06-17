# backend/train_model.py (Updated to use your specific .xlsx file path)

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

print("Loading your dataset and training Random Forest Regressor...")

# --- Configuration for your Dataset ---
# Updated path to your .xlsx file
DATASET_PATH = r'C:\Users\Bhiresh\Desktop\agripricepro\pricesofagriculture.xlsx'
TARGET_COLUMN = 'Average Price (INR/Quintal)' # The column you want to predict

# Define features based on your CSV's column names from the image
CATEGORICAL_FEATURES = [
    'Crop Type', 'Crop Category', 'Season', 'Country', 'State',
    'District', 'Market', 'Month' # Month as categorical for one-hot encoding
]
NUMERICAL_FEATURES = [
    'Year', 'Rainfall (mm)', 'Temperature (Celsius)',
    'Area Under Cultivation (Hectares)', 'Production (Tonnes)',
    'Yield (Kg/Hectare)', 'Previous Year Price (INR/Quintal)'
]

# This list defines the exact order of features that the pipeline expects during prediction.
# It is crucial to maintain this order when making predictions in app.py.
# The ColumnTransformer applies transformations based on these names, so their presence
# in the DataFrame with these names is key.
TRAINING_FEATURES_ORDER = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


# Ensure all feature columns are present in the defined lists
EXPECTED_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET_COLUMN]

# --- 1. Load your Dataset ---
try:
    # Use read_excel because the file is explicitly .xlsx
    df = pd.read_excel(DATASET_PATH)
    print(f"Successfully loaded '{DATASET_PATH}' with {len(df)} rows and {len(df.columns)} columns.")
    print("Columns loaded:", df.columns.tolist())
except FileNotFoundError:
    print(f"ERROR: Dataset '{DATASET_PATH}' not found. Please ensure the path is correct.")
    exit()
except Exception as e:
    print(f"ERROR: Could not load dataset. Check file format or path: {e}")
    exit()

# --- 2. Basic Data Preprocessing and Cleaning ---
# Ensure all expected columns exist
missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
if missing_cols:
    print(f"ERROR: Missing expected columns in dataset: {missing_cols}")
    print("Please check your Excel sheet headers and ensure they match the defined features/target.")
    exit()

# Handle missing values (simple imputation for demonstration)
# For numerical features, fill with mean or median
for col in NUMERICAL_FEATURES:
    if df[col].isnull().any():
        df[col] = df[col].fillna(df[col].mean())
        print(f"Filled missing values in numerical column: {col}")

# For categorical features, fill with mode or a placeholder 'Unknown'
for col in CATEGORICAL_FEATURES:
    # Convert to string first to handle potential mixed types or numeric months gracefully for categorical processing
    df[col] = df[col].astype(str)
    if df[col].isnull().any() or (df[col] == 'nan').any(): # Check for actual NaN or string 'nan' after conversion
        df[col] = df[col].replace('nan', df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
        print(f"Filled missing values in categorical column: {col}")


# Drop rows where the target (price) is missing (as we can't train without it)
original_rows = len(df)
df.dropna(subset=[TARGET_COLUMN], inplace=True)
if len(df) < original_rows:
    print(f"Dropped {original_rows - len(df)} rows with missing target price.")

if df.empty:
    print("ERROR: Dataset is empty after cleaning. Cannot train model.")
    exit()

# --- Prepare data for model ---
X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
y = df[TARGET_COLUMN]

# --- 3. Feature Engineering & Preprocessing Pipeline ---
# Create a preprocessor using ColumnTransformer
# OneHotEncoder for categorical features (handle_unknown='ignore' prevents errors on unseen categories)
# sparse_output=False ensures a dense array output, which can be easier to debug for smaller datasets
# StandardScaler for numerical features (good practice for Random Forest, though less critical than for linear models)
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), NUMERICAL_FEATURES),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
    ])

# --- 4. Create and Train the Model Pipeline ---
# Combine preprocessor and RandomForestRegressor into a single pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)) # n_jobs=-1 uses all available cores
])

print("Training RandomForestRegressor...")
model_pipeline.fit(X, y)

print(f"Model trained. R-squared on training data: {model_pipeline.score(X, y):.4f}") # Display R-squared with more precision

# --- 5. Save the Entire Pipeline and Other Metadata ---
models_dir = 'models'
os.makedirs(models_dir, exist_ok=True)

joblib.dump(model_pipeline, os.path.join(models_dir, 'crop_price_rf_pipeline.pkl'))

# Extract unique values for frontend dropdowns directly from your dataset
metadata = {
    "crop_categories": df['Crop Category'].unique().tolist(),
    "crop_types_by_category": {
        cat: df[df['Crop Category'] == cat]['Crop Type'].unique().tolist()
        for cat in df['Crop Category'].unique()
    },
    "countries": df['Country'].unique().tolist(),
    "states_by_country": {
        country: df[df['Country'] == country]['State'].unique().tolist()
        for country in df['Country'].unique()
    },
    "seasons": df['Season'].unique().tolist(),
    "districts_by_state": { # New: add districts for potential future use or display
        state: df[df['State'] == state]['District'].unique().tolist()
        for state in df['State'].unique()
    },
    "markets_by_district": { # New: add markets
        district: df[df['District'] == district]['Market'].unique().tolist()
        for district in df['District'].unique()
    },
    "months": sorted(df['Month'].unique().astype(str).tolist()), # Ensure months are sorted and as strings for consistency
    "unit_map": { # Assuming all prices are in INR/Quintal based on your column name
        crop_type: "INR/Quintal" for crop_type in df['Crop Type'].unique()
    },
    "TRAINING_FEATURES_ORDER": TRAINING_FEATURES_ORDER # Save the feature order
}
joblib.dump(metadata, os.path.join(models_dir, 'app_metadata.pkl'))


print(f"RandomForestRegressor pipeline and app metadata saved to '{models_dir}/' directory.")