"""
Script 03 — World Bank indicators
"""
import requests, time, pandas as pd, numpy as np, os

os.makedirs("data/processed", exist_ok=True)

INDICATORS = {
    "gdp_per_capita":     "NY.GDP.PCAP.CD",
    "gini":               "SI.POV.GINI",
    "hospital_beds":      "SH.MED.BEDS.ZS",
    "health_expenditure": "SH.XPD.CHEX.GD.ZS",
    "population":         "SP.POP.TOTL",
    "urban_pct":          "SP.URB.TOTL.IN.ZS",
}

def fetch(indicator_code, retries=3):
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
           f"?format=json&per_page=1000&mrv=5")
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=60)  # increased to 60s
            data = r.json()
            if len(data) < 2:
                return pd.DataFrame()
            rows = []
            for item in data[1]:
                if item["value"] is not None and len(item["countryiso3code"]) == 3:
                    rows.append({"iso3": item["countryiso3code"], "value": item["value"]})
            return pd.DataFrame(rows).drop_duplicates("iso3")
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    print(f"  Skipping {indicator_code} after {retries} failures")
    return pd.DataFrame(columns=["iso3", "value"])

frames = {}
for name, code in INDICATORS.items():
    print(f"Fetching {name}...")
    frames[name] = fetch(code).rename(columns={"value": name})
    time.sleep(1)

df = frames["population"]
for name, frame in frames.items():
    if name != "population":
        df = df.merge(frame, on="iso3", how="left")

def norm(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-9)

df["vuln_gdp"]         = 1 - norm(pd.to_numeric(df["gdp_per_capita"], errors="coerce"))
df["vuln_gini"]        = norm(pd.to_numeric(df["gini"], errors="coerce"))
df["coping_beds"]      = norm(pd.to_numeric(df["hospital_beds"], errors="coerce"))
df["coping_health"]    = norm(pd.to_numeric(df["health_expenditure"], errors="coerce"))

df["wb_vulnerability"] = df["vuln_gdp"].fillna(0.5) * 0.6 + df["vuln_gini"].fillna(0.5) * 0.4
df["wb_coping"]        = df["coping_beds"].fillna(0.5) * 0.5 + df["coping_health"].fillna(0.5) * 0.5

df.to_csv("data/processed/worldbank.csv", index=False)
print(f"Saved {len(df)} rows to data/processed/worldbank.csv")
