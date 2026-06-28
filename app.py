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

# Navbar (just brand now)
navbar = dbc.NavbarSimple(
    brand="Art Encyclopedia",
    brand_href="/",
    color="dark",
    dark=True
)

# Welcome page layout with buttons
welcome_layout = html.Div([
    html.H2("Welcome", style={"textAlign": "center", "marginTop": "40px"}),
    html.P("Choose a section to explore:", style={"textAlign": "center"}),

    html.Div([
        html.Button("Encyclopedia Timeline", id="encyclopedia-btn", n_clicks=0,
                    style={"margin": "10px", "padding": "12px 24px", "fontSize": "16px",
                           "backgroundColor": "#0074D9", "color": "white", "border": "none",
                           "borderRadius": "6px", "cursor": "pointer",
                           "transition": "all 0.3s ease"}),

        html.Button("Demographic", id="demographic-btn", n_clicks=0,
                    style={"margin": "10px", "padding": "12px 24px", "fontSize": "16px",
                           "backgroundColor": "#2ECC40", "color": "white", "border": "none",
                           "borderRadius": "6px", "cursor": "pointer",
                           "transition": "all 0.3s ease"})
    ], style={"textAlign": "center", "marginTop": "20px"})
])

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
        return welcome_layout

# Button navigation
@app.callback(
    Output("url", "pathname"),
    [Input("encyclopedia-btn", "n_clicks"),
     Input("demographic-btn", "n_clicks")]
)
def navigate_to_page(ency_clicks, demo_clicks):
    if ency_clicks > 0:
        return "/encyclopedia"
    elif demo_clicks > 0:
        return "/demographic"
    return "/"

# Register callbacks from both pages
encyclopedia.register_callbacks(app)
demographic.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
