# NativData Project 2: Nigeria NCD Geospatial Analysis

## Overview

This project maps the geographic distribution of two non-communicable diseases (NCDs) in Nigeria: type 2 diabetes and cancer. It examines how health burden relates to Nigeria's geopolitical and economic geography, and uncovers a critical data gap in cancer surveillance that reflects real infrastructure inequality.

**Goal:** Build geospatial visualizations showing diabetes prevalence across all 6 geopolitical zones and cancer registry coverage (6 states only), then overlay them to reveal patterns in health surveillance inequality.

**Data Sources:**
- Diabetes: Uloko et al. 2018 meta-analysis (peer-reviewed, all 6 zones)
- Cancer: Population-based cancer registries from NCBI/GLOBOCAN (6 registries, 6 states)
- Geography: Nigeria admin-1 shapefile from HumanData

---

## Project Structure

```
nativdata-p2-ncd-geospatial/
├── data/
│   ├── raw/
│   │   ├── cancer_registry_data.csv
│   │   ├── diabetes_prevalence_by_zone.csv
│   │   └── states_and_zones.csv
│   ├── shapefiles/
│   │   └── nga_admin1.* (all 5 files)
│   └── processed/
│       ├── nigeria_states_with_zones.geojson
│       ├── diabetes_by_zone_clean.csv
│       └── cancer_registries_clean.csv
├── notebooks/
│   ├── 1_load_data.py
│   ├── 2_merge_data.py
│   ├── 3_diabetes_zone_map.py
│   ├── 4_cancer_registry_map.py
│   └── 5_overlay_ncd_analysis.py
├── output/
│   └── maps/
│       ├── 01_diabetes_zone_choropleth.html
│       ├── 02_cancer_registry_coverage_map.html
│       └── 03_overlay_diabetes_cancer_map.html
└── README.md
```

---

## Stages

### Stage 1: Data Loading & Exploration
**File:** `notebooks/1_load_data.py`

Load and inspect all raw data:
- Cancer registries (6 registries across 6 states)
- Diabetes prevalence by geopolitical zone (all 6 zones)
- State-to-zone mapping (37 states + FCT)
- Nigeria state boundaries (shapefile)

**Output:** Console summary of data structure and counts.

### Stage 2: Data Merging & Preparation
**File:** `notebooks/2_merge_data.py`

Merge data at appropriate geographic levels:
- Merge shapefile with zone assignments (state level)
- Clean cancer data for registry-only states (6 states)
- Clean diabetes data for zone-level mapping (6 zones)

**Key insight:** Cancer and diabetes are at different geographic resolutions, so they cannot be directly merged. We work at both levels separately, then overlay carefully.

**Output:** Processed GeoJSON and CSV files saved to `data/processed/`.

### Stage 3: Diabetes Choropleth Map
**File:** `notebooks/3_diabetes_zone_map.py`

Create zone-level choropleth showing diabetes prevalence across all Nigeria.

**Data:** Uloko et al. 2018 meta-analysis (all 6 zones)

**Map:** `01_diabetes_zone_choropleth.html`
- Color gradient: Yellow-Orange-Red (low to high prevalence)
- Interactive popups showing 95% confidence intervals
- Full geographic coverage (all Nigeria)

**Key finding:** South-North divide. South South has highest prevalence (9.8%), North West lowest (3.0%).

### Stage 4: Cancer Registry Coverage Map
**File:** `notebooks/4_cancer_registry_map.py`

Map cancer registries as POINTS, not choropleth, because only 6 registries exist.

**Data:** Population-based cancer registries from NCBI (Jedy-Agba et al., individual state registries)

**Map:** `02_cancer_registry_coverage_map.html`
- Points color-coded by zone
- Circle size proportional to ASR (age-standardized incidence rate)
- Background shows all state boundaries (light grey) to emphasize the gap

**Key finding:** All 6 registries are in the South (South-East: 2, South-West: 2, South-South: 1). ZERO in the North (North-West, North-East, North-Central).

**Critical note:** This gap is NOT a data collection error. It reflects real infrastructure inequality in Nigeria's cancer surveillance system.

### Stage 5: Overlay Analysis
**File:** `notebooks/5_overlay_ncd_analysis.py`

Overlay diabetes choropleth (complete) with cancer registry points (sparse).

**Map:** `03_overlay_diabetes_cancer_map.html`

**Key insight:** The South has both high diabetes prevalence AND cancer registry coverage. The North has documented high diabetes prevalence but ZERO cancer registries. This reveals a surveillance inequality problem.

---

## Key Findings

### Diabetes (Complete Data)
| Zone | Prevalence | 95% CI |
|------|-----------|--------|
| North West | 3.0% | 1.7-4.3% |
| North East | 5.9% | 2.4-9.4% |
| North Central | 3.8% | 2.9-4.7% |
| South West | 5.5% | 4.0-7.1% |
| South East | 4.6% | 3.4-5.9% |
| South South | 9.8% | 7.2-12.4% |

**Pattern:** South South significantly higher than North. Likely driven by urbanization, income, and lifestyle factors in oil-rich, densely urban zones.

### Cancer (Sparse Data)
| Registry | State | ASR (per 100,000) | Zone |
|----------|-------|------------------|------|
| Ibadan | Oyo | 98.5 | South West |
| Abuja | FCT | 98.5 | North Central |
| Ekiti | Ekiti | 78.9 | South West |
| Enugu | Enugu | 78.4 | South East |
| Calabar | Cross River | 58.3 | South South |

**Pattern:** Only 6 registries. 5 of 6 in the South. ASR ranges 58-98 per 100,000 where data exists.

### The Surveillance Inequality
- Diabetes: Data for 100% of Nigeria (all 6 zones)
- Cancer: Data for 16% of Nigeria (6 states only, all South-concentrated)

This means:
1. We can make confident statements about diabetes distribution across Nigeria
2. We CANNOT make statements about cancer distribution nationally
3. Cancer burden in the North is invisible, not absent
4. This reflects structural health system inequality

---

## Data Sources & Citations

### Diabetes
**Uloko AE, Mba CM, Uloko AT.** (2018). "The prevalence of diabetes mellitus in Nigeria: A systematic review and meta-analysis." *Primary Care Diabetes*. PubMed: 29807817. PMC: PMC5984944.

Provides zone-level prevalence estimates with 95% confidence intervals for all 6 geopolitical zones.

### Cancer
**Jedy-Agba E, Curado MP, Ogunbiyi O, et al.** (2012). "Cancer incidence in Nigeria: A report from population-based cancer registries." *Cancer Epidemiology*. PubMed: 22621842.

**State-level registries from NCBI Bookshelf:**
- Ibadan Cancer Registry (Jedy-Agba et al. 2012)
- Abuja Cancer Registry (Jedy-Agba et al. 2012)
- Calabar Cancer Registry (Cross River State NCBI 581069)
- Ekiti Cancer Registry (Ekiti State NCBI 581056)
- Enugu Cancer Registry (Enugu State NCBI 581076)

### Geography
Nigeria state boundaries: HumanData Humanitarian Data Exchange (COD AB NGA). Shapefile with admin-1 (state) level boundaries.


## Learning Objectives

**What this project teaches:**
1. Working with data at multiple geographic resolutions (state vs. zone)
2. Merging geospatial and tabular data
3. Honest data visualization: showing gaps, not hiding them
4. Reading and citing peer-reviewed medical literature
5. Recognizing when data ABSENCE tells a story (infrastructure inequality)

---

## Limitations

1. **Cancer data is sparse:** Only 6 registries. Cannot infer national cancer burden.
2. **Diabetes data is zone-level only:** Not state-level. Hides within-zone variation.
3. **Study periods differ:** Diabetes meta-analysis uses mixed years; registries use 2009-2016 period.
4. **No individual-level data:** All data is aggregated by geography, so cannot link individual diabetes+cancer status.

---

## Future Directions

Later in the future, I wish to add; 
1. socioeconomic context (urbanization, GDP, healthcare spending by zone)
2. Incorporate hospital-based cancer registries to improve coverage
3. State-level diabetes estimates (if NDHS data becomes available)
4. Temporal analysis: trend in diabetes/cancer over years
5. Overlay with health facility density to explain surveillance gaps

---

## Author

**Olokhimo Oluwasunmisola Osawere (Khimo)**
NativData Project 2
Data Science Portfolio for Postgraduate Applications
Lagos, Nigeria
September 2026

---

## Acknowledgments

Data sources: Uloko et al. (diabetes), Jedy-Agba et al. and NCBI registries (cancer), HumanData (geography).

This project is part of the NativData initiative, where i analyze open source data, to get more information that can help my community.
DISCLAIMER: I AM STILL A LEARNER!!!
