"""
Script 04 — Combine all sources into final GeoJSON
"""
import geopandas as gpd
import pandas as pd
import numpy as np
import os

os.makedirs("output", exist_ok=True)

print("Loading boundaries...")
gdf = gpd.read_file("data/raw/countries.gpkg")

print("Loading INFORM...")
inform = pd.read_csv("data/processed/inform.csv")

print("Loading World Bank...")
wb = pd.read_csv("data/processed/worldbank.csv")

gdf = gdf.merge(inform, on="iso3", how="left")
gdf = gdf.merge(wb[["iso3","population","gdp_per_capita","wb_vulnerability","wb_coping"]], on="iso3", how="left")

# Component scores (0-1 scale)
gdf["hazard"] = gdf["inform_flood_norm"].fillna(gdf["inform_hazard_norm"])
gdf["vulnerability"] = (
    gdf["inform_vulnerability_norm"].fillna(0) * 0.7 +
    gdf["wb_vulnerability"].fillna(0) * 0.3
)
gdf["coping_lack"] = (
    gdf["inform_coping_lack_norm"].fillna(0) * 0.7 +
    (1 - gdf["wb_coping"].fillna(0.5)) * 0.3
)

# Default risk score
W_HAZARD, W_VULN, W_COPING = 0.40, 0.35, 0.25
raw = W_HAZARD * gdf["hazard"] + W_VULN * gdf["vulnerability"] + W_COPING * gdf["coping_lack"]
mn, mx = raw.min(), raw.max()
gdf["risk_score"] = ((raw - mn) / (mx - mn + 1e-9) * 10).round(2)

bins   = [0, 2, 4, 6, 8, 10]
labels = ["Very Low", "Low", "Medium", "High", "Very High"]
gdf["risk_tier"] = pd.cut(gdf["risk_score"], bins=bins, labels=labels, include_lowest=True).astype(str)

# Simplify geometry to reduce file size
gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.1, preserve_topology=True)

gdf.to_file("output/global_flood_risk.geojson", driver="GeoJSON")
print(f"Saved output/global_flood_risk.geojson ({os.path.getsize('output/global_flood_risk.geojson')//1024} KB)")
