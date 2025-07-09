# notebooks/03_clean_province_names.py
import geopandas as gpd
import pandas as pd

print("🧹 Cleaning province names...")

# Load your shapefile
pakistan_gdf = gpd.read_file("data/raw/pakistan_shapefile/pakistan.shp")

# Print current province names
print("📋 Current provinces:")
for province in sorted(pakistan_gdf['PROVINCE'].unique()):
    count = len(pakistan_gdf[pakistan_gdf['PROVINCE'] == province])
    print(f"   {province}: {count} districts")

# Create province name mapping
province_mapping = {
    'PUNJAB': 'Punjab',
    'Punjab': 'Punjab',
    'SINDH': 'Sindh', 
    'Sindh': 'Sindh',
    'BALOCHISTAN': 'Balochistan',
    'Balochistan': 'Balochistan',
    'KHYBER PAKHTUNKHWA': 'Khyber Pakhtunkhwa',
    'Khyber Pakhtunkhwa': 'Khyber Pakhtunkhwa',
    'AZAD KASHMIR': 'Azad Kashmir',
    'GILGIT-BALTISTAN': 'Gilgit-Baltistan',
    'FATA': 'FATA',
    'DISPUTED TERRITORY': 'Disputed Territory',
    'FEDERAL CAPITAL TERRITORY': 'Islamabad Capital Territory'
}

# Apply mapping
pakistan_gdf['PROVINCE_CLEAN'] = pakistan_gdf['PROVINCE'].map(province_mapping)

# Check results
print("\n✨ Cleaned provinces:")
cleaned_summary = pakistan_gdf.groupby('PROVINCE_CLEAN').size().sort_values(ascending=False)
for province, count in cleaned_summary.items():
    print(f"   {province}: {count} districts")

# Save cleaned data
pakistan_gdf.to_file("data/processed/pakistan_districts_cleaned.shp")
print("\n✅ Cleaned shapefile saved: data/processed/pakistan_districts_cleaned.shp")

# Save summary
summary_dict = {
    'original_provinces': pakistan_gdf['PROVINCE'].unique().tolist(),
    'cleaned_provinces': cleaned_summary.to_dict(),
    'total_districts': len(pakistan_gdf)
}

import json
with open('data/processed/cleaned_province_summary.json', 'w') as f:
    json.dump(summary_dict, f, indent=2)

print("✅ Summary saved: data/processed/cleaned_province_summary.json")