import pandas as pd
import geopandas as gpd
from pathlib import Path

BASE_PATH = Path("data")

print("="*80)
print("STAGE 1: DATA LOADING & EXPLORATION")
print("="*80)

print("\n[STEP 1] Loading cancer registry data...")
df_cancer = pd.read_csv(BASE_PATH / "raw" / "cancer_registry_data.csv")
print(f"✓ Loaded {len(df_cancer)} cancer registries")
print(df_cancer[['registry_name', 'state_name', 'asr_per_100000_both_sexes']])

print("\n[STEP 2] Loading diabetes prevalence by zone...")
df_diabetes = pd.read_csv(BASE_PATH / "raw" / "diabetes_prevalence_by_zone.csv")
print(f"✓ Loaded {len(df_diabetes)} zones")
print(df_diabetes)

print("\n[STEP 3] Loading states and zones reference...")
df_zones = pd.read_csv(BASE_PATH / "raw" / "states_and_zones.csv")
print(f"✓ Loaded {len(df_zones)} states")

print("\n[STEP 4] Loading Nigeria shapefile...")
gdf_nigeria = gpd.read_file(BASE_PATH / "shapefiles" / "nga_admin1.shp")
print(f"✓ Loaded {len(gdf_nigeria)} state boundaries")
print(f"Columns: {list(gdf_nigeria.columns)}")

print("\n" + "="*80)
print("STAGE 1 COMPLETE")
print("="*80)
print(f"""
Important note about this dataset:

Cancer data covers only 6 registries (out of 37 states). This reflects a
REAL, documented gap in Nigeria's cancer surveillance infrastructure, not
a mistake in data collection. Two-thirds of Nigeria's registries are in
the south. We will map this gap directly, not hide it.

Diabetes data covers all 6 geopolitical zones from a real meta-analysis.

Next: Stage 2 will merge what can be merged and clearly flag what can't.
""")