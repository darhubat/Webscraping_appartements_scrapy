import pandas as pd
import geopy.geocoders as geo
from geopy.extra.rate_limiter import RateLimiter

# Bereinigung/Umwandlung der gescrapten Daten
df = pd.read_csv(r'output\appartements.csv', delimiter=',', parse_dates=True)
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


# Ergänzen von Location-Daten (Long/Lat) aufgrund der Adresse
geolocator = geo.Nominatim(user_agent='Daten_Bereinigung')
geo.options.default_timeout = 10
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def eval_results(x):
    try:
        return (x.latitude, x.longitude)
    except:
        return (None, None)
df['Latitude/Longitude'] = df['Wohnungs_Adresse'].apply(geolocator.geocode, timeout=100).apply(
    lambda x: eval_results(x))
df.to_csv(r'output\appartements_bereinigt.csv', sep=',', index=False)