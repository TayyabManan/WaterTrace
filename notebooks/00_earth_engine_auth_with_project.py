# notebooks/00_earth_engine_auth_with_project.py
import ee
import os

print("🔐 Setting up Earth Engine with Google Cloud Project...")

# Your project ID (replace with yours)
PROJECT_ID = "watertrace-gis-portfolio"  # UPDATE THIS!

print(f"🎯 Using project: {PROJECT_ID}")

try:
    # Step 1: Authenticate
    print("📝 Starting authentication...")
    ee.Authenticate()
    print("✅ Authentication successful!")
    
    # Step 2: Initialize with project
    print("🚀 Initializing with project...")
    ee.Initialize(project=PROJECT_ID)
    print("✅ Earth Engine initialized with project!")
    
    # Step 3: Test functionality
    print("🧪 Testing Earth Engine...")
    test_number = ee.Number(5).add(3)
    result = test_number.getInfo()
    print(f"✅ Test calculation: 5 + 3 = {result}")
    
    # Step 4: Test GRACE data access
    print("🛰️ Testing GRACE data access...")
    grace = ee.ImageCollection("NASA/GRACE/MASS_GRIDS/MASCON_CRI")
    first_image = grace.first()
    date = first_image.date().format('YYYY-MM-dd')
    print(f"✅ GRACE data accessible - first image: {date.getInfo()}")
    
    print("🎉 Earth Engine setup complete!")
    
    # Save project ID for future use
    config = {
        'project_id': PROJECT_ID,
        'setup_complete': True,
        'test_passed': True
    }
    
    import json
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/earth_engine_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure you created a Google Cloud Project")
    print("2. Enabled Earth Engine API in the project")
    print("3. Updated PROJECT_ID in this script")
    print("4. Have stable internet connection")