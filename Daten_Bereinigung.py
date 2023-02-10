import pandas as pd
import geopy
import geopy.geocoders as geo
from geopy.extra.rate_limiter import RateLimiter
import time



# Einlesen der Daten
df = pd.read_csv(r'output\appartements_bereinigt.csv', delimiter=',', parse_dates=True)


# Bereinigung/Umwandlung der neu gescrapten und ergänzten Daten
unbereinigt = df['clean'].isna()
df.loc[unbereinigt, 'Zimmeranzahl'] = df['Zimmeranzahl'].str.extract('(\d.?\d?)', expand=False)
df.loc[unbereinigt, 'Zimmeranzahl'] = df['Zimmeranzahl'].str.replace(",", ".")
df['Zimmeranzahl'] = df['Zimmeranzahl'].astype(float).fillna(0)
df.loc[unbereinigt, 'Wohnungsgrösse_m2'] = df['Wohnungsgrösse_m2'].str.extract('(\d*)', expand=False)
df['Wohnungsgrösse_m2'] = pd.to_numeric(df['Wohnungsgrösse_m2'], errors='coerce').astype('Int64').fillna(0)
df.loc[unbereinigt, 'Verkaufspreis'] = df['Verkaufspreis'].str.extract('(\d+\s\d*\s?\d*)', expand=False)
df.loc[unbereinigt, 'Verkaufspreis'] = df['Verkaufspreis'].str.replace(" ", "")
df['Verkaufspreis'] = pd.to_numeric(df['Verkaufspreis'], errors='coerce').astype('Int64').fillna(0)
df.loc[unbereinigt, 'Wohnungsart'] = df['Wohnungsart'].fillna('unbekannt')
df.loc[unbereinigt, 'Kanton'] = df['Wohnungs_Adresse'].str[-2:]
df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce').dt.normalize()
drop_art_index = df[df['Wohnungsart'] == 'Wohnungsart'].index
df.drop(drop_art_index, inplace=True)
drop_index = df[df['Zimmeranzahl'] > 11].index
df.drop(drop_index, inplace=True)
df.loc[unbereinigt, 'clean'] = 'clean'


# Ergänzen von Location-Daten (Long/Lat) aufgrund der Adresse
geolocator = geo.Nominatim(user_agent='Daten_Bereinigung')
geo.options.default_timeout = 10
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2)


# Schaut, welche Zeilen noch keine Langitude & Longitude haben und dann werden nur für diese die Lat & Lon generiert
start = time.time()
missing = df['Latitude'].isna() & df['Longitude'].isna()
locations = df.loc[missing, 'Wohnungs_Adresse'].apply(geolocator.geocode, timeout=30)
df.loc[missing, 'Latitude'] = locations.apply(lambda location: location.latitude if location else 'unbekant')
df.loc[missing, 'Longitude'] = locations.apply(lambda location: location.longitude if location else 'unbekannt')
ende = time.time()
print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print(f' Gebrauchte Zeit für Longitude/Latitude Generierung: \n ** {ende - start} Sekunden **')


# Schreibt die bereinigten und neu generierten Daten wieder in die CSV-Datei
df.to_csv(r'output\appartements_bereinigt.csv', sep=',', index=False)
# df.to_csv(r'output_clean\appartements_bereinigt_clean_lat_long.csv', sep=',', index=False)

"""
# Alter Code
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
