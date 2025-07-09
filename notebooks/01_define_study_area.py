# notebooks/01_load_pakistan_shapefile.py
import geopandas as gpd
import folium
import os
import matplotlib.pyplot as plt

print("🗺️ Loading Pakistan shapefile...")

# Load your shapefile (adjust path as needed)
# Common shapefile names: pakistan.shp, pak_admin.shp, etc.
shapefile_path = "data/raw/pakistan_shapefile/pakistan.shp"  # Update this path

try:
    # Load shapefile
    pakistan_gdf = gpd.read_file(shapefile_path)
    print(f"✅ Shapefile loaded successfully!")
    print(f"📊 Shape: {pakistan_gdf.shape}")
    print(f"🗂️ Columns: {list(pakistan_gdf.columns)}")
    print(f"📐 CRS: {pakistan_gdf.crs}")
    
    # Display first few rows
    print("\n📋 First few rows:")
    print(pakistan_gdf.head())
    
except FileNotFoundError:
    print(f"❌ Shapefile not found at: {shapefile_path}")
    print("📁 Please update the path to your shapefile")
    print("💡 Common locations:")
    print("   - data/raw/pakistan.shp")
    print("   - shapefiles/pakistan.shp") 
    print("   - downloads/pakistan.shp")
    exit()

# Check if it's country-level or province-level data
if len(pakistan_gdf) == 1:
    print("🇵🇰 Country-level shapefile detected")
    level = "country"
elif len(pakistan_gdf) < 10:
    print("🏛️ Province-level shapefile detected")
    level = "province"
else:
    print("🏘️ District-level shapefile detected")
    level = "district"

# Get bounds for later use
bounds = pakistan_gdf.total_bounds
print(f"\n📏 Bounding Box:")
print(f"   West: {bounds[0]:.4f}°")
print(f"   South: {bounds[1]:.4f}°") 
print(f"   East: {bounds[2]:.4f}°")
print(f"   North: {bounds[3]:.4f}°")

# Calculate area
if pakistan_gdf.crs.is_geographic:
    # Convert to appropriate projected CRS for Pakistan
    pakistan_gdf_projected = pakistan_gdf.to_crs('EPSG:32643')  # UTM Zone 43N for Pakistan
    total_area = pakistan_gdf_projected.geometry.area.sum() / 1e6  # Convert to km²
else:
    total_area = pakistan_gdf.geometry.area.sum() / 1e6

print(f"📐 Total Area: {total_area:,.0f} km²")

# Create basic plot
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
pakistan_gdf.plot(ax=ax, color='lightblue', edgecolor='darkblue', linewidth=0.8)
ax.set_title('Pakistan Administrative Boundaries', fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()

# Save plot
os.makedirs('data/outputs', exist_ok=True)
plt.savefig('data/outputs/pakistan_shapefile_overview.png', dpi=300, bbox_inches='tight')
print("✅ Overview map saved: data/outputs/pakistan_shapefile_overview.png")
plt.show()

# Save bounds for later use
bounds_dict = {
    'west': bounds[0],
    'south': bounds[1], 
    'east': bounds[2],
    'north': bounds[3],
    'level': level,
    'total_area_km2': total_area
}

import json
with open('data/processed/pakistan_bounds.json', 'w') as f:
    json.dump(bounds_dict, f, indent=2)

print("✅ Bounds saved: data/processed/pakistan_bounds.json")