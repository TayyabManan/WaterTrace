# notebooks/04_earth_engine_setup.py
import ee
import geopandas as gpd

print("🛰️ Testing Earth Engine with your districts...")

# Test Earth Engine authentication
try:
    ee.Initialize()
    print("✅ Earth Engine ready!")
    
    # Load your districts
    pakistan_gdf = gpd.read_file("data/raw/pakistan_shapefile/pakistan.shp")
    bounds = pakistan_gdf.total_bounds
    
    # Create bounding box
    pakistan_bbox = ee.Geometry.Rectangle([bounds[0], bounds[1], bounds[2], bounds[3]])
    
    # Test GRACE data access
    grace = ee.ImageCollection("NASA/GRACE/MASS_GRIDS/MASCON_CRI")
    pakistan_grace = grace.filterBounds(pakistan_bbox).filterDate('2020-01-01', '2023-12-31')
    
    image_count = pakistan_grace.size().getInfo()
    print(f"📊 Available GRACE images for Pakistan: {image_count}")
    
    if image_count > 0:
        print("🎯 Ready for groundwater analysis!")
    else:
        print("⚠️ No GRACE images found - check date range")
        
except Exception as e:
    print(f"❌ Earth Engine error: {e}")
    print("💡 Run: earthengine authenticate")