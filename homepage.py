import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
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
