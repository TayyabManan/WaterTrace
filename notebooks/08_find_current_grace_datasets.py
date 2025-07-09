# notebooks/17_find_current_grace_datasets.py
import ee
import json
import requests
from datetime import datetime

print("🔍 Finding current, non-deprecated GRACE/GRACE-FO datasets...")

# Load project configuration
with open('data/processed/earth_engine_config.json', 'r') as f:
    config = json.load(f)
PROJECT_ID = config['project_id']

ee.Initialize(project=PROJECT_ID)

print("📡 Testing current GRACE dataset options...")

# Based on Earth Engine documentation, let's test current datasets
current_datasets = [
    {
        'name': 'GRACE/GRACE-FO Mascon (JPL)',
        'id': 'NASA/GRACE/MASS_GRIDS/MASCON_CRI_V02',
        'description': 'Updated GRACE mascon data'
    },
    {
        'name': 'GRACE/GRACE-FO Monthly Mass Grids',
        'id': 'NASA/GRACE/MASS_GRIDS/OCEAN_EOFR',
        'description': 'Ocean bottom pressure'
    },
    {
        'name': 'GRACE/GRACE-FO Land Water Storage',
        'id': 'NASA/GRACE/MASS_GRIDS/LAND_AO',
        'description': 'Land water storage anomalies'
    },
    {
        'name': 'GRACE Alternative Processing',
        'id': 'NASA/GRACE/MASS_GRIDS/MASCON',
        'description': 'Alternative GRACE processing'
    },
    # Test different GRACE-FO naming conventions
    {
        'name': 'GRACE-FO CSR Mascon',
        'id': 'CSR/GRACE-FO/MASCON',
        'description': 'GRACE-FO from CSR'
    },
    {
        'name': 'GRACE-FO JPL Mascon',
        'id': 'JPL/GRACE-FO/MASCON', 
        'description': 'GRACE-FO from JPL'
    },
    {
        'name': 'GRACE-FO GFZ Mascon',
        'id': 'GFZ/GRACE-FO/MASCON',
        'description': 'GRACE-FO from GFZ'
    }
]

# Also test some alternative current datasets
alternative_datasets = [
    {
        'name': 'MODIS Global Terrestrial Evapotranspiration',
        'id': 'MODIS/NTSG/MOD16A2/105',
        'description': 'Current evapotranspiration data'
    },
    {
        'name': 'ERA5 Reanalysis (Latest)',
        'id': 'ECMWF/ERA5/DAILY',
        'description': 'Recent weather reanalysis with soil moisture'
    },
    {
        'name': 'GPM Precipitation (Current)',
        'id': 'NASA/GPM_L3/IMERG_V06',
        'description': 'Current precipitation data'
    }
]

all_test_datasets = current_datasets + alternative_datasets

working_datasets = []
deprecated_datasets = []

for dataset in all_test_datasets:
    try:
        print(f"\n🧪 Testing: {dataset['name']}")
        print(f"   ID: {dataset['id']}")
        
        # Try to access the collection
        collection = ee.ImageCollection(dataset['id'])
        
        # Get basic info
        size = collection.size().getInfo()
        
        if size > 0:
            # Get date range
            first_image = collection.limit(1, 'system:time_start', True).first()
            last_image = collection.limit(1, 'system:time_start', False).first()
            
            first_date = first_image.date().format('YYYY-MM-dd').getInfo()
            last_date = last_image.date().format('YYYY-MM-dd').getInfo()
            
            # Get bands
            bands = first_image.bandNames().getInfo()
            
            # Check if recent (2020+)
            has_recent_data = last_date >= '2020-01-01'
            
            dataset_info = {
                'name': dataset['name'],
                'id': dataset['id'],
                'description': dataset['description'],
                'total_images': size,
                'first_date': first_date,
                'last_date': last_date,
                'bands': bands,
                'has_recent_data': has_recent_data,
                'status': 'working'
            }
            
            working_datasets.append(dataset_info)
            
            print(f"   ✅ {size} images available")
            print(f"   📅 {first_date} to {last_date}")
            print(f"   🔧 Bands: {bands[:3]}..." if len(bands) > 3 else f"   🔧 Bands: {bands}")
            
            if has_recent_data:
                print(f"   🎯 HAS RECENT DATA (2020+)")
            
        else:
            print(f"   ❌ No images found")
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {error_msg[:100]}...")
        
        # Check if it's a deprecation error
        if 'deprecated' in error_msg.lower():
            deprecated_datasets.append({
                'name': dataset['name'],
                'id': dataset['id'],
                'error': 'deprecated'
            })

# Summary of findings
print("\n" + "="*60)
print("📊 DATASET ANALYSIS SUMMARY")
print("="*60)

current_datasets_found = [d for d in working_datasets if d['has_recent_data']]

if current_datasets_found:
    print(f"\n✅ Found {len(current_datasets_found)} datasets with recent data:")
    
    for dataset in current_datasets_found:
        print(f"\n🛰️ {dataset['name']}")
        print(f"   📅 Coverage: {dataset['first_date']} to {dataset['last_date']}")
        print(f"   📊 Images: {dataset['total_images']}")
        print(f"   🔧 Key bands: {dataset['bands'][:3]}")
        
        # Check for groundwater-related bands
        gw_bands = [band for band in dataset['bands'] if any(keyword in band.lower() 
                   for keyword in ['lwe', 'water', 'storage', 'thickness', 'gwf', 'gws'])]
        
        if gw_bands:
            print(f"   💧 Groundwater bands: {gw_bands}")
        
else:
    print("⚠️ No current datasets found with recent data")

# Alternative: Check for GLDAS and other hydrological datasets
print(f"\n🌊 Checking alternative hydrological datasets...")

hydro_datasets = [
    'NASA/GLDAS/V021/NOAH/G025/T3H',  # We know this works
    'ECMWF/ERA5_LAND/DAILY',
    'NASA/USDA/HSL/SMAP10KM_soil_moisture',
    'NASA/SMAP/SPL4SMGP/007'
]

print("\n🔍 Testing proven alternative datasets:")

for dataset_id in hydro_datasets:
    try:
        collection = ee.ImageCollection(dataset_id)
        size = collection.size().getInfo()
        
        if size > 0:
            # Test recent data
            recent = collection.filterDate('2023-01-01', '2024-01-01')
            recent_size = recent.size().getInfo()
            
            if recent_size > 0:
                bands = recent.limit(1).first().bandNames().getInfo()
                print(f"✅ {dataset_id}: {recent_size} recent images")
                print(f"   Bands: {bands[:5]}...")
                
                # Look for water-related bands
                water_bands = [band for band in bands if any(keyword in band.lower() 
                              for keyword in ['moi', 'water', 'gws', 'soil', 'wet'])]
                if water_bands:
                    print(f"   💧 Water-related: {water_bands}")
            
    except Exception as e:
        print(f"❌ {dataset_id}: {str(e)[:50]}...")

# Save findings
findings = {
    'analysis_date': datetime.now().isoformat(),
    'working_datasets': working_datasets,
    'current_datasets_with_recent_data': current_datasets_found,
    'deprecated_datasets': deprecated_datasets,
    'recommendations': [],
    'next_steps': []
}

# Generate recommendations
if current_datasets_found:
    findings['recommendations'].append("Use current, non-deprecated datasets found")
    for dataset in current_datasets_found[:2]:  # Top 2
        findings['recommendations'].append(f"Primary option: {dataset['name']} ({dataset['id']})")

findings['recommendations'].append("Use GLDAS V021 for recent years (proven to work)")
findings['recommendations'].append("Combine multiple datasets for complete timeline")

findings['next_steps'] = [
    "Test the recommended datasets with Pakistan boundaries",
    "Create export scripts using current datasets only", 
    "Ensure no deprecation warnings in final code",
    "Document dataset versions for reproducibility"
]

with open('data/processed/current_datasets_analysis.json', 'w') as f:
    json.dump(findings, f, indent=2)

print(f"\n💾 Analysis saved to: data/processed/current_datasets_analysis.json")

print(f"\n🎯 RECOMMENDATIONS:")
print(f"1. Use GLDAS V021 (2000-2025) - proven current dataset")
print(f"2. Use ERA5 or SMAP for additional validation")
print(f"3. Avoid all deprecated GRACE datasets")
print(f"4. Focus on current, maintained datasets only")

print(f"\n✅ Ready to create future-proof analysis!")