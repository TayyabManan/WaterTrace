# notebooks/14_complete_grace_gldas_timeline.py
import ee
import geopandas as gpd
import json

print("🚀 Creating complete Pakistan groundwater timeline (2002-2024)...")

# Load project configuration
with open('data/processed/earth_engine_config.json', 'r') as f:
    config = json.load(f)
PROJECT_ID = config['project_id']

ee.Initialize(project=PROJECT_ID)

# Load Pakistan bounds
pakistan_gdf = gpd.read_file("data/raw/pakistan_shapefile/pakistan.shp")
bounds = pakistan_gdf.total_bounds
pakistan_bbox = ee.Geometry.Rectangle([bounds[0], bounds[1], bounds[2], bounds[3]])

print(f"📏 Pakistan study area: [{bounds[0]:.3f}, {bounds[1]:.3f}, {bounds[2]:.3f}, {bounds[3]:.3f}]")

# ========================================
# PART 1: GRACE Historical Data (2002-2017)
# ========================================
print("\n🛰️ PART 1: Processing GRACE data (2002-2017)")

grace = ee.ImageCollection('NASA/GRACE/MASS_GRIDS/MASCON_CRI')
grace_pakistan = grace.filterBounds(pakistan_bbox).filterDate('2002-01-01', '2017-12-31')
grace_count = grace_pakistan.size().getInfo()

print(f"📊 GRACE images: {grace_count}")

def extract_grace_data(image):
    """Extract GRACE groundwater data for Pakistan"""
    stats = image.select('lwe_thickness').reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=pakistan_bbox,
        scale=25000,
        maxPixels=1e9
    )
    
    return ee.Feature(None, {
        'date': image.date().format('YYYY-MM-dd'),
        'groundwater_cm': stats.get('lwe_thickness'),
        'data_source': 'GRACE',
        'variable': 'lwe_thickness',
        'system_time': image.get('system:time_start')
    })

grace_timeseries = grace_pakistan.map(extract_grace_data)

# ========================================
# PART 2: GLDAS Recent Data (2018-2024)
# ========================================
print("\n🌱 PART 2: Processing GLDAS data (2018-2024)")

gldas = ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')

# Use deep soil moisture as groundwater proxy
groundwater_proxy_band = 'SoilMoi100_200cm_inst'  # 100-200cm depth
print(f"💧 Using groundwater proxy: {groundwater_proxy_band}")

# Filter GLDAS for recent period
gldas_pakistan = gldas.filterBounds(pakistan_bbox).filterDate('2018-01-01', '2024-12-31')
gldas_count = gldas_pakistan.size().getInfo()

print(f"📊 GLDAS images: {gldas_count}")
print("⏳ Note: GLDAS has 3-hourly data, we'll create monthly averages...")

def get_monthly_gldas(year, month):
    """Get monthly average GLDAS data"""
    monthly_data = gldas_pakistan.filter(
        ee.Filter.calendarRange(year, year, 'year')
    ).filter(
        ee.Filter.calendarRange(month, month, 'month')
    )
    
    # Calculate monthly mean
    monthly_mean = monthly_data.select(groundwater_proxy_band).mean()
    
    # Extract statistics for Pakistan
    stats = monthly_mean.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=pakistan_bbox,
        scale=25000,
        maxPixels=1e9
    )
    
    return ee.Feature(None, {
        'date': ee.Date.fromYMD(year, month, 15).format('YYYY-MM-dd'),
        'groundwater_cm': stats.get(groundwater_proxy_band),
        'data_source': 'GLDAS',
        'variable': groundwater_proxy_band,
        'year': year,
        'month': month
    })

# Create monthly time series for 2018-2024
print("📅 Creating monthly GLDAS time series...")
monthly_features = []

for year in range(2018, 2025):  # 2018-2024
    for month in range(1, 13):
        if year == 2024 and month > 12:  # Don't go beyond current date
            break
        monthly_features.append(get_monthly_gldas(year, month))

gldas_monthly = ee.FeatureCollection(monthly_features)
gldas_monthly_count = len(monthly_features)

print(f"📈 GLDAS monthly time points: {gldas_monthly_count}")

# ========================================
# PART 3: Export Both Datasets
# ========================================
print("\n📤 Starting exports...")

# Export GRACE data
grace_task = ee.batch.Export.table.toDrive(
    collection=grace_timeseries,
    description='pakistan_grace_2002_2017_complete',
    folder='WaterTrace_Data',
    fileFormat='CSV'
)
grace_task.start()

# Export GLDAS data  
gldas_task = ee.batch.Export.table.toDrive(
    collection=gldas_monthly,
    description='pakistan_gldas_2018_2024_monthly',
    folder='WaterTrace_Data', 
    fileFormat='CSV'
)
gldas_task.start()

print(f"✅ GRACE export started (Task: {grace_task.id})")
print(f"✅ GLDAS export started (Task: {gldas_task.id})")

# ========================================
# PART 4: Test Sample Data
# ========================================
print("\n🧪 Testing sample data extraction...")

# Test GRACE sample
print("📊 GRACE sample data:")
grace_sample = grace_timeseries.limit(3).getInfo()
for feature in grace_sample['features']:
    props = feature['properties']
    date = props.get('date', 'Unknown')
    value = props.get('groundwater_cm', 'No data')
    print(f"   {date}: {value:.2f} cm" if value else f"   {date}: No data")

# Test GLDAS sample
print("\n🌱 GLDAS sample data:")
gldas_sample = gldas_monthly.limit(3).getInfo()
for feature in gldas_sample['features']:
    props = feature['properties']
    date = props.get('date', 'Unknown')
    value = props.get('groundwater_cm', 'No data')
    print(f"   {date}: {value:.4f} m³/m³" if value else f"   {date}: No data")

# ========================================
# PART 5: Save Export Information
# ========================================
export_summary = {
    'datasets': {
        'grace_historical': {
            'period': '2002-2017',
            'images': grace_count,
            'task_id': grace_task.id,
            'band': 'lwe_thickness',
            'unit': 'cm',
            'description': 'Actual groundwater anomaly from GRACE satellites'
        },
        'gldas_recent': {
            'period': '2018-2024',
            'monthly_points': gldas_monthly_count,
            'task_id': gldas_task.id,
            'band': groundwater_proxy_band,
            'unit': 'm³/m³',
            'description': 'Deep soil moisture (100-200cm) as groundwater proxy'
        }
    },
    'complete_timeline': {
        'period': '2002-2024',
        'total_years': 22,
        'grace_years': '2002-2017 (15 years)',
        'gldas_years': '2018-2024 (7 years)',
        'overlap_analysis': 'Can calibrate GLDAS against GRACE using 2017 overlap'
    },
    'next_steps': [
        'Wait for exports to complete (5-10 minutes)',
        'Download CSV files from Google Drive',
        'Harmonize the two datasets',
        'Create complete 22-year timeline',
        'Analyze trends and patterns'
    ]
}

with open('data/processed/complete_timeline_summary.json', 'w') as f:
    json.dump(export_summary, f, indent=2)

print("\n🎉 Complete timeline setup finished!")
print("\n📁 Expected files in Google Drive > WaterTrace_Data:")
print("   1. pakistan_grace_2002_2017_complete.csv")
print("   2. pakistan_gldas_2018_2024_monthly.csv")

print(f"\n📊 Timeline Summary:")
print(f"   🛰️ GRACE: 2002-2017 ({grace_count} measurements)")
print(f"   🌱 GLDAS: 2018-2024 ({gldas_monthly_count} monthly averages)")
print(f"   📈 Total: 22 years of groundwater data!")

print("\n💡 Next: Run export status checker in 10 minutes")