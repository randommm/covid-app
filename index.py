import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app1 import App1, register_callbacks1
from app2 import App2, register_callbacks2
#from homepage import Homepage
import os

#'BOOTSTRAP', 'GRID', '_BOOTSWATCH_BASE', 'CERULEAN', 'COSMO', 'CYBORG', 'DARKLY', 'FLATLY', 'JOURNAL', 'LITERA', 'LUMEN', 'LUX', 'MATERIA', 'MINTY', 'PULSE', 'SANDSTONE', 'SIMPLEX', 'SKETCHY', 'SLATE', 'SOLAR', 'SPACELAB', 'SUPERHERO', 'UNITED', 'YETI'
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE],
meta_tags=[dict(name="viewport",content="width=1000px, initial-scale=1.0")])
app.config.suppress_callback_exceptions = True
app.title = 'Corona vaccine data'
server = app.server

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/app1':
        return App1()
    elif pathname == '/app2':
        return App2()
    else:
        return App1()

register_callbacks1(app)
register_callbacks2(app)

try:
    os.environ['SERVER_SOFTWARE']
except KeyError:
    app.run_server(debug=True, port=8011, host='localhost')
else:
    if __name__ == '__main__':
        app.run_server()
