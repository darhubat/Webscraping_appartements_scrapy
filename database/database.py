import mysql.connector
import pandas as pd


# MySQL-Datenbankverbindung einrichten
db_connection = mysql.connector.connect(
    host="localhost",  # z.B. "localhost"
    user="Dario",
    password="Xxxxxxxxx", #hier dein PW eingeben
    database="database_homes"
)


# CSV-Datei laden
csv_file = 'output\\appartements_bereinigt.csv'
data = pd.read_csv(csv_file, delimiter=',', parse_dates=True)
# Datenbereinigung Schritt 1
data['Datum'] = pd.to_datetime(data['Datum'], errors='coerce').dt.normalize()
data['Verkaufspreis'] = pd.to_numeric(data['Verkaufspreis'], errors='coerce').astype('Int64').fillna(0.0)
data['Zimmeranzahl'] = pd.to_numeric(data['Zimmeranzahl'], errors='coerce').astype('float').fillna(0.0)
data['Wohnungsrösse_m2'] = pd.to_numeric(data['Wohnungsgrösse_m2'], errors='coerce').astype('float').fillna(0.0)
data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce').astype('float').fillna(0.0)
data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce').astype('float').fillna(0.0)
del data['Latitude/Longitude']
filtered_data = data.query('clean == clean') # es werden nur die Werte in die MySQL-Tabelle geschrieben, bei denen die Koordinaten bereits generiert wurden


# Tabelle in MySQL erstellen, falls noch nicht vorhanden
create_table_query = """
CREATE TABLE IF NOT EXISTS homes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Datum DATETIME,
    Wohnungsart VARCHAR(255),
    ZimmerAnzahl FLOAT,
    Wohnungsgroesse_m2 FLOAT,
    Verkaufspreis INT,
    WohnungsAdresse TEXT,
    Kanton VARCHAR(2),
    Clean VARCHAR(5),
    Latitude FLOAT,
    Longitude FLOAT
); """

cursor = db_connection.cursor()
cursor.execute(create_table_query)

# Daten in die MySQL-Tabelle einfügen
for _, row in filtered_data.iterrows(): # _, Index wird damit ignoriert, da wir diesen nicht benötigen
    insert_query = """
    INSERT INTO homes (Datum, Wohnungsart, ZimmerAnzahl, Wohnungsgroesse_m2, Verkaufspreis, WohnungsAdresse, Kanton, 
    Clean, Latitude, Longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # %s sind nur ein Platzhalter für die späteren Werte
    cursor.execute(insert_query, (row['Datum'], row['Wohnungsart'], row['Zimmeranzahl'], row['Wohnungsgrösse_m2'], row['Verkaufspreis'],
                                  row['Wohnungs_Adresse'], row['Kanton'], row['clean'], row['Latitude'], row['Longitude']))

db_connection.commit()
cursor.close()
db_connection.close()


