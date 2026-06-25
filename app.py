import dash
from dash import dcc, html, Input, Output
import encyclopedia, demographic

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.H1("Welcome to the Art Encyclopedia"),
    dcc.Location(id="url", refresh=False),
    html.Div([
        dcc.Link("Encyclopedia Timeline", href="/encyclopedia"),
        html.Br(),
        dcc.Link("Demographic", href="/demographic")
    ]),
    html.Div(id="page-content")
])

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
