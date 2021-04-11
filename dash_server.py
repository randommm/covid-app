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

def smoother(series, N):
    res = pd.DataFrame(series).rolling(N,center=True).mean()
    res = res.iloc[N-1:,0]
    return res

app = dash.Dash(meta_tags=[dict(name="viewport",content="width=1000px, initial-scale=1.0")])
app.title = 'Corona vacine data'
server = app.server

app.layout = html.Div([html.Div([
    html.Div([
        dcc.Graph(id='graph', figure=go.Figure(),
            style={'width': '98%'}),
        dcc.Markdown('''
        * Cumulative number of people vaccinated (per hundred) against smoothed number of deaths per day (per million)

        * Smoothing is done using [moving average](https://en.wikipedia.org/wiki/Moving_average).

        **Source:**
        * https://github.com/owid/covid-19-data/tree/master/public/data
        ''',

        style={'flex-grow': 1, 'margin': '-10px 30px 10px 20px'})
        ],
        style={'flex-grow': 1}
    ),
    html.Div([

        dcc.Markdown('''
        ## Country:
        '''),
        html.Div([
        dcc.RadioItems(
            id='country',
            options=[
                {'label': k, 'value': k} for k in countries
            ],
            value='Brazil',
            labelStyle={'display': 'block'}
        ),
        ], style={
        '-webkit-column-count': '3',
        '-moz-column-count': '3',
        'column-count': '3',
        }),

        dcc.Markdown('''
        ## Smoothing:
        '''),
        dcc.Slider(
            min=1,
            max=15,
            step=2,
            value=7,
            id='smoothf',
        ),
    ],
    style={'min-width': '250px', 'max-width': '500px'}
    ),
],
style={'display': 'flex'}
),])

@app.callback(
    Output(component_id='graph', component_property='figure'),
    [
       Input('country', 'value'),
       Input('smoothf', 'value'),
    ]
)
def callbackf(country, smoothf):
    print((country, smoothf))
    counter[0] += 1
    print(counter[0])



    fig = go.Figure()

    if not country or not smoothf:
        return fig

    df = datasets[country].copy()
    if smoothf > 1:
        index = df.index
        df.deaths = smoother(df.deaths, smoothf)
        add_text = ''
    else:
        add_text = ' [smoothed]'

    fig.add_trace(go.Scatter(x=df.index, y=df.deaths,
                mode='lines+markers',
                name='Death Covid'+add_text))

    fig.add_trace(go.Scatter(x=df.index, y=df.vaccines,
                mode='lines+markers',
                name='Vaccines Covid'))

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

try:
    os.environ['SERVER_SOFTWARE']
except KeyError:
    app.run_server(debug=True, port=8011, host='localhost')
else:
    if __name__ == '__main__':
        app.run_server()

# Run debug server with
# python dash_server.py

# Run deployment server with
# gunicorn dash_server:server -b :8000 -t 900 --workers 3 --error-logfile output.log --access-logfile access.log --capture-output --log-level debug
