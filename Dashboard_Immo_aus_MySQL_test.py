import pandas as pd
import plotly.express as px
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from dash import dash_table
import mysql.connector
import datetime as dt


app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
# für Heroku-Server ist die untenstehende Zeile notwendig
server = app.server


# Daten für das Dashboard werden direkt aus einer MySQL-Datenbank abgerufen
def fetch_data():
    db_connection = mysql.connector.connect(
        host="localhost",
        user="Dario",
        password="Fopalu22!",   # hier dein PW eingeben
        database="database_homes"
    )

    query = "SELECT * FROM homes"
    df = pd.read_sql(query, db_connection)
    db_connection.close()
    return df

df = fetch_data()

# Datum in Monat und Jahr konvertieren für RangeSlider-Filter
df['JahrMonat'] = pd.to_datetime(df['Datum']).dt.to_period('M').astype(str)

# Erstellen einer Liste mit eindeutigen Jahren und Monaten für den RangeSlider-Filter
min_date = df['Datum'].min()
max_date = df['Datum'].max()


app.layout = html.Div(children=[

    html.H1("Verkaufsangebote Wohnungsmarkt Schweiz"),

    html.H2(children=["Zahlen und Fakten zu den Online Verkaufsangebote für Wohnungen"]),


    html.Div(id='header_div',

        children=[
    html.Div([html.H3('Wohnungsart'),
                dcc.Dropdown(id='Wohnungsart',
                 options=[
                     # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                     {"label": art, "value": art} for art in df.Wohnungsart.unique()],
                    multi=True,
                    value=[art for art in df.Wohnungsart.unique()], )]),

    html.Div([html.H3('Begrenzung auf Kanton'),
                dcc.Checklist(id='Kanton',
                    options=[
                    # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                    {"label": kant, "value": kant} for kant in sorted(df.Kanton.unique())],
                    inline=True,
                    style={"padding": "10px", "max-width": "800px", "margin": "auto"},
                    value=[kant for kant in df.Kanton.unique()], )]),

    html.Div([html.H3('Anzahl-Zimmer'),
                dcc.Dropdown(id='ZimmerAnzahl',
                 options=[
                     # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                     {"label": zimmer, "value": zimmer} for zimmer in sorted(df.ZimmerAnzahl.unique())
                 ],
                 multi=True,
                 optionHeight=50,
                 value=[2.5, 3.5],)]),

        # RangeSlider-Filter, nur auf Monats- und Jahresbasis
            html.Div([html.H3('Zeitraum wählen (Monat/Jahr)', style={'color': 'white'}),
                      dcc.RangeSlider(id='date_range_slider',
                                      min=0,
                                      max=len(pd.date_range(min_date, max_date, freq='M')) - 1,
                                      marks={i: {'label': (min_date + pd.DateOffset(months=i)).strftime('%m/%Y'),
                                                 'style': {'color': 'white'}} for i in
                                             range(len(pd.date_range(min_date, max_date, freq='M')))},
                                      step=1,
                                      value=[0, len(pd.date_range(min_date, max_date, freq='M')) - 1],
                                      tooltip={"placement": "bottom", "always_visible": True}
                )
                      ]),
             ]),


    html.Div(id='content_div', children=[
        dcc.Graph(id='scatter_geo', figure={}),
        dcc.Graph(id='scatter_3D', figure={}),
        dash_table.DataTable(
        id="table_chart",
        data=df.to_dict('records'),
        sort_action='native',
        filter_action="native",
        columns=[
            {'name': 'Standort', 'id': 'WohnungsAdresse', 'type': 'text'},
            {'name': 'Art der Wohnung', 'id': 'Wohnungsart', 'type': 'text'},
            {'name': 'Anz. Zimmer', 'id': 'ZimmerAnzahl', 'type': 'numeric'},
            {'name': 'Verkaufspreis', 'id': 'Verkaufspreis', 'type': 'numeric'},
            {'name': 'Kanton', 'id': 'Kanton', 'type': 'text'},
            {'name': 'Erschienen', 'id': 'Datum', 'type': 'datetime'},
        ],
        page_size=9,
        editable=True,
        ),
        ]),

    html.Div(id='footer',
       children=[html.P('Dashboard Immo | © darhubat')])
])


@app.callback(
    [Output(component_id='scatter_geo', component_property='figure'),
     Output(component_id='scatter_3D', component_property='figure'),],
     dash.dependencies.Output('table_chart','data'),

    [Input(component_id='Wohnungsart', component_property='value'),
     Input(component_id='Kanton', component_property='value'),
     # Input(component_id='Datum', component_property='start_date'),
     # Input(component_id='Datum', component_property='end_date'),
     Input(component_id='ZimmerAnzahl', component_property='value'),
     Input(component_id='date_range_slider', component_property='value')]
)

def update_graph(option_slctd_wohnungsart, option_slctd_kanton, option_slctd_zimmer, date_range):
    dff = df.copy()
    # if bool(option_slctd_wohnungsart):
    dff = dff[dff.Wohnungsart.isin(option_slctd_wohnungsart)]
    dff = dff[dff.Kanton.isin(option_slctd_kanton)]
    # if bool(option_slctd_zimmer):
    dff = dff[dff.ZimmerAnzahl.isin(option_slctd_zimmer)]
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    dff = dff[dff.datum.between(
        dt.datetime.strftime(start_date, "%Y-%m-%d"),
        dt.datetime.strftime(end_date, "%Y-%m-%d")
    )]
    """
    # Filter nach Datum
    start_date = min_date + pd.DateOffset(months=date_range[0])
    end_date = min_date + pd.DateOffset(months=date_range[1])
    dff = dff[(dff['Datum'] >= start_date) & (dff['Datum'] <= end_date)]


    # Plotly Express Scatter-Grafik

    fig_2 = px.scatter_3d(dff, x='ZimmerAnzahl', y='Wohnungsgroesse_m2', z='Verkaufspreis',
                          color='Verkaufspreis', size='Wohnungsgroesse_m2', opacity=0.4, size_max=12, color_continuous_scale='solar',
                          hover_data=['WohnungsAdresse', 'Wohnungsart', 'Wohnungsgroesse_m2', 'ZimmerAnzahl', 'Verkaufspreis'])

    fig_2.update_layout(
            title='3D Scatterplot der Wohnungs-Verkaufspreise in der Schweiz',
            font=dict(size=8),
            template='plotly_dark',
    )

    # Map
    fig_1 = px.scatter_geo(dff, lat='Latitude', lon='Longitude',
                          geojson='geometry',
                          scope='europe',
                          hover_data=['WohnungsAdresse', 'Wohnungsart', 'Wohnungsgroesse_m2', 'ZimmerAnzahl', 'Verkaufspreis'],
                          opacity=0.4, projection='orthographic',
                          color_continuous_scale="solar",
                          # plasma, Bluered_r, aggrnyl, brwnyl, deep, thermal, orrd, redor, gray, temps, reds, ylorrd
                          color='Verkaufspreis',
                          size="Wohnungsgroesse_m2",
                          size_max=9,
                          center=dict(
                               lat=46.8131873,
                               lon=8.22421)
                           )

    fig_1.update_layout(
            title='Wohnungangebote in der Schweiz (Karte)',
            template='plotly_dark',
            font=dict(size=9),
            geo=dict(center=dict(
                lat=46.8131873,
                lon=8.22421),
                scope='europe',
                projection_scale=10))

    data = dff.to_dict('records')
    return fig_1, fig_2, data


if __name__ == '__main__':
    app.title = "Entwicklung der Verkaufsangebote für Wohnungen in der Schweiz"
    app.run_server(debug=True, port=8050)
