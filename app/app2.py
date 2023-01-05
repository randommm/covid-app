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

last_date = main_df[main_df.location == countries[0]].date.iloc[-1]
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
        * You can click on points on the plot to remove them.

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
        ''', style={'margin-top': '15px'}),
        dcc.DatePickerSingle(
            id='app_2_vacc_date',
            min_date_allowed=date(2021, 4, 1),
            max_date_allowed=last_date,
            date=last_date-timedelta(21),
        ),

        dcc.Markdown('''
        ## Countries:
        ''', style={'margin-top': '15px'}),
        html.Div(children=[
        html.Button('Select all', id='app_2_sel_all', n_clicks=0),
        html.Button('Select all large population states', id='app_2_sel_all_large', n_clicks=0, style={'margin-left': '7px'}),
        ], style={'margin-bottom': '7px'}),
        html.Div(children=[
        dcc.Checklist(
            id='app2_countries',
            options=[
                {'label': k, 'value': k} for k in countries
            ],
            value=countries_large,
            labelStyle={'display': 'block'}
        ),
        ], style={
        '-webkit-column-count': '5',
        '-moz-column-count': '5',
        'column-count': '5',
        }, id='app1_country_div'),
    ],
    style={'min-width': '550px', 'max-width': '600px'}
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
        Output('app2_countries', 'value'),
        [
            Input('app_2_sel_all', 'n_clicks'),
            Input('app_2_sel_all_large', 'n_clicks'),
            Input('app2_graph', 'clickData'),
        ],
        State('app2_countries', 'value'),
    )
    def callbackf(n1, n2, cdata, cur_val):
        changed_id = [p['prop_id'] for p in
           dash.callback_context.triggered][0]
        if 'app_2_sel_all.n_clicks' in changed_id:
            return countries
        elif 'app_2_sel_all_large.n_clicks' in changed_id:
            return countries_large
        elif 'app2_graph.clickData' in changed_id:
            ecountries = [c['text'] for c in cdata['points']]
            return [c for c in cur_val if c not in ecountries]
        else:
            return cur_val

    @app.callback(
        Output(component_id='app2_graph', component_property='figure'),
        [
            Input('app_2_vacc_date', 'date'),
            Input('app_2_death_dates', 'start_date'),
            Input('app_2_death_dates', 'end_date'),
            Input('app2_countries', 'value'),
        ]
    )
    def callbackf(vac_date, start_date, end_date, countries):
        fig = go.Figure()
        if not vac_date or not start_date or not end_date:
            print("empty fig")
            return fig

        #end_date = datetime.strptime(end_date,"%Y-%m-%d").date()
        #end_date = str(end_date+timedelta(1))
        def diff_deaths(country, end_date, start_date):
            df = main_df[main_df.location==country].set_index('date')
            diff = df.loc[end_date].deaths.item()
            diff = diff - df.loc[start_date].deaths.item()
            return diff
        deaths = [
            diff_deaths(country, end_date, start_date)
            for country in countries
        ]

        vaccines = [
            main_df[main_df.location==country].set_index('date').loc[
                vac_date
            ].fvaccines.item()
            for country in countries
        ]

        fig = px.scatter(
            x=vaccines, y=deaths, opacity=0.65,
            trendline='ols', trendline_color_override='darkblue',
            text=countries,
        )
        fig.update_traces(hovertemplate=
            'vacc: %{x}<br>diff deaths: %{y}<br>country: %{text}<extra></extra>',
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
