import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import encyclopedia, demographic

# Create the app with Bootstrap theme
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    pages_folder=""  # disable automatic pages folder requirement
)

server = app.server

# Navbar
navbar = dbc.NavbarSimple(
    brand="Art Encyclopedia",
    brand_href="/",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Encyclopedia Timeline", href="/encyclopedia")),
        dbc.NavItem(dbc.NavLink("Demographic", href="/demographic")),
    ]
)

# Layout
app.layout = dbc.Container([
    navbar,
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content", className="mt-4")
], fluid=True)

# Page routing
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/encyclopedia":
        return encyclopedia.layout
    elif pathname == "/demographic":
        return demographic.layout
    else:
        return html.Div([
            html.H2("Welcome"),
            html.P("Choose a section above to explore.")
        ])

# Register callbacks from both pages
encyclopedia.register_callbacks(app)
demographic.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)

