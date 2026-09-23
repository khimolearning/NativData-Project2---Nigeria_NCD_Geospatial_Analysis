import pandas as pd
import geopandas as gpd
from pathlib import Path

BASE_PATH = Path("data")

print("="*80)
print("STAGE 2: DATA MERGING & PREPARATION")
print("="*80)

print("\n[STEP 1] Loading all raw data...")
df_cancer = pd.read_csv(BASE_PATH / "raw" / "cancer_registry_data.csv")
df_diabetes = pd.read_csv(BASE_PATH / "raw" / "diabetes_prevalence_by_zone.csv")
df_zones = pd.read_csv(BASE_PATH / "raw" / "states_and_zones.csv")
gdf_nigeria = gpd.read_file(BASE_PATH / "shapefiles" / "nga_admin1.shp")

print("✓ All files loaded")

print("\n[STEP 2] Understanding the geographic resolution problem...")
print(f"Cancer data: {len(df_cancer)} registries (sparse, only 6 states)")
print(f"Diabetes data: {len(df_diabetes)} zones (complete, all 6 zones)")
print(f"State reference: {len(df_zones)} states (all 37 + FCT)")
print("""
WHY THIS MATTERS:
- We cannot merge cancer and diabetes directly at state level because cancer
  only has 6 states, diabetes only has 6 zones.
- We need to work at both levels separately, then visualize what can and
  cannot be mapped together.
""")

print("\n[STEP 3] Merge shapefile with zone data...")
# Rename shapefile column to match our data
gdf_nigeria = gdf_nigeria.rename(columns={"adm1_name": "state_name"})

# Merge with zones
gdf_with_zones = gdf_nigeria.merge(df_zones, on="state_name", how="left")
print(f"✓ Merged shapefile with zones: {len(gdf_with_zones)} states")

# Check for mismatches
unmatched = gdf_with_zones[gdf_with_zones['geopolitical_zone'].isna()]
if len(unmatched) > 0:
    print(f"⚠ WARNING: {len(unmatched)} states did not match zones:")
    print(unmatched[['state_name']])
else:
    print("✓ All states matched to zones successfully")

print("\n[STEP 4] Prepare diabetes data (zone level)...")
df_diabetes_clean = df_diabetes[['geopolitical_zone', 'diabetes_prevalence_percent', 'ci_lower', 'ci_upper']].copy()
df_diabetes_clean = df_diabetes_clean.rename(columns={'diabetes_prevalence_percent': 'diabetes_percent'})
print(f"✓ Diabetes data ready for zone-level mapping:")
print(df_diabetes_clean)

print("\n[STEP 5] Prepare cancer data (state level, registries only)...")
df_cancer_clean = df_cancer[['registry_name', 'state_name', 'geopolitical_zone', 'asr_per_100000_both_sexes']].copy()
df_cancer_clean = df_cancer_clean.rename(columns={'asr_per_100000_both_sexes': 'cancer_asr'})
print(f"✓ Cancer data ready for state-level mapping:")
print(df_cancer_clean)

print("""
[STEP 6] Explain the next steps...

We now have THREE datasets at different geographic scales:

1. ZONE LEVEL: Diabetes for all 6 zones (complete coverage)
   → Can map as choropleth across all Nigeria

2. STATE LEVEL (REGISTRIES ONLY): Cancer for 6 states only
   → Can map as points/markers, NOT choropleth (too sparse)
   → Will show the geographic gap in Nigeria's cancer surveillance

3. SHAPEFILE + ZONES: All 37 states with zone assignments
   → Use as base layer for all maps

In Stage 3, we'll make a diabetes choropleth (complete). In Stage 4,
we'll make a cancer registry map (showing the gap). In Stage 5, we'll
overlay them carefully, acknowledging their different resolutions.
""")

print("\n[STEP 7] Save merged data for next stages...")
gdf_with_zones.to_file(BASE_PATH / "processed" / "nigeria_states_with_zones.geojson", driver='GeoJSON')
df_diabetes_clean.to_csv(BASE_PATH / "processed" / "diabetes_by_zone_clean.csv", index=False)
df_cancer_clean.to_csv(BASE_PATH / "processed" / "cancer_registries_clean.csv", index=False)
print("✓ All processed data saved")

print("\n" + "="*80)
print("STAGE 2 COMPLETE")
print("="*80)