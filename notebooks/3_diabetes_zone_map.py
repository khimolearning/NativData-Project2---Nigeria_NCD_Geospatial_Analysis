import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth
from pathlib import Path

BASE_PATH = Path("data")
OUTPUT_PATH = Path("output/maps")

print("="*80)
print("STAGE 3: DIABETES CHOROPLETH MAP (ZONE LEVEL)")
print("="*80)

print("\n[STEP 1] Loading processed data...")
gdf_zones = gpd.read_file(BASE_PATH / "processed" / "nigeria_states_with_zones.geojson")
df_diabetes = pd.read_csv(BASE_PATH / "processed" / "diabetes_by_zone_clean.csv")
print("✓ Data loaded")

print("\n[STEP 2] Aggregate state-level shapefile to zone level...")
# Group by zone and dissolve boundaries
gdf_zone_boundaries = gdf_zones.dissolve(by='geopolitical_zone', aggfunc='first')
gdf_zone_boundaries = gdf_zone_boundaries.reset_index()
print(f"✓ Created {len(gdf_zone_boundaries)} zone boundaries")
print(gdf_zone_boundaries[['geopolitical_zone']])

print("\n[STEP 3] Merge zone boundaries with diabetes data...")
gdf_diabetes_map = gdf_zone_boundaries.merge(
    df_diabetes,
    left_on='geopolitical_zone',
    right_on='geopolitical_zone',
    how='left'
)
print(f"✓ Merged zones with diabetes data")
print(gdf_diabetes_map[['geopolitical_zone', 'diabetes_percent']])

print("\n[STEP 4] Convert datetime columns to string, then to GeoJSON...")
# Find and convert any Timestamp columns
for col in gdf_diabetes_map.columns:
    if pd.api.types.is_datetime64_any_dtype(gdf_diabetes_map[col]):
        gdf_diabetes_map[col] = gdf_diabetes_map[col].astype(str)

geojson_data = gdf_diabetes_map.to_json()

print("\n[STEP 5] Create Folium map...")
# Center map on Nigeria (roughly 9.08, 8.68)
m = folium.Map(
    location=[9.08, 8.68],
    zoom_start=5,
    tiles='OpenStreetMap'
)

print("\n[STEP 6] Add diabetes choropleth layer...")
# Create choropleth
choropleth = folium.Choropleth(
    geo_data=geojson_data,
    name='Diabetes Prevalence by Zone',
    data=gdf_diabetes_map,
    columns=['geopolitical_zone', 'diabetes_percent'],
    key_on='properties.geopolitical_zone',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Diabetes Prevalence (%)'
)
choropleth.add_to(m)

print("\n[STEP 7] Add hover information...")
# Create feature group with popups for each zone
feature_group = folium.FeatureGroup(name='Zone Labels')
for idx, row in gdf_diabetes_map.iterrows():
    zone_name = row['geopolitical_zone']
    diabetes_pct = row['diabetes_percent']
    ci_lower = row['ci_lower']
    ci_upper = row['ci_upper']
    
    # Get centroid for popup placement
    centroid = row['geometry'].centroid
    
    popup_text = f"""
    <b>{zone_name}</b><br>
    Diabetes Prevalence: {diabetes_pct:.1f}%<br>
    95% CI: {ci_lower:.1f}% - {ci_upper:.1f}%<br>
    <i>Source: Uloko et al. 2018</i>
    """
    
    folium.Marker(
        location=[centroid.y, centroid.x],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(feature_group)

feature_group.add_to(m)

print("\n[STEP 8] Add title and legend...")
title_html = '''
             <div style="position: fixed; 
                     top: 10px; left: 50px; width: 400px; height: auto; 
                     background-color: white; border:2px solid grey; z-index:9999; font-size:16px;
                     padding: 10px; border-radius: 5px;">
             <b>Type 2 Diabetes Prevalence by Geopolitical Zone</b><br>
             <i>NativData Project 2: NCD Geospatial Analysis</i><br><br>
             Data: Uloko et al. 2018 meta-analysis<br>
             Coverage: All 6 geopolitical zones (complete)
             </div>
             '''
m.get_root().html.add_child(folium.Element(title_html))

print("\n[STEP 9] Save map...")
output_file = OUTPUT_PATH / "01_diabetes_zone_choropleth.html"
m.save(str(output_file))
print(f"✓ Map saved to {output_file}")

print("\n" + "="*80)
print("STAGE 3 COMPLETE")
print("="*80)
print("""
KEY FINDINGS:
- South South has highest diabetes prevalence (9.8%)
- North West has lowest (3.0%)
- Clear South-North divide, similar to Project 1's Pidgin pattern
- All 6 zones have data, so choropleth shows full Nigeria

NEXT: Stage 4 will map cancer registries (6 states only, as points).
""")