from dash import dcc, html, Input, Output
import plotly.express as px
from data_loader import df

layout = html.Div([
    html.H2("Demographics"),
    dcc.Graph(id="gender-pie"),
    dcc.Graph(id="trend-chart")
])

def register_callbacks(app):
    @app.callback(
        [Output("gender-pie", "figure"),
         Output("trend-chart", "figure")],
        [Input("gender-pie", "clickData")]
    )
    def update_demographics(gender_click):
        filtered = df.copy()

        # Filter by gender if clicked
        if gender_click:
            selected_gender = gender_click["points"][0]["label"]
            filtered = filtered[filtered["Gender"] == selected_gender]

        # Gender pie chart (overall, not filtered)
        gender_pie = px.pie(df, names="Gender", title="Overall Works by Gender")

        # Trend chart (filtered by gender if selected)
        trend_data = filtered.dropna(subset=["Century"]).groupby(
            ["Century", "Gender"]
        ).size().reset_index(name="Count")

        trend_fig = px.line(
            trend_data,
            x="Century",
            y="Count",
            color="Gender",
            markers=True,
            title="Filtered Works Across Centuries"
        )

        return gender_pie, trend_fig
