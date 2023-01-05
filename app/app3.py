import numpy as np
import pandas as pd
import json
from datetime import datetime
from scipy.interpolate import UnivariateSpline
import pickle
import os

import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta

from navbar import Navbar
nav = Navbar()

with open("df.pkl", "rb") as f:
    datasets = pickle.load(f)

countries = list(datasets.keys())
n_vaccines = {}
for country in countries:
    if len(datasets[country]):
        nv = datasets[country].iloc[-1,1]
        if nv >= 2:
            n_vaccines[country] = nv

countries = sorted(n_vaccines.items(), key=lambda x:x[1], reverse=True)
countries = [x[0] for x in countries]

last_date = datasets[countries[0]].index[-1]
last_date = datetime.strptime(last_date,"%Y-%m-%d").date()

body = html.Div([
html.Div([
    html.Div([
        dcc.Graph(id='app2_graph', figure=go.Figure(),
            style={'width': '98%'}),
        dcc.Markdown('''
        * X-axis: percentage of people vaccinated.
        * Y-axis: number of difference between deaths (per million) end date and start date (i.e.: positive values indicate that the number of deaths increased).
        * Trendline plotted using Ordinary Least Squares.
        * Contries with less than 1 million inhabitants were not included in the analysis.

        **Source:**
        * https://github.com/owid/covid-19-data/tree/master/public/data
        ''',

        style={'flex-grow': 1, 'margin': '-1px 50px 10px 20px'})
        ],
        style={'flex-grow': 1}
    ),
    html.Div([

        dcc.Markdown('''
        ## Days to consider deaths (will plot the difference of deaths between these days):
        ''', style={'margin-top': '15px'}),
        dcc.DatePickerRange(
            id='app_2_death_dates',
            min_date_allowed=date(2021, 4, 1),
            max_date_allowed=last_date,
            start_date=last_date-timedelta(14),
            end_date=last_date,
        ),

        dcc.Markdown('''
        ## Day to consider percentage of vaccinated:
        ''', style={'margin-top': '50px'}),
        dcc.DatePickerSingle(
            id='app_2_vacc_date',
            min_date_allowed=date(2021, 4, 1),
            max_date_allowed=last_date,
            date=last_date-timedelta(21),
        ),

    ],
    style={'min-width': '350px', 'max-width': '500px'}
    ),
],
style={'display': 'flex'}
),
])

def App2():
    layout = html.Div([
    nav,
    body
    ])
    return layout

def register_callbacks2(app):
    @app.callback(
        Output(component_id='app2_graph', component_property='figure'),
        [
           Input('app_2_vacc_date', 'date'),

           Input('app_2_death_dates', 'start_date'),
           Input('app_2_death_dates', 'end_date'),
        ]
    )
    def callbackf(vac_date, start_date, end_date):
        fig = go.Figure(data=go.Choropleth(
            locations = df['CODE'],
            z = df['GDP (BILLIONS)'],
            text = df['COUNTRY'],
            colorscale = 'Blues',
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '$',
            colorbar_title = 'GDP<br>Billions US$',
        ))

        fig.update_layout(
            title_text='2014 Global GDP',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
        )

        fig.show()
