# notebooks/21_data_exploration_validation.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("📊 WaterTrace Data Validation & Exploration")
print("=" * 60)

# Load all three datasets
datasets = {
    'gldas_recent': {
        'file': 'pakistan_gldas_2018_2024_monthly.csv',
        'description': 'GLDAS 2018-2024 (Future-proof dataset)',
        'status': 'primary'
    },
    'grace_historical': {
        'file': 'pakistan_grace_2002_2017_complete.csv', 
        'description': 'GRACE 2002-2017 (Historical baseline)',
        'status': 'historical'
    },
    'grace_backup': {
        'file': 'pakistan_groundwater_updated_grace.csv',
        'description': 'GRACE backup/validation',
        'status': 'validation'
    }
}

loaded_data = {}

for name, info in datasets.items():
    try:
        print(f"\n📁 Loading {info['file']}...")
        df = pd.read_csv(f"data/csv/{info['file']}")  # Update path
        
        print(f"   ✅ Shape: {df.shape}")
        print(f"   📅 Columns: {list(df.columns)}")
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            print(f"   🕐 Period: {df['date'].min()} to {df['date'].max()}")
            print(f"   📊 Data points: {len(df)}")
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"   ⚠️ Missing values: {missing[missing > 0].to_dict()}")
        else:
            print(f"   ✅ No missing values")
        
        loaded_data[name] = {
            'data': df,
            'info': info
        }
        
    except Exception as e:
        print(f"   ❌ Error loading {info['file']}: {str(e)[:100]}...")

# Data quality summary
print(f"\n📊 DATA LOADING SUMMARY")
print(f"Successfully loaded: {len(loaded_data)}/3 datasets")

# Save validation results
validation_results = {
    'timestamp': datetime.now().isoformat(),
    'datasets_loaded': len(loaded_data),
    'validation_status': 'completed',
    'next_step': 'data_integration'
}

import json
import os
os.makedirs('data/processed', exist_ok=True)
with open('data/processed/data_validation_results.json', 'w') as f:
    json.dump(validation_results, f, indent=2)

print("✅ Data validation completed!")