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
        password="Xxxxxxx",   # hier dein PW eingeben
        database="database_homes"
    )

    query = "SELECT * FROM homes"
    df = pd.read_sql(query, db_connection)
    db_connection.close()
    return df

df = fetch_data()


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
              # Hinzufügen eines Buttons für alle auswählen oder abwählen
              html.Button('Alle auswählen', className='button5', id='select-all', n_clicks=0),
              html.Button('Alle abwählen', className='button5', id='deselect-all', n_clicks=0),

              # Die Checklist-Komponente für die Kantone
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
             ]),

    dcc.Loading(id="loading", type="default", children=[
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
    ]),

    html.Div(id='footer',
       children=[html.P('Dashboard Immo | © darhubat')])
])


# Callback für "Alle auswählen" und "Alle abwählen"
@app.callback(
    Output('Kanton', 'value'),
    [Input('select-all', 'n_clicks'),
     Input('deselect-all', 'n_clicks')],
    [dash.dependencies.State('Kanton', 'options'),
     dash.dependencies.State('Kanton', 'value')]
)
def select_deselect_all(select_all_clicks, deselect_all_clicks, kanton_options, current_value):
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_value  # Keine Änderung, wenn keine Schaltfläche geklickt wurde
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'select-all':
            # Alle Kantonswerte auswählen
            return [kant['value'] for kant in kanton_options]
        elif button_id == 'deselect-all':
            # Alle Kantonswerte abwählen
            return []

    return current_value  # Standardmäßig keine Änderung, falls keine Trigger aktiv sind


@app.callback(
    [Output(component_id='scatter_geo', component_property='figure'),
     Output(component_id='scatter_3D', component_property='figure'),],
     dash.dependencies.Output('table_chart','data'),

    [Input(component_id='Wohnungsart', component_property='value'),
     Input(component_id='Kanton', component_property='value'),
     # Input(component_id='Datum', component_property='start_date'),
     # Input(component_id='Datum', component_property='end_date'),
     Input(component_id='ZimmerAnzahl', component_property='value')]
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
    dff = dff[dff.ZimmerAnzahl.isin(option_slctd_zimmer)]
    data = dff.to_dict('records')


    # Plotly Express

    #
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
                projection_scale=10),
        )

    return fig_1, fig_2, data


if __name__ == '__main__':
    app.title = "Entwicklung der Verkaufsangebote für Wohnungen in der Schweiz"
    app.run_server(debug=True, port=8050)
