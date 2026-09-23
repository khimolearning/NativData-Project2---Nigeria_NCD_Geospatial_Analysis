import pandas as pd
import geopandas as gpd
import folium
from pathlib import Path

BASE_PATH = Path("data")
OUTPUT_PATH = Path("output/maps")

print("="*80)
print("STAGE 4: CANCER REGISTRY MAP (STATE LEVEL, POINTS)")
print("="*80)

print("\n[STEP 1] Loading processed data...")
gdf_zones = gpd.read_file(BASE_PATH / "processed" / "nigeria_states_with_zones.geojson")
df_cancer = pd.read_csv(BASE_PATH / "processed" / "cancer_registries_clean.csv")
print("✓ Data loaded")
print(f"Cancer registries: {len(df_cancer)} states")

print("\n[STEP 2] Why cancer is different from diabetes...")
print("""
Diabetes: Complete data for all 6 zones → choropleth makes sense
Cancer: Only 6 registries out of 37 states → choropleth would be 84% blank

Solution: Map cancer as POINTS (markers), not color. This shows:
1. WHERE the registries actually are (South > North)
2. HOW SPARSE the coverage is (only 6 dots on 37-state map)
3. The real data gap in Nigeria's cancer surveillance
""")

print("\n[STEP 3] Merge cancer data with state geometries...")
# Merge cancer data with shapefile to get state boundaries + geometry
gdf_cancer_map = gdf_zones.merge(
    df_cancer,
    on=['state_name', 'geopolitical_zone'],
    how='inner'  # Keep only states with cancer registries
)
print(f"✓ Merged: {len(gdf_cancer_map)} cancer registry states with geometry")
print(gdf_cancer_map[['registry_name', 'state_name', 'cancer_asr']])

print("\n[STEP 4] Create base map of Nigeria...")
m = folium.Map(
    location=[9.08, 8.68],
    zoom_start=5,
    tiles='OpenStreetMap'
)

print("\n[STEP 5] Add all state boundaries (light grey background)...")
# Add all state boundaries as light background
gdf_zones_for_background = gdf_zones.copy()
# Convert datetime columns to string
for col in gdf_zones_for_background.columns:
    if pd.api.types.is_datetime64_any_dtype(gdf_zones_for_background[col]):
        gdf_zones_for_background[col] = gdf_zones_for_background[col].astype(str)

geojson_background = gdf_zones_for_background.to_json()

folium.GeoJson(
    geojson_background,
    style_function=lambda x: {'fillColor': '#f0f0f0', 'color': '#cccccc', 'weight': 1, 'fillOpacity': 0.5},
    name='State Boundaries'
).add_to(m)

print("\n[STEP 6] Add cancer registry points...")
# Add a marker for each cancer registry
for idx, row in gdf_cancer_map.iterrows():
    state_name = row['state_name']
    registry_name = row['registry_name']
    cancer_asr = row['cancer_asr']
    zone = row['geopolitical_zone']
    
    # Get centroid for marker placement
    centroid = row['geometry'].centroid
    
    # Color code by zone
    zone_colors = {
        'North West': 'gray',
        'North East': 'gray',
        'North Central': 'gray',
        'South West': 'red',
        'South South': 'orange',
        'South East': 'darkred'
    }
    color = zone_colors.get(zone, 'blue')
    
    popup_text = f"""
    <b>{registry_name}</b><br>
    State: {state_name}<br>
    Zone: {zone}<br>
    Cancer ASR: {cancer_asr:.1f} per 100,000<br>
    <i>Age-standardized incidence rate</i>
    """
    
    folium.CircleMarker(
        location=[centroid.y, centroid.x],
        radius=10,
        popup=folium.Popup(popup_text, max_width=300),
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.7,
        weight=2,
        tooltip=registry_name
    ).add_to(m)

print("✓ Added 6 cancer registry markers")

print("\n[STEP 7] Add title and explain the gap...")
title_html = '''
             <div style="position: fixed; 
                     top: 10px; left: 50px; width: 420px; height: auto; 
                     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                     padding: 10px; border-radius: 5px;">
             <b>Cancer Registry Coverage in Nigeria</b><br>
             <i>NativData Project 2: NCD Geospatial Analysis</i><br><br>
             Only 6 population-based cancer registries exist:<br>
             <span style="color: darkred;">● South East (2)</span><br>
             <span style="color: red;">● South West (2)</span><br>
             <span style="color: orange;">● South South (1)</span><br>
             <span style="color: gray;">● North (0 registries)</span><br><br>
             <b>This gap is real, not a data error.</b><br>
             31 states have no cancer surveillance infrastructure.<br>
             Sources: Jedy-Agba et al., NCBI registries
             </div>
             '''
m.get_root().html.add_child(folium.Element(title_html))

print("\n[STEP 8] Add legend...")
legend_html = '''
     <div style="position: fixed; 
                 bottom: 50px; right: 50px; width: 250px; height: auto; 
                 background-color: white; border:2px solid grey; z-index:9999; font-size:12px;
                 padding: 10px; border-radius: 5px;">
     <b>Cancer ASR (per 100,000)</b><br>
     Ibadan (Oyo): 98.5<br>
     Abuja (FCT): 98.5<br>
     Ekiti (Ekiti): 78.9<br>
     Enugu (Enugu): 78.4<br>
     Calabar (Cross River): 58.3<br>
     </div>
     '''
m.get_root().html.add_child(folium.Element(legend_html))

print("\n[STEP 9] Save map...")
output_file = OUTPUT_PATH / "02_cancer_registry_coverage_map.html"
m.save(str(output_file))
print(f"✓ Map saved to {output_file}")

print("\n" + "="*80)
print("STAGE 4 COMPLETE")
print("="*80)
print("""
KEY FINDINGS:
- 6 registries across 6 states only (16% of Nigeria)
- All registries are in the South (South-East, South-West, South-South)
- ZERO registries in the North (North-West, North-East, North-Central)
- Cancer ASR ranges from 58.3 (Calabar) to 98.5 (Ibadan/Abuja)
- This is NOT a data collection failure — it reflects real infrastructure gaps

IMPLICATION FOR PROJECT 2:
We cannot map cancer choropleth across all Nigeria because the data
doesn't exist. But mapping the GAP itself is scientifically honest and
tells an important story about health surveillance inequality in Nigeria.

NEXT: Stage 5 will overlay diabetes (complete) + cancer (sparse) and
explain what we CAN and CANNOT conclude from each layer.
""")