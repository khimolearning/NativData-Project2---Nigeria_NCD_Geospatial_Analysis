import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth
from pathlib import Path
import numpy as np

BASE_PATH = Path("data")
OUTPUT_PATH = Path("output/maps")

print("="*80)
print("STAGE 5: OVERLAY NCD ANALYSIS (DIABETES + CANCER)")
print("="*80)

print("\n[STEP 1] Loading all processed data...")
gdf_zones = gpd.read_file(BASE_PATH / "processed" / "nigeria_states_with_zones.geojson")
df_diabetes = pd.read_csv(BASE_PATH / "processed" / "diabetes_by_zone_clean.csv")
df_cancer = pd.read_csv(BASE_PATH / "processed" / "cancer_registries_clean.csv")
print("✓ Data loaded")

print("\n[STEP 2] Aggregate shapefile to zone level...")
gdf_zone_boundaries = gdf_zones.dissolve(by='geopolitical_zone', aggfunc='first')
gdf_zone_boundaries = gdf_zone_boundaries.reset_index()

print("\n[STEP 3] Merge zones with diabetes data...")
gdf_diabetes_map = gdf_zone_boundaries.merge(
    df_diabetes,
    left_on='geopolitical_zone',
    right_on='geopolitical_zone',
    how='left'
)

# Convert datetime columns to string
for col in gdf_diabetes_map.columns:
    if pd.api.types.is_datetime64_any_dtype(gdf_diabetes_map[col]):
        gdf_diabetes_map[col] = gdf_diabetes_map[col].astype(str)

geojson_diabetes = gdf_diabetes_map.to_json()

print("\n[STEP 4] Prepare cancer registry data...")
gdf_cancer_map = gdf_zones.merge(
    df_cancer,
    on=['state_name', 'geopolitical_zone'],
    how='inner'
)

print("\n[STEP 5] Create overlay map with diabetes choropleth + cancer points...")
m = folium.Map(
    location=[9.08, 8.68],
    zoom_start=5,
    tiles='OpenStreetMap'
)

print("\n[STEP 6] Add diabetes choropleth layer...")
choropleth = folium.Choropleth(
    geo_data=geojson_diabetes,
    name='Diabetes Prevalence by Zone',
    data=gdf_diabetes_map,
    columns=['geopolitical_zone', 'diabetes_percent'],
    key_on='properties.geopolitical_zone',
    fill_color='YlOrRd',
    fill_opacity=0.6,
    line_opacity=0.3,
    legend_name='Diabetes Prevalence (%)'
)
choropleth.add_to(m)

print("\n[STEP 7] Add cancer registry markers on top...")
zone_colors = {
    'North West': 'gray',
    'North East': 'gray',
    'North Central': 'gray',
    'South West': 'blue',
    'South South': 'purple',
    'South East': 'darkblue'
}

for idx, row in gdf_cancer_map.iterrows():
    state_name = row['state_name']
    registry_name = row['registry_name']
    cancer_asr = row['cancer_asr']
    zone = row['geopolitical_zone']
    
    centroid = row['geometry'].centroid
    color = zone_colors.get(zone, 'black')
    
    popup_text = f"""
    <b>{registry_name}</b><br>
    State: {state_name}<br>
    Zone: {zone}<br>
    Cancer ASR: {cancer_asr:.1f} per 100,000
    """
    
    folium.CircleMarker(
        location=[centroid.y, centroid.x],
        radius=12,
        popup=folium.Popup(popup_text, max_width=300),
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.8,
        weight=2,
        tooltip=registry_name
    ).add_to(m)

print("✓ Added diabetes choropleth + cancer markers")

print("\n[STEP 8] Add title...")
title_html = '''
             <div style="position: fixed; 
                     top: 10px; left: 50px; width: 450px; height: auto; 
                     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                     padding: 10px; border-radius: 5px;">
             <b>Nigeria NCD Geospatial Analysis</b><br>
             <i>Diabetes Prevalence + Cancer Registry Coverage</i><br><br>
             <b>Background (Red-Yellow):</b> Type 2 Diabetes by zone (complete data)<br>
             <b>Dots:</b> Cancer registries (sparse data, South-concentrated)<br><br>
             South has BOTH high diabetes AND cancer surveillance.<br>
             North has high diabetes but NO cancer registries.
             </div>
             '''
m.get_root().html.add_child(folium.Element(title_html))

print("\n[STEP 9] Add layer control...")
folium.LayerControl().add_to(m)

print("\n[STEP 10] Save overlay map...")
output_file = OUTPUT_PATH / "03_overlay_diabetes_cancer_map.html"
m.save(str(output_file))
print(f"✓ Map saved to {output_file}")

print("\n[STEP 11] Calculate zone-level summary statistics...")
print("\nDiabetes by zone:")
print(gdf_diabetes_map[['geopolitical_zone', 'diabetes_percent']].to_string(index=False))

print("\n\nCancer registries by zone:")
cancer_by_zone = df_cancer.groupby('geopolitical_zone').agg({
    'registry_name': 'count',
    'cancer_asr': ['mean', 'min', 'max']
}).round(2)
cancer_by_zone.columns = ['num_registries', 'mean_asr', 'min_asr', 'max_asr']
print(cancer_by_zone)

print("\n" + "="*80)
print("STAGE 5 COMPLETE")
print("="*80)
print("""
KEY INSIGHT:
The overlay reveals a SURVEILLANCE INEQUALITY pattern:
- South has complete diabetes data + complete cancer registry coverage
- North has complete diabetes data + ZERO cancer registries

This is not because Northerners have no cancer. It's because cancer
surveillance infrastructure follows South-to-North economic/urban gradients.

Both diseases are likely under-recognized in the North due to weak
health information systems, not actual absence.

NEXT: Stage 6 documents all findings in README.md and analysis summary.
""")
