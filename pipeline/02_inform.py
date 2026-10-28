"""
Script 02 — INFORM Risk Index 2026
"""
import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

print("Reading INFORM Risk Index...")
df = pd.read_excel(
    "data/raw/INFORM2024.xlsx",
    sheet_name="INFORM Risk 2026 (a-z)",
    header=1
)

# Drop the units row (row 0 has "(0-10)", "(a-z)" etc.)
df = df[df["ISO3"] != "(a-z)"].copy()

col_map = {
    "ISO3":                    "iso3",
    "COUNTRY":                 "country_inform",
    "INFORM RISK":             "inform_risk",
    "HAZARD & EXPOSURE":       "inform_hazard",
    "River Flood":             "inform_flood",
    "Tropical Cyclone":        "inform_cyclone",
    "Drought":                 "inform_drought",
    "Earthquake":              "inform_earthquake",
    "VULNERABILITY":           "inform_vulnerability",
    "Socio-Economic Vulnerability": "inform_vuln_socioeco",
    "Vulnerable Groups":       "inform_vuln_groups",
    "LACK OF COPING CAPACITY": "inform_coping_lack",
    "Institutional":           "inform_coping_institutional",
    "Infrastructure":          "inform_coping_infrastructure",
}

df = df.rename(columns=col_map)
keep = [v for v in col_map.values() if v in df.columns]
df = df[keep].dropna(subset=["iso3"])

# Normalise 0-10 scores to 0-1
score_cols = [c for c in keep if c not in ("iso3", "country_inform")]
for c in score_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")
    df[c + "_norm"] = df[c] / 10

df.to_csv("data/processed/inform.csv", index=False)
print(f"Saved {len(df)} rows to data/processed/inform.csv")
print(df[["iso3","inform_risk","inform_flood"]].head())
