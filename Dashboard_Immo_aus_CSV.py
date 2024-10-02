import pandas as pd
import plotly.express as px
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from dash import dash_table
import datetime as dt


app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
# für Heroku-Server ist die untenstehende Zeile notwendig
server = app.server


df = pd.read_csv(r'output\\appartements_bereinigt.csv', delimiter=',', parse_dates=True)
# Datenbereinigung Schritt 1
df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce').dt.normalize()
df['Verkaufspreis'] = pd.to_numeric(df['Verkaufspreis'], errors='coerce').astype('Int64').fillna(0.0)
del df['Latitude/Longitude']
# df.rename(columns = {'Latitude/Longitude': 'Koordinaten'}, inplace = True)
# df[['latitude', 'longitude']] = df['Koordinaten'].str.extract(pat = '(-?\d+\.\d+),\s*(-?\d+\.\d+)')
# df['Jahr'] = df['Datum'].dt.year
# df['Monat'] = df['Datum'].dt.month


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
                    value=['Neubau', 'Neubauprojekt', 'unbekannt'])]),

    html.Div([html.H3('Begrenzung auf Kanton'),
                dcc.Checklist(id='Kanton',
                    options=[
                    # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                    {"label": kant, "value": kant} for kant in sorted(df.Kanton.unique())],
                    inline=True,
                    style={"padding": "10px", "max-width": "800px", "margin": "auto"},
                    value=[kant for kant in df.Kanton.unique()], )]),

    html.Div([html.H3('Anzahl-Zimmer'),
                dcc.Dropdown(id='Zimmer_Anzahl',
                 options=[
                     # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                     {"label": zimmer, "value": zimmer} for zimmer in sorted(df.Zimmeranzahl.unique())
                 ],
                 multi=True,
                 optionHeight=50,
                 value=[2.5, 3.5],)]),
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
            {'name': 'Standort', 'id': 'Wohnungs_Adresse', 'type': 'text'},
            {'name': 'Art der Wohnung', 'id': 'Wohnungsart', 'type': 'text'},
            {'name': 'Anz. Zimmer', 'id': 'Zimmeranzahl', 'type': 'numeric'},
            {'name': 'Verkaufspreis', 'id': 'Verkaufspreis', 'type': 'numeric'},
            {'name': 'Kanton', 'id': 'Kanton', 'type': 'text'},
            {'name': 'Erschienen', 'id': 'Datum', 'type': 'datetime'},
        ],
        page_size=9,
        editable=True,
        ),
        ]),

    html.Div(id='footer',
       children=[html.P('Dashboard Immo | © D. Hubatka')])
])


@app.callback(
    [Output(component_id='scatter_geo', component_property='figure'),
     Output(component_id='scatter_3D', component_property='figure'),],
     dash.dependencies.Output('table_chart','data'),

    [Input(component_id='Wohnungsart', component_property='value'),
     Input(component_id='Kanton', component_property='value'),
     # Input(component_id='Datum', component_property='start_date'),
     # Input(component_id='Datum', component_property='end_date'),
     Input(component_id='Zimmer_Anzahl', component_property='value')]
)


def update_graph(option_slctd_wohnungsart, option_slctd_kanton, option_slctd_zimmer):
    dff = df.copy()
    # if bool(option_slctd_wohnungsart):
    dff = dff[dff.Wohnungsart.isin(option_slctd_wohnungsart)]
    dff = dff[dff.Kanton.isin(option_slctd_kanton)]
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    dff = dff[dff.datum.between(
        dt.datetime.strftime(start_date, "%Y-%m-%d"),
        dt.datetime.strftime(end_date, "%Y-%m-%d")
    )]
    """
    # if bool(option_slctd_zimmer):
    dff = dff[dff.Zimmeranzahl.isin(option_slctd_zimmer)]
    data = dff.to_dict('records')


    # Plotly Express

    #
    fig_2 = px.scatter_3d(dff, x='Zimmeranzahl', y='Wohnungsgrösse_m2', z='Verkaufspreis',
                          color='Verkaufspreis', size='Wohnungsgrösse_m2', opacity=0.4, size_max=12, color_continuous_scale='solar',
                          hover_data=['Wohnungs_Adresse', 'Wohnungsart', 'Wohnungsgrösse_m2', 'Zimmeranzahl', 'Verkaufspreis'])

    fig_2.update_layout(
            title='3D Scatterplot der Wohnungs-Verkaufspreise in der Schweiz',
            font=dict(size=8),
            template='plotly_dark',
    )

    # Map
    fig_1 = px.scatter_geo(dff, lat='Latitude', lon='Longitude',
                          geojson='geometry',
                          scope='europe',
                          hover_data=['Wohnungs_Adresse', 'Wohnungsart', 'Wohnungsgrösse_m2', 'Zimmeranzahl', 'Verkaufspreis'],
                          opacity=0.4, projection='orthographic',
                          color_continuous_scale="solar",
                          # plasma, Bluered_r, aggrnyl, brwnyl, deep, thermal, orrd, redor, gray, temps, reds, ylorrd
                          color='Verkaufspreis',
                          size="Wohnungsgrösse_m2",
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
                projection_scale=10),
        )

    return fig_1, fig_2, data


if __name__ == '__main__':
    app.title = "Entwicklung Verkaufsangebote für Wohnungen in der Schweiz"
    app.run_server(debug=True, port=8050)
