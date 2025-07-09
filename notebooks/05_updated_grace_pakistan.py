# notebooks/05_updated_grace_pakistan.py
import ee
import geopandas as gpd
import json
import pandas as pd

print("🛰️ Processing Pakistan groundwater with updated GRACE data...")

# Load project configuration
with open('data/processed/earth_engine_config.json', 'r') as f:
    config = json.load(f)
PROJECT_ID = config['project_id']

# Initialize Earth Engine
ee.Initialize(project=PROJECT_ID)
print("✅ Earth Engine initialized!")

# Load Pakistan districts
pakistan_gdf = gpd.read_file("data/raw/pakistan_shapefile/pakistan.shp")
bounds = pakistan_gdf.total_bounds
pakistan_bbox = ee.Geometry.Rectangle([bounds[0], bounds[1], bounds[2], bounds[3]])

print("🔍 Checking available GRACE datasets...")

# Try different GRACE datasets (newest to oldest)
grace_datasets = [
    {
        'name': 'GRACE-FO (Latest)',
        'id': 'NASA/GRACE-FO/MASS_GRIDS/MASCON',
        'start_date': '2018-01-01'
    },
    {
        'name': 'GRACE (Updated)',
        'id': 'NASA/GRACE/MASS_GRIDS/MASCON',  
        'start_date': '2002-01-01'
    },
    {
        'name': 'GRACE (Original - Deprecated)',
        'id': 'NASA/GRACE/MASS_GRIDS/MASCON_CRI',
        'start_date': '2002-01-01'
    }
]

# Test each dataset
available_datasets = []
for dataset in grace_datasets:
    try:
        print(f"📡 Testing {dataset['name']}...")
        
        grace_collection = ee.ImageCollection(dataset['id'])
        pakistan_grace = grace_collection.filterBounds(pakistan_bbox).filterDate(
            dataset['start_date'], '2023-12-31'
        )
        
        image_count = pakistan_grace.size().getInfo()
        
        if image_count > 0:
            first_date = pakistan_grace.limit(1, 'system:time_start', True).first().date().format('YYYY-MM-dd').getInfo()
            last_date = pakistan_grace.limit(1, 'system:time_start', False).first().date().format('YYYY-MM-dd').getInfo()
            
            available_datasets.append({
                'name': dataset['name'],
                'id': dataset['id'],
                'image_count': image_count,
                'date_range': f"{first_date} to {last_date}",
                'first_date': first_date,
                'last_date': last_date
            })
            
            print(f"   ✅ {image_count} images available ({first_date} to {last_date})")
        else:
            print(f"   ❌ No images found")
            
    except Exception as e:
        print(f"   ❌ Error accessing {dataset['name']}: {str(e)[:100]}...")

# Use the best available dataset
if available_datasets:
    # Prefer GRACE-FO (newest), then GRACE (updated), then original
    best_dataset = available_datasets[0]
    print(f"\n🎯 Using: {best_dataset['name']}")
    print(f"📊 Images available: {best_dataset['image_count']}")
    print(f"📅 Date range: {best_dataset['date_range']}")
    
    # Load the chosen dataset
    grace = ee.ImageCollection(best_dataset['id'])
    groundwater = grace.select('lwe_thickness')
    
    # Filter for Pakistan and time period
    start_date = '2010-01-01'  # Start from 2010 for recent trends
    end_date = '2023-12-31'
    
    pakistan_gw = groundwater.filterDate(start_date, end_date).filterBounds(pakistan_bbox)
    
    print(f"\n⏳ Extracting Pakistan groundwater time series...")
    print(f"📅 Period: {start_date} to {end_date}")
    
    # Function to extract groundwater statistics
    def extract_groundwater_stats(image):
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=pakistan_bbox,
            scale=25000,  # 25km resolution
            maxPixels=1e9
        )
        
        return ee.Feature(None, {
            'date': image.date().format('YYYY-MM-dd'),
            'groundwater_anomaly': stats.get('lwe_thickness'),
            'system_time': image.get('system:time_start')
        })
    
    # Process time series
    gw_timeseries = pakistan_gw.map(extract_groundwater_stats)
    
    # Get the size to check
    series_count = gw_timeseries.size().getInfo()
    print(f"📈 Processing {series_count} time points...")
    
    if series_count > 0:
        # Export to Google Drive
        task = ee.batch.Export.table.toDrive(
            collection=gw_timeseries,
            description='pakistan_groundwater_updated_grace',
            folder='WaterTrace_Data',
            fileFormat='CSV'
        )
        
        task.start()
        print("✅ Export task started!")
        print("📁 Check Google Drive folder 'WaterTrace_Data' in 5-10 minutes")
        print("📄 File: pakistan_groundwater_updated_grace.csv")
        
        # Save task info
        task_info = {
            'task_id': task.id,
            'dataset_used': best_dataset['name'],
            'dataset_id': best_dataset['id'],
            'date_range': f"{start_date} to {end_date}",
            'expected_records': series_count,
            'export_started': True
        }
        
        with open('data/processed/grace_export_info.json', 'w') as f:
            json.dump(task_info, f, indent=2)
        
        print(f"\n🔄 Task ID: {task.id}")
        print("💡 Monitor progress with: task.status()")
        
        # Test a few data points immediately
        print("\n🧪 Testing data extraction...")
        sample_data = gw_timeseries.limit(5)
        sample_list = sample_data.getInfo()
        
        print("📋 Sample data points:")
        for feature in sample_list['features']:
            props = feature['properties']
            date = props.get('date', 'Unknown')
            value = props.get('groundwater_anomaly', 'No data')
            if value is not None and value != 'No data':
                print(f"   {date}: {value:.2f} cm")
            else:
                print(f"   {date}: No data")
    
    else:
        print("❌ No data points found for the specified period")

else:
    print("❌ No GRACE datasets available")

print("\n🎉 GRACE data processing setup complete!")