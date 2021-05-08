import dash_bootstrap_components as dbc

def Navbar():
    navbar = dbc.NavbarSimple(

children=[
  dbc.NavItem(dbc.NavLink("Per contry data", href="/app1")),
  dbc.NavItem(dbc.NavLink("Countrywise comparison", href="/app2")
  ,style={'margin-left': '1 !important', 'text-align':'left'}
  ),
]

    )
    return navbar
