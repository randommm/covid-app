import numpy as np
import pandas as pd
import json
from datetime import datetime
from scipy.interpolate import UnivariateSpline
import pickle
import os

import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from navbar import Navbar
nav = Navbar()

with open("main_df.pkl", "rb") as f:
    main_df = pickle.load(f)

with open("df_vars.pkl", "rb") as f:
    df_vars = pickle.load(f)

countries = list(main_df.location.unique())
n_vaccines = {}
for country in countries:
    nv = main_df[main_df.location == country]
    nv = nv.iloc[-1].vaccines
    if nv >= 2:
        n_vaccines[country] = nv

countries = sorted(n_vaccines.items(), key=lambda x:x[1], reverse=True)
countries = [x[0] for x in countries]
countries_large = [
    c for c in countries
    if df_vars.loc[df_vars.location==c, 'population'].item()
    > 1_000_000
]

def smoother(series, N):
    res = pd.DataFrame(series).rolling(N,center=True).mean()
    res = res.iloc[N-1:,0]
    return res

body = html.Div([
html.Div([
    html.Div([
        dcc.Graph(id='app1_graph', figure=go.Figure(),
            style={'width': '98%'}),
        dcc.Markdown('''
        * Cumulative percentage of people vaccinated against smoothed number of deaths per day (per million).

        * Smoothing is done using [moving average](https://en.wikipedia.org/wiki/Moving_average).

        **Source:**
        * https://github.com/owid/covid-19-data/tree/master/public/data
        ''',

        style={'flex-grow': 1, 'margin': '-1px 50px 10px 20px'})
        ],
        style={'flex-grow': 1}
    ),
    html.Div([

        dcc.Markdown('''
        ## Smoothing:
        '''),
        dcc.Slider(
            min=1,
            max=15,
            step=2,
            value=7,
            id='app1_smoothf',
        ),

        dcc.Checklist(
            options=[
                {'label': 'Include low population contries', 'value': 'yes'},
            ],
            value=[],
            id='app1_smallstate',
        ),


        dcc.Markdown('''
        ## Country:
        '''),
        html.Div(children=[
        dcc.RadioItems(
            id='app1_country',
            options=[
                {'label': k, 'value': k} for k in countries
            ],
            value='Brazil',
            labelStyle={'display': 'block'}
        ),
        ], style={
        '-webkit-column-count': '5',
        '-moz-column-count': '5',
        'column-count': '5',
        }, id='app1_country_div'),

    ],
    style={'min-width': '250px', 'max-width': '500px'}
    ),
],
style={'display': 'flex'}
),
])

def App1():
    layout = html.Div([
    nav,
    body
    ])
    return layout

def register_callbacks1(app):
    @app.callback(
        Output('app1_country_div', 'children'),
        [
           Input('app1_smallstate', 'value'),
        ],
        State('app1_country', 'value'),
    )
    def callbackf(smallstate, cur_location):
        fig = go.Figure()

        if smallstate:
            countries_sel = countries
        else:
            countries_sel = countries_large

        return dcc.RadioItems(
            id='app1_country',
            options=[
                {'label': k, 'value': k} for k in countries_sel
            ],
            value=cur_location,
            labelStyle={'display': 'block'}
        )


    @app.callback(
        Output(component_id='app1_graph', component_property='figure'),
        [
           Input('app1_country', 'value'),
           Input('app1_smoothf', 'value'),
        ]
    )
    def callbackf(country, smoothf):
        fig = go.Figure()

        if not country or not smoothf:
            return fig

        df = main_df[main_df.location == country].copy()
        df.date = np.array([datetime.strptime(d,"%Y-%m-%d") for d in df.date])
        df.set_index('date')
        if smoothf > 1:
            smoothed = smoother(df.deaths, smoothf)
            df = df.loc[smoothed.index]
            df.deaths = smoothed
            add_text = ''
        else:
            add_text = ' [smoothed]'

        fig.add_trace(go.Scatter(x=df.date, y=df.deaths,
                    mode='lines+markers',
                    name='Death Covid'+add_text))

        fig.add_trace(go.Scatter(x=df.date, y=df.vaccines,
                    mode='lines+markers',
                    name='Prop vaccinated Covid'))

        fig.add_trace(go.Scatter(x=df.date, y=df.fvaccines,
                    mode='lines+markers',
                    name='Prop fully vaccinated Covid'))

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
            #yaxis_tickformat = '%',
            #yaxis_showexponent = 'all',
            #yaxis_exponentformat = 'power',
        )

        return fig
