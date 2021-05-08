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
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta

from navbar import Navbar
nav = Navbar()

counter = [0]

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
        * Number of people vaccinated (per hundred) against average number of deaths per day (per million).

        **Source:**
        * https://github.com/owid/covid-19-data/tree/master/public/data
        ''',

        style={'flex-grow': 1, 'margin': '-1px 50px 10px 20px'})
        ],
        style={'flex-grow': 1}
    ),
    html.Div([

        dcc.Markdown('''
        ## Days to consider deaths (averaged among days):
        ''', style={'margin-top': '15px'}),
        dcc.DatePickerRange(
            id='app_2_death_dates',
            min_date_allowed=date(2021, 4, 1),
            max_date_allowed=last_date,
            start_date=last_date-timedelta(7),
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
    style={'min-width': '250px', 'max-width': '500px'}
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
        counter[0] += 1
        print(counter[0])

        fig = go.Figure()
        if not vac_date or not start_date or not end_date:
            print("empty fig")
            return fig

        end_date = datetime.strptime(end_date,"%Y-%m-%d").date()
        end_date = str(end_date+timedelta(1))
        deaths = [
            datasets[country].loc[
                start_date:end_date
            ].deaths.mean()
            for country in countries
        ]

        vaccines = [
            datasets[country].loc[
                vac_date
            ].vaccines.item()
            for country in countries
        ]

        fig = px.scatter(
            x=vaccines, y=deaths, opacity=0.65,
            trendline='ols', trendline_color_override='darkblue',
            text=countries,
        )
        fig.update_traces(hovertemplate=
            'vacc: %{x}<br>deaths: %{y}<br>country: %{text}<extra></extra>',
            selector={'mode': 'markers+text'}
        )
        fig.update_traces(mode="markers", selector={'mode': 'markers+text'})

        fig.update_layout(
            autosize=True,
            #width=1000,
            height=600,
            margin=dict(
                l=50,
                r=50,
                b=100,
                t=100,
                pad=4
            ),
            legend_orientation="h",
            legend=dict(y=1.1),
            xaxis_title="Vaccine (%)",
            yaxis_title="Deaths (per million)",

            #trendline='ols',
            #trendline_color_override='darkblue'
            #yaxis_tickformat = '%',
            #yaxis_showexponent = 'all',
            #yaxis_exponentformat = 'power',
        )

        return fig
