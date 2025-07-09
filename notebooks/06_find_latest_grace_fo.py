# notebooks/11_find_latest_grace_fo.py
import ee
import json

print("🔍 Finding the latest GRACE-FO datasets for 2018-2024...")

# Load project configuration
with open('data/processed/earth_engine_config.json', 'r') as f:
    config = json.load(f)
PROJECT_ID = config['project_id']

ee.Initialize(project=PROJECT_ID)

# Test different GRACE-FO dataset variations
grace_fo_variations = [
    'NASA/GLDAS/V021/NOAH/G025/T3H',
    'NASA/GRACE/MASS_GRIDS/MASCON_CRI',
    'NASA/GRACE/MASS_GRIDS/LAND',
    'NASA/GRACE/MASS_GRIDS/OCEAN',
    'USGS/GLDAS/NOAH025/V2_1',
    'NASA/GRACE/MASS_GRIDS/MASCON'
]

# Also search the Earth Engine Data Catalog directly
print("🔍 Searching for GRACE and GRACE-FO datasets...")

# Let's check what's actually available by testing known working datasets
test_datasets = [
    {
        'name': 'GRACE Monthly Mass Grids',
        'id': 'NASA/GRACE/MASS_GRIDS/MASCON_CRI',
        'description': 'Original GRACE data'
    },
    {
        'name': 'GRACE Terrestrial Water Storage',
        'id': 'NASA/GRACE/MASS_GRIDS/LAND', 
        'description': 'Land water storage from GRACE'
    },
    {
        'name': 'GLDAS Noah (Alternative groundwater)',
        'id': 'NASA/GLDAS/V021/NOAH/G025/T3H',
        'description': 'Global Land Data Assimilation System'
    }
]

available_datasets = []

for dataset in test_datasets:
    try:
        print(f"\n📡 Testing: {dataset['name']}")
        print(f"   ID: {dataset['id']}")
        
        collection = ee.ImageCollection(dataset['id'])
        
        # Get total count
        total_count = collection.size().getInfo()
        
        if total_count > 0:
            # Get date range
            first_image = collection.limit(1, 'system:time_start', True).first()
            last_image = collection.limit(1, 'system:time_start', False).first()
            
            first_date = first_image.date().format('YYYY-MM-dd').getInfo()
            last_date = last_image.date().format('YYYY-MM-dd').getInfo()
            
            # Get band names
            bands = first_image.bandNames().getInfo()
            
            print(f"   ✅ {total_count} images")
            print(f"   📅 {first_date} to {last_date}")
            print(f"   🔧 Bands: {bands[:3]}..." if len(bands) > 3 else f"   🔧 Bands: {bands}")
            
            # Check if extends beyond 2017
            if last_date > '2018-01-01':
                print(f"   🎯 HAS RECENT DATA!")
            
            available_datasets.append({
                'name': dataset['name'],
                'id': dataset['id'],
                'total_images': total_count,
                'first_date': first_date,
                'last_date': last_date,
                'bands': bands,
                'has_recent_data': last_date > '2018-01-01'
            })
            
        else:
            print(f"   ❌ No images found")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}...")

# Filter for recent data
recent_datasets = [d for d in available_datasets if d['has_recent_data']]

if recent_datasets:
    print(f"\n🎉 Found {len(recent_datasets)} datasets with recent data!")
    
    for dataset in recent_datasets:
        print(f"\n🛰️ {dataset['name']}")
        print(f"   📅 Coverage: {dataset['first_date']} to {dataset['last_date']}")
        print(f"   📊 {dataset['total_images']} total images")
        
    # Save results
    with open('data/processed/recent_datasets.json', 'w') as f:
        json.dump(recent_datasets, f, indent=2)
        
else:
    print("⚠️ No datasets found with data beyond 2018")
    print("Let's try a different approach...")

# Alternative: Check NASA Giovanni (web interface) datasets
print("\n🌐 Alternative approach: Let's check what's available online...")
print("📋 According to NASA Giovanni, these should be available:")
print("   - GRACE: 2002-2017")
print("   - GRACE-FO: 2018-present")
print("   - GLDAS: 1948-present (alternative groundwater data)")

# Let's try GLDAS for recent groundwater data
print("\n🧪 Testing GLDAS for recent groundwater-related data...")
try:
    gldas = ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
    
    # Filter for recent years
    recent_gldas = gldas.filterDate('2020-01-01', '2024-01-01')
    recent_count = recent_gldas.size().getInfo()
    
    if recent_count > 0:
        print(f"✅ GLDAS has {recent_count} recent images!")
        
        # Get a sample image
        sample_image = recent_gldas.limit(1).first()
        bands = sample_image.bandNames().getInfo()
        date = sample_image.date().format('YYYY-MM-dd').getInfo()
        
        print(f"📅 Sample date: {date}")
        print(f"🔧 Available bands: {bands}")
        
        # Look for groundwater-related bands
        gw_bands = [band for band in bands if any(keyword in band.lower() for keyword in ['gws', 'groundwater', 'water', 'storage'])]
        
        if gw_bands:
            print(f"💧 Groundwater-related bands: {gw_bands}")
        else:
            print("📊 All bands (some may be groundwater-related):")
            for band in bands:
                print(f"   - {band}")
                
except Exception as e:
    print(f"❌ GLDAS error: {e}")

print("\n💡 Recommendations:")
print("1. Use GRACE data (2002-2017) for historical trends")
print("2. Use GLDAS data (2018-2024) for recent years") 
print("3. Combine both datasets for complete timeline")