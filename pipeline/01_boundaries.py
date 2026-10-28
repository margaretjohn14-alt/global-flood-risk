"""
Script 01 — Country boundaries
Downloads Natural Earth 110m country shapefile and saves to data/raw/countries.gpkg
"""
import geopandas as gpd
import requests, zipfile, io, os

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

print("Downloading Natural Earth boundaries...")
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
r = requests.get(url, timeout=30)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall("data/raw/ne_110m")

gdf = gpd.read_file("data/raw/ne_110m/ne_110m_admin_0_countries.shp")
gdf = gdf[["NAME", "ISO_A3", "SUBREGION", "geometry"]].copy()
gdf.columns = ["country", "iso3", "subregion", "geometry"]
gdf = gdf[gdf["iso3"] != "-99"].copy()
gdf = gdf.to_crs(epsg=4326)
gdf.to_file("data/raw/countries.gpkg", driver="GPKG")
print(f"Saved {len(gdf)} countries to data/raw/countries.gpkg")
