# notebooks/02_enhanced_district_map_fixed.py
import geopandas as gpd
import folium
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

print("🌐 Creating enhanced district-level interactive map...")

# Load your district shapefile
shapefile_path = "data/raw/pakistan_shapefile/pakistan.shp"  # Update if different
pakistan_gdf = gpd.read_file(shapefile_path)

# Calculate center point
bounds = pakistan_gdf.total_bounds
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2

print(f"📍 Map center: [{center_lat:.4f}, {center_lon:.4f}]")

# Create map with better tiles
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles='CartoDB positron'
)

# Add different tile layers (fixed)
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('CartoDB dark_matter').add_to(m)
folium.TileLayer(
    tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png',
    attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    name='Stamen Terrain',
    overlay=False,
    control=True
).add_to(m)

# Define colors for each province
province_colors = {
    'Punjab': '#ff6b6b',
    'Sindh': '#4ecdc4', 
    'Balochistan': '#45b7d1',
    'Khyber Pakhtunkhwa': '#96ceb4',
    'KPK': '#96ceb4',  # Alternative name
    'FATA': '#96ceb4',  # Federally Administered Tribal Areas
    'Gilgit-Baltistan': '#fcea2b',
    'Azad Kashmir': '#ff9ff3',
    'Islamabad Capital Territory': '#54a0ff',
    'Islamabad': '#54a0ff'  # Alternative name
}

# Check unique provinces in your data
unique_provinces = pakistan_gdf['PROVINCE'].unique()
print(f"📋 Provinces in your data: {list(unique_provinces)}")

# Create province groups for layer control
province_groups = {}
for province in unique_provinces:
    province_groups[province] = folium.FeatureGroup(name=f"{province} Districts")

# Add districts colored by province
print("🎨 Adding districts to map...")
for idx, row in pakistan_gdf.iterrows():
    province = row['PROVINCE']
    district = row['DISTRICT']
    
    # Get color for province
    color = province_colors.get(province, '#95a5a6')  # Default gray if province not found
    
    # Create popup with district info
    popup_html = f"""
    <div style="width: 200px;">
        <h4><b>{district} District</b></h4>
        <p><b>Province:</b> {province}</p>
        <p><b>Alternative Name:</b> {row.get('D_name', 'N/A')}</p>
        <p><i>Groundwater monitoring zone</i></p>
    </div>
    """
    
    # Add district polygon
    district_layer = folium.GeoJson(
        row.geometry,
        style_function=lambda x, color=color: {
            'fillColor': color,
            'color': 'white',
            'weight': 1,
            'fillOpacity': 0.7,
            'opacity': 1
        },
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{district}, {province}"
    )
    
    # Add to appropriate province group
    if province in province_groups:
        district_layer.add_to(province_groups[province])
    else:
        district_layer.add_to(m)

# Add province groups to map
for group in province_groups.values():
    group.add_to(m)

# Add major cities with better icons
major_cities = [
    {"name": "Karachi", "coords": [24.8607, 67.0011], "pop": "14.9M", "province": "Sindh"},
    {"name": "Lahore", "coords": [31.5804, 74.3587], "pop": "11.1M", "province": "Punjab"},
    {"name": "Islamabad", "coords": [33.6844, 73.0479], "pop": "1.0M", "province": "ICT"},
    {"name": "Rawalpindi", "coords": [33.5651, 73.0169], "pop": "2.1M", "province": "Punjab"},
    {"name": "Faisalabad", "coords": [31.4504, 73.1350], "pop": "3.2M", "province": "Punjab"},
    {"name": "Multan", "coords": [30.1575, 71.5249], "pop": "1.9M", "province": "Punjab"},
    {"name": "Peshawar", "coords": [34.0151, 71.5249], "pop": "1.9M", "province": "KPK"},
    {"name": "Quetta", "coords": [30.1798, 66.9750], "pop": "1.0M", "province": "Balochistan"},
    {"name": "Hyderabad", "coords": [25.3792, 68.3683], "pop": "1.7M", "province": "Sindh"}
]

# Create city markers group
city_group = folium.FeatureGroup(name="Major Cities")

print("🏙️ Adding major cities...")
for city in major_cities:
    city_popup = f"""
    <div style="width: 180px;">
        <h4><b>{city['name']}</b></h4>
        <p><b>Population:</b> {city['pop']}</p>
        <p><b>Province:</b> {city['province']}</p>
        <p><i>Potential groundwater monitoring station</i></p>
    </div>
    """
    
    folium.CircleMarker(
        location=city["coords"],
        popup=folium.Popup(city_popup, max_width=200),
        tooltip=f"{city['name']} ({city['pop']})",
        radius=8,
        color='darkred',
        fill=True,
        fillColor='red',
        fillOpacity=0.8,
        weight=2
    ).add_to(city_group)

city_group.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Create dynamic legend based on actual provinces in data
province_counts = pakistan_gdf['PROVINCE'].value_counts()
legend_entries = []
for province, count in province_counts.items():
    color = province_colors.get(province, '#95a5a6')
    legend_entries.append(f'<p><span style="color:{color};">●</span> {province} ({count} districts)</p>')

legend_html = f'''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 300px; height: {100 + len(legend_entries) * 20}px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:12px; padding: 15px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
<h4 style="margin-top:0;"><b>WaterTrace - Pakistan Study Area</b></h4>
{"".join(legend_entries)}
<p><span style="color:darkred;">●</span> Major Cities</p>
<p><i>Total: {len(pakistan_gdf)} Districts for Groundwater Analysis</i></p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save enhanced map
os.makedirs('data/outputs', exist_ok=True)
m.save('data/outputs/pakistan_districts_enhanced.html')
print("✅ Enhanced district map saved: data/outputs/pakistan_districts_enhanced.html")

# Create summary statistics
print("\n📊 District Summary by Province:")
province_summary = pakistan_gdf.groupby('PROVINCE').size().sort_values(ascending=False)
for province, count in province_summary.items():
    print(f"   {province}: {count} districts")

# Save district information for later use
district_info = {
    'total_districts': len(pakistan_gdf),
    'provinces': pakistan_gdf['PROVINCE'].unique().tolist(),
    'province_counts': province_summary.to_dict(),
    'bounds': {
        'west': bounds[0],
        'south': bounds[1],
        'east': bounds[2], 
        'north': bounds[3]
    },
    'center': [center_lat, center_lon]
}

with open('data/processed/district_summary.json', 'w') as f:
    json.dump(district_info, f, indent=2)

print("✅ District summary saved: data/processed/district_summary.json")

# Create simple district distribution chart
plt.figure(figsize=(12, 6))
ax = province_summary.plot(kind='bar', color=['#ff6b6b', '#45b7d1', '#4ecdc4', '#96ceb4', '#fcea2b'][:len(province_summary)])
plt.title('Districts by Province - Pakistan Study Area', fontweight='bold', size=14)
plt.xlabel('Province')
plt.ylabel('Number of Districts')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Add value labels on bars
for i, v in enumerate(province_summary.values):
    ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

plt.savefig('data/outputs/districts_by_province.png', dpi=300, bbox_inches='tight')
print("✅ District chart saved: data/outputs/districts_by_province.png")
plt.show()

print("\n🎉 Enhanced district map completed successfully!")
print("📂 Open the HTML file to see your interactive map!")