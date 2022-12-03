import pandas as pd
import plotly.express as px
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import datetime
from datetime import date
from dash import dash_table
import plotly.graph_objects as go
import numpy as np

app = dash.Dash(__name__)
# für Heroku-Server ist die untenstehende Zeile notwendig
server = app.server

df = pd.read_csv(r'output\appartements_bereinigt.csv', delimiter=',', parse_dates=True)
df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce').dt.normalize()
df['Jahr'] = df['Datum'].dt.year
df['Monat'] = df['Datum'].dt.month



app.layout = html.Div(children=[

    html.H1("Verkaufsangebote Wohnungsmarkt Schweiz"),

    html.H2(children=["Zahlen und Fakten zu den Wohnungsverkaufsangeboten ", str(df['Jahr'].min()),  " bis " , str(df['Jahr'].max()) ]),


    html.Div(id='header_div',

        children=[
    html.Div([html.H3('Wohnungsart'),
                dcc.Dropdown(id='Wohnungsart',
                 options=[
                     # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                     {"label": art} for art in df.Wohnungsart
                 ],
                 multi=True,
                 value='Neubau')]),


    html.Div([html.H3('Auswertungs-Zeitraum'),
              dcc.DatePickerRange(id='Datum',
                         min_date_allowed=df['Datum'].min(),
                         max_date_allowed=df['Datum'].max(),
                         initial_visible_month=[df['Datum'].min(), df['Datum'].max()],
                         end_date=df['Datum'].max(),
                        )]),


    html.Div([html.H3('Anzahl Zimmer'),
                dcc.Dropdown(id='Zimmer_Anzahl',
                 options=[
                     # die Labels könnte man auch über eine Funktion als Liste automatisch generieren
                     {"label": f'{zimmer} Zimmer'} for zimmer in df.Zimmeranzahl
                 ],
                 multi=True,
                 optionHeight=50,
                 clearable=False)]),
    ]),


    html.Div(id='content_div',children=[
        dcc.Graph(id='scatter_geo', figure={}),
        dcc.Graph(id='barchart', figure={}),
        dcc.Graph(id='small_multiples', figure={}, style={'overflowY': 'scroll', 'height': 400}),
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
       children=[html.P('Dashboard Immo| © D. Hubatka')])
])



@app.callback(
    [Output(component_id='scatter_geo', component_property='figure'),
     Output(component_id='barchart', component_property='figure'),
     Output(component_id='small_multiples', component_property='figure')],

    dash.dependencies.Output('table_chart','data'),

    [Input(component_id='Wohnungsart', component_property='value'),
     Input(component_id='Datum', component_property='value'),
     Input(component_id='Zimmer_Anzahl', component_property='value')]
)


def update_graph(option_slctd_wohnungsart, option_slctd_date, option_slctd_zimmer):
    dff = df.copy()
    dff = dff[dff["Wohnungsart"] == option_slctd_wohnungsart]
    dff = dff[(dff["Datum"] >= option_slctd_date[0]) & (dff["Datum"] <= option_slctd_date[1])]
    dff = dff[dff['Jahr'] == option_slctd_zimmer]
    data = dff.to_dict('records')


    # Plotly Express

    # Barchart Earthquake per Year
    fig2 = px.bar(dff, x="Jahr",
                  y="number",
                  color='mag',
                  hover_name="type",
                  hover_data={'Jahr': True, 'mag': True, "place": True, 'number': False},
                  template='plotly_dark',
                  color_continuous_scale="solar",
                  # plasma, Bluered_r, aggrnyl, brwnyl, deep, thermal, orrd, redor, gray, temps, reds, ylorrd
                  labels={
                      "number": "Anzahl",
                      "mag": "Magnitude",
                      "Jahr": "Jahr"}, )

    fig2.update_layout(
        title='Anzahl der ' + '"' + str(option_slctd_wohnungsart).capitalize() + 's"' + ' pro Jahr von ' + str(
            option_slctd_date[0]) + ' bis ' + str(option_slctd_date[1]),
        font=dict(size=9)

    )

    # Earthquake-Map
    fig1 = px.scatter_geo(dff, lat='latitude', lon='longitude',
                          scope='usa',
                          hover_data=['Jahr', 'place'],
                          opacity=0.5, projection='albers usa',
                          template='plotly_dark',
                          color_continuous_scale="solar",
                          # plasma, Bluered_r, aggrnyl, brwnyl, deep, thermal, orrd, redor, gray, temps, reds, ylorrd
                          color='mag',
                          size="mag",
                          labels={"mag": "Magnitude"})

    fig1.update_layout(
        title='"' + str(option_slctd_wohnungsart).capitalize() + ' in der Schweiz (Karte) von ' + str(option_slctd_date[0]) + ' bis ' + str(option_slctd_date[1]),
        geo_scope='usa',
        font=dict(size=9)
    )

    data1 = []

    years = dff['Jahr'].unique()
    if len(years) < 4:
        set_height = 400
    else:
        if len(years) % 4 == 0:
            set_height = len(years) * 100
        else:
            set_height = (len(years) + (4 - (len(years) % 4))) * 100


    layout = dict(
        title='"' + str(option_slctd_wohnungsart).capitalize() + ' in der Jahresentwicklung auf der Karte der Schweiz von ' + str(option_slctd_date[0]) + ' bis ' + str(option_slctd_date[1]),
        # showlegend = False,
        autosize=False,
        height=set_height,
        hovermode=False,
        template='plotly_dark',
        font=dict(size=9),
        legend=dict(
            x=0.7,
            y=-0.1,
            bgcolor="rgba(255, 255, 255, 0)",
            font=dict(size=10),
        )
    )


    for i in range(len(years)):
        geo_key = 'geo' + str(i + 1) if i != 0 else 'geo'
        lons = list(dff[dff['Jahr'] == years[i]]['longitude'])
        lats = list(dff[dff['Jahr'] == years[i]]['latitude'])
        data1.append(
            dict(
                type='scattergeo',
                showlegend=False,
                lon=lons,
                lat=lats,
                geo=geo_key,
                name=int(years[i]),
                marker=dict(
                    color="#BB2020",
                    opacity=0.5
                )
            )
        )
        # Year markers
        data1.append(
            dict(
                type='scattergeo',
                showlegend=False,
                lon=[-78],
                lat=[47],
                geo=geo_key,
                text=[years[i]],
                mode='text',
            )
        )
        layout[geo_key] = dict(
            scope='usa',
            showland=True,
            #landcolor='rgb(229, 229, 229)',
            showcountries=False,
            domain=dict(x=[], y=[]),
            #subunitcolor="rgb(255, 255, 255)",

        )

    z = 0
    COLS = 4
    ROWS = int(np.ceil(len(years) / COLS))
    for y in reversed(range(ROWS)):
        for x in range(COLS):
            geo_key = 'geo' + str(z + 1) if z != 0 else 'geo'
            layout[geo_key]['domain']['x'] = [float(x) / float(COLS), float(x + 1) / float(COLS)]
            layout[geo_key]['domain']['y'] = [float(y) / float(ROWS), float(y + 1) / float(ROWS)]
            z = z + 1
            if z > len(years)-1:
                break

    fig5 = go.Figure(data=data1, layout=layout)
    #fig5.update_layout(height = 2000)

    return fig1, fig2, fig5, data


if __name__ == '__main__':
    app.title = "Entwicklung Verkaufsangebote für Wohnungen in der Schweiz"
    app.run_server(debug=True)
