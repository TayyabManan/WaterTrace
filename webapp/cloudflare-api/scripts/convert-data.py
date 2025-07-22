#!/usr/bin/env python3
"""
Convert CSV data files to JSON format for embedding in Cloudflare Workers
"""
import pandas as pd
import json
import os

# Paths
base_path = "/mnt/d/Haris/GIS Portfolio/Water Trace"
grace_csv = os.path.join(base_path, "data/csv/pakistan_grace_2002_2017_complete.csv")
gldas_csv = os.path.join(base_path, "data/csv/pakistan_gldas_2018_2024_monthly.csv")
output_dir = os.path.join(base_path, "webapp/cloudflare-api/src/data")

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Convert GRACE data
print("Converting GRACE data...")
grace_df = pd.read_csv(grace_csv)
grace_data = grace_df.to_dict('records')
with open(os.path.join(output_dir, 'grace-data.json'), 'w') as f:
    json.dump(grace_data, f, indent=2)

# Convert GLDAS data
print("Converting GLDAS data...")
gldas_df = pd.read_csv(gldas_csv)
gldas_data = gldas_df.to_dict('records')
with open(os.path.join(output_dir, 'gldas-data.json'), 'w') as f:
    json.dump(gldas_data, f, indent=2)

# Create a combined metadata file
metadata = {
    "grace_period": {
        "start": grace_df['Date'].min() if 'Date' in grace_df.columns else grace_df.iloc[:, 0].min(),
        "end": grace_df['Date'].max() if 'Date' in grace_df.columns else grace_df.iloc[:, 0].max(),
        "records": len(grace_df)
    },
    "gldas_period": {
        "start": gldas_df['Date'].min() if 'Date' in gldas_df.columns else gldas_df.iloc[:, 0].min(),
        "end": gldas_df['Date'].max() if 'Date' in gldas_df.columns else gldas_df.iloc[:, 0].max(),
        "records": len(gldas_df)
    }
}

with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Data conversion complete!")
print(f"GRACE records: {len(grace_data)}")
print(f"GLDAS records: {len(gldas_data)}")