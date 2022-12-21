import pandas as pd
import geopandas
import geopy
import geopy.geocoders as geo
from geopy.extra.rate_limiter import RateLimiter
import time
import glob
import os
import numpy as np

""""
# merging the files
files_joined = os.path.join('C:\\Users\\dhuab\\PycharmProjects\\Python_Kaufpreise_Immobilien\\output', "appartements*.csv")

# Return a list of all joined files
list_files = glob.glob(files_joined)

# Merge files by joining all files
dataframe = pd.concat(map(pd.read_csv, list_files), ignore_index=True)
print(dataframe)
"""

# Bereinigung/Umwandlung der neu gescrapten und ergänzten Daten
df = pd.read_csv(r'output\appartements_bereinigt.csv', delimiter=',', parse_dates=True)
anz = len(df)
for zeile in df[['clean']].iloc[:anz].iterrows():
    if str(zeile[1][0]) == 'clean':
        continue
    else:
        df['Zimmeranzahl'] = df['Zimmeranzahl'].str.extract('(\d.?\d?)', expand=True)
        df['Zimmeranzahl'] = df['Zimmeranzahl'].str.replace(",", ".")
        df['Wohnungsgrösse_m2'] = df['Wohnungsgrösse_m2'].str.extract('(\d*)', expand=True)
        df['Verkaufspreis'] = df['Verkaufspreis'].str.extract('(\d+\s\d*\s?\d*)', expand=True)
        df['Verkaufspreis'] = df['Verkaufspreis'].str.replace(" ", "").fillna(0)
        df['Wohnungsart'] = df['Wohnungsart'].fillna('unbekannt')
        df['Kanton'] = df['Wohnungs_Adresse'].str[-2:]
        df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce').dt.normalize()
        df['Zimmeranzahl'] = df['Zimmeranzahl'].astype(float).fillna(0)
        df['Wohnungsgrösse_m2'] = pd.to_numeric(df['Wohnungsgrösse_m2'], errors='coerce').astype('Int64').fillna(0)
        df['Verkaufspreis'] = pd.to_numeric(df['Verkaufspreis'], errors='coerce').astype('Int64').fillna(0)
        df.insert(loc=len(df.columns), column='clean', value='clean')


# Ergänzen von Location-Daten (Long/Lat) aufgrund der Adresse
geolocator = geo.Nominatim(user_agent='Daten_Bereinigung')
geo.options.default_timeout = 10
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2)

def eval_results(x):
    try:
        return (x.latitude, x.longitude)
    except:
        return (None, None)

# Die Schleife prüft, ob bereits Lat/Long vorhanden ist, falls nicht, werden diese generiert
anzahl_zeilen_df = len(df)
for row in df[['Latitude/Longitude']].iloc[:anzahl_zeilen_df].iterrows():
    if str(row[1][0]) != 'nan':
        continue
    else:
        df['Latitude/Longitude'] = df['Wohnungs_Adresse'].apply(geolocator.geocode, timeout=30).apply(
        lambda x: eval_results(x))
df.to_csv(r'output_clean\appartements_clean_lat_lon.csv', sep=',', index=False)


"""
df['Latitude/Longitude'] = df['Wohnungs_Adresse'].apply(geolocator.geocode, timeout=100).apply(
    lambda x: eval_results(x))
df.to_csv(r'output\appartements_bereinigt.csv', sep=',', index=False)
"""

"""
def divide (a, b):
    if str(a) != 'nan':
        return a
    else:
        b.apply(geolocator.geocode, timeout=30).apply(lambda x: eval_results(x))

df['Latitude/Longitude'] = np.vectorize(divide(df['Latitude/Longitude'], df['Wohnungs_Adresse']))
"""