import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import os

from navbar import Navbar
nav = Navbar()

body = html.Div([
    [

        html.H2("Covid data"),
        html.P(
         """Covid data"""
           ),

    ],
])

def Homepage():
    layout = html.Div([
    nav,
    body
    ])
    return layout

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = Homepage()
