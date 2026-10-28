from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
import pandas as pd
import numpy as np
import json

app = FastAPI(title="Global Flood Risk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

gdf = gpd.read_file("output/global_flood_risk.geojson")

def compute_risk(gdf_in, w_hazard, w_vuln, w_coping):
    df = gdf_in.copy()
    total = w_hazard + w_vuln + w_coping
    wh, wv, wc = w_hazard/total, w_vuln/total, w_coping/total
    raw = wh * df["hazard"] + wv * df["vulnerability"] + wc * df["coping_lack"]
    mn, mx = raw.min(), raw.max()
    df["risk_score"] = ((raw - mn) / (mx - mn + 1e-9) * 10).round(2)
    bins   = [0, 2, 4, 6, 8, 10]
    labels = ["Very Low", "Low", "Medium", "High", "Very High"]
    df["risk_tier"] = pd.cut(df["risk_score"], bins=bins, labels=labels, include_lowest=True).astype(str)
    return df

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/risk")
def get_risk(
    w_hazard: float = Query(default=0.40, ge=0.0, le=1.0),
    w_vuln:   float = Query(default=0.35, ge=0.0, le=1.0),
    w_coping: float = Query(default=0.25, ge=0.0, le=1.0),
):
    result = compute_risk(gdf, w_hazard, w_vuln, w_coping)
    return json.loads(result.to_json())

@app.get("/country/{iso3}")
def get_country(iso3: str):
    row = gdf[gdf["iso3"] == iso3.upper()]
    if row.empty:
        return {"error": f"Country {iso3} not found"}
    r = row.iloc[0]
    return {
        "iso3": r["iso3"],
        "country": r["country"],
        "risk_score": r["risk_score"],
        "risk_tier": r["risk_tier"],
        "components": {
            "hazard": r["hazard"],
            "vulnerability": r["vulnerability"],
            "coping_lack": r["coping_lack"],
        },
        "population": r.get("population"),
        "gdp_per_capita": r.get("gdp_per_capita"),
    }
