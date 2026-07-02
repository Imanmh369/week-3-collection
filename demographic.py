from dash import dcc, html, Output, Input
import plotly.express as px
from dash import dash_table
import pandas as pd
from data_loader import artist_df, df
import re

# -------------------------
# Layout
# -------------------------
layout = html.Div([
    html.H2("Demographic Analysis", style={"textAlign": "left", "color": "#2c3e50"}),

    # Section 1: Nationality Distribution (Top 20)
    html.Div([
        html.H4("Summary: Total Artists by Nationality (Top 20)",
                style={"textAlign": "center", "marginBottom": "30px","marginTop": "40px","color": "#2c3e50","fontWeight": "bold"}),

        dcc.Graph(
            id="nationality-summary-chart",
            style={"width": "90%", "height": "700px", "margin": "auto","paddingBottom": "40px"}
        )
    ], style={"marginBottom": "80px", "display":"block"}),

    # Section 2: Gender × Nationality chart beside Female Contributor table
    html.Div([
        # Chart on the left
        html.Div([
            html.H4("Distribution of Artists by Nationality and Gender (Top 15)",
                    style={"textAlign": "center", "marginBottom": "10px"}),

            dcc.Graph(
                id="gender-nationality-chart",
                style={"width": "100%", "height": "600px"}
            )
        ], style={"flex": "2", "paddingRight": "20px"}),

        # Compact Female table on the right
        html.Div([
            html.H4("Top Female Contributor", style={"textAlign": "center", "marginBottom": "10px"}),

            dash_table.DataTable(
                id="female-summary-table",
                columns=[
                    {"name": "Nationality", "id": "Nationality"},
                    {"name": "Female Percentage (%)", "id": "Percentage"}
                ],
                data=[],  # filled in callback
                style_table={
                    "width": "90%",
                    "margin": "auto",
                    "maxHeight": "400px",
                    "overflowY": "auto",
                    "boxShadow": "0px 2px 6px rgba(0,0,0,0.1)",
                    "borderRadius": "6px"
                },
                style_cell={
                    "textAlign": "center",
                    "fontFamily": "Arial",
                    "fontSize": "13px"
                },
                style_header={
                    "backgroundColor": "#2c3e50",
                    "color": "white",
                    "fontWeight": "bold"
                },
                style_data={
                    "backgroundColor": "#f8f9fa",
                    "color": "#2c3e50"
                },
                page_size=5  # show only top 5 rows
            )
        ], style={"flex": "1", "alignSelf": "center"})
    ], style={"display": "flex", "flexDirection": "row", "marginTop": "40px"}),


    html.Div([
        html.H4("Acquisitions Across Centuries by Gender",
                style={"textAlign": "center", "marginBottom": "20px",
               "marginTop": "60px", "color": "#2c3e50", "fontWeight": "bold" }
                ),

                dcc.Graph(
                    id="century-gender-area",
                    style={"width": "90%", "height": "600px", "margin": "auto"}
                )
    ]),

    html.Div([
        html.H4("Nationality × Classification Distribution",
                style={"textAlign": "center", "marginBottom": "30px",
                       "marginTop": "40px", "color": "#2c3e50", "fontWeight": "bold"}),
        dcc.Graph(
            id="nationality-classification-chart",
            style={"width": "90%", "height": "700px", "margin": "auto", "paddingBottom": "40px"}
        )
    ], style={"marginBottom": "80px", "display": "block"}),

    html.Div([
        html.H4("Gender Distribution Across Departments",
                style={"textAlign": "center", "marginBottom": "30px",
                   "marginTop": "40px", "color": "#2c3e50", "fontWeight": "bold"}),

        dcc.Graph(
            id="gender-department-chart",
            style={"width": "90%", "height": "700px", "margin": "auto", "paddingBottom": "40px"}
        ),

        html.P(
            id="gender-department-comment",
            style={"textAlign": "center", "fontStyle": "italic",
                   "color": "#2c3e50", "marginTop": "20px"

            }
        )

    ], style={"marginBottom": "80px"})

    

])

# -------------------------
# Callbacks
# -------------------------
def register_callbacks(app):
    # --- Nationality Chart ---
    @app.callback(
        Output("nationality-summary-chart", "figure"),
        Input("nationality-summary-chart", "id")
    )
    def update_nationality_summary(_):
        nationality_data = (
            artist_df.dropna(subset=["Nationality"])
            .groupby("Nationality")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
            .head(20)
        )

        total_artists = nationality_data["Count"].sum()
        nationality_data["Percentage"] = (nationality_data["Count"] / total_artists) * 100

        fig = px.bar(
            nationality_data,
            x="Nationality",
            y="Percentage",
            color="Nationality",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )

        fig.update_traces(width=0.8)

         # Add annotation for interpretation
        if "American" in nationality_data["Nationality"].values:
            american_pct = nationality_data.loc[
                nationality_data["Nationality"] == "American", "Percentage"
            ].values[0]

            fig.add_annotation(
                text=(
                    f"MoMA’s collection reveals a striking imbalance:<br> "
                    f"American artists represent about {american_pct:.1f}% of the museum’s holdings — "
                    f"nearly half of all artists. While MoMA promotes global diversity,<br> "
                    f"this data suggests its core collection remains predominantly Western, "
                    f"with limited representation from non‑Western regions."
                ),
                xref="paper",
                yref="paper",
                x=0.5,
                y=1.20,
                showarrow=False,
                font=dict(size=13, color="#2c3e50"),
                align="center"
            )


        fig.update_layout(
            plot_bgcolor="#f8f9fa",
            paper_bgcolor="#ffffff",
            font=dict(color="#2c3e50", size=14),
            title_font=dict(size=16, color="#2c3e50"),
            xaxis_title="Nationality",
            yaxis_title="Percentage of Artists (%)",
            hovermode="x unified",
            margin=dict(l=60, r=60, t=100, b=180),
            autosize=True,
            xaxis=dict(
                tickangle=20, 
                tickfont=dict(size=13),
                ticklabeloverflow="allow", 
                automargin=True),
            yaxis=dict(
                gridcolor="#dfe6e9", 
                zerolinecolor="#b2bec3"),

            legend=dict(
                orientation="v", 
                yanchor="top", 
                y=0.9, xanchor="left", 
                x=1.02, 
                font=dict(size=11))
        )
        return fig

    # --- Gender × Nationality Chart + Female Table ---
    @app.callback(
        [Output("gender-nationality-chart", "figure"),
         Output("female-summary-table", "data")],
        Input("gender-nationality-chart", "id")
    )
    def update_gender_nationality(_):
        artist_df["Gender"] = artist_df["Gender"].str.strip().str.title()
        artist_df["Gender"] = artist_df["Gender"].where(
            artist_df["Gender"].isin(["Male", "Female"]), "Unknown"
        )

        gender_nat = (
            artist_df.dropna(subset=["Nationality", "Gender"])
            .groupby(["Nationality", "Gender"])
            .size()
            .reset_index(name="Count")
        )

        gender_nat["Percentage"] = gender_nat.groupby("Nationality")["Count"].transform(
            lambda x: (x / x.sum()) * 100
        )

        top_nat = artist_df["Nationality"].value_counts().head(15).index
        gender_nat = gender_nat[gender_nat["Nationality"].isin(top_nat)]

        # Remove Unknown gender
        gender_nat = gender_nat[gender_nat["Gender"].isin(["Male", "Female"])]


        # Chart
        fig = px.bar(
            gender_nat,
            x="Percentage",
            y="Nationality",
            color="Gender",
            barmode="stack",       # keep stacked style
            orientation="h", 
            title="Nationality × Gender Distribution (Top 15)",
            color_discrete_map={"Male": "#5DADE2", "Female": "#F1948A", "Unknown": "#D5DBDB"}
        )

        fig.update_layout(
            plot_bgcolor="#f8f9fa",
            paper_bgcolor="#ffffff",
            font=dict(color="#2c3e50", size=13),
            title_font=dict(size=16, color="#2c3e50"),
            xaxis_title="Percentage of Artists (%)",
            yaxis_title="Nationality",
            hovermode="x unified",
            margin=dict(l=100, r=40, t=100, b=60),
            yaxis=dict(categoryorder="total ascending", tickfont=dict(size=12)),
            legend=dict(title="Gender", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )

        fig.update_traces(
            texttemplate="%{x:.1f}%",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=12, color="white"),
            cliponaxis=False

        
)

        # Female summary table (top 5)
        female_summary = (
            gender_nat[gender_nat["Gender"] == "Female"]
            .sort_values("Percentage", ascending=False)
            [["Nationality", "Percentage"]]
            .head(5)
            .reset_index(drop=True)
        )

        return fig, female_summary.to_dict("records")
    
    # --- Acquisitions Across Centuries by Gender ---
    @app.callback(
        Output("century-gender-area", "figure"),
        Input("century-gender-area", "id")
    )

    def update_century_gender(_):
        artist_df["Gender"] = artist_df["Gender"].str.strip().str.title()
        artist_df["Gender"] = artist_df["Gender"].where(
            artist_df["Gender"].isin(["Male", "Female"]), "Unknown"
        )

        # Replace 0s with NaN
        artist_df["BeginDate"] = artist_df["BeginDate"].replace(0, pd.NA)

        # Convert year to century
        artist_df["Century"] = artist_df["BeginDate"].apply(
            lambda x: int(x // 100 + 1) if pd.notna(x) else "Unknown"
        )

        # Group by century and gender
        century_gender = (
            artist_df.dropna(subset=["Century", "Gender"])
            .groupby(["Century", "Gender"])
            .size()
            .reset_index(name="Count")
        )

        # Remove Unknown gender
        century_gender = century_gender[century_gender["Gender"].isin(["Male", "Female"])]


        # Normalize to percentages
        century_gender["Percentage"] = century_gender.groupby("Century")["Count"].transform(
        lambda x: (x / x.sum()) * 100
    )


        # Area chart
        fig = px.line(
            century_gender,
            x="Century",
            y="Count",
            color="Gender",
            markers=True,
            line_shape="linear",
            title="Percentage of Works Across Centuries by Gender",
            color_discrete_map={"Male": "#5DADE2", "Female": "#F1948A"}
        )

        # Styling
        fig.update_layout(
            plot_bgcolor="#f8f9fa",
            paper_bgcolor="#ffffff",
            font=dict(color="#2c3e50", size=13),
            title_font=dict(size=16, color="#2c3e50"),
            xaxis_title="Century",
            yaxis_title="Count of Works",
            hovermode="x unified",
            margin=dict(l=60, r=60, t=100, b=80),
            legend=dict(title="Gender", orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="center", x=0.5)
)

        fig.update_traces(line=dict(width=3), marker=dict(size=8, symbol="circle"))

        fig.add_annotation(
             x=20,  # century number
             y=century_gender.loc[(century_gender["Century"] == 20) & (century_gender["Gender"] == "Female"), "Count"].values[0],
             text="Female representation rises in 20th century",
             showarrow=True,
             arrowhead=2,
             ax=40, ay=-40,
             font=dict(size=12, color="#2c3e50"),
             bgcolor="#f8f9fa"
)

        fig.add_annotation(
            x=19,
            y=century_gender.loc[(century_gender["Century"] == 19) & (century_gender["Gender"] == "Male"), "Count"].values[0],
            text="Male dominance continues",
            showarrow=True,
            arrowhead=2,
            ax=-40, ay=-40,
            font=dict(size=12, color="#2c3e50"),
            bgcolor="#f8f9fa"
)

        return fig
    

    # --- Nationality × Classification Chart ---

    @app.callback(
        Output("nationality-classification-chart", "figure"),
        Input("nationality-classification-chart", "id")
    )
    
    def update_nat_class_chart(_):


        def clean_nationality(val):
            if pd.isna(val):
                return None
            val = val.replace("()", "").strip() 
            val = re.sub(r"[()]", "", val).strip()
            parts = val.split() 
            parts = list(dict.fromkeys(parts))
            return " ".join(parts) if parts else None 
        
        df["Nationality"] = df["Nationality"].apply(clean_nationality)

        

        nat_class = (
            df.dropna(subset=["Nationality", "Classification"])
            .groupby(["Nationality", "Classification"])
            .size()
            .reset_index(name="Count")
        )

        # Focus on top 15 nationalities for readability
        top_nat = df["Nationality"].value_counts().head(10).index
        top_class = df["Classification"].value_counts().head(6).index
        filtered = nat_class[nat_class["Nationality"].isin(top_nat) & nat_class["Classification"].isin(top_class)]
        
        

        if filtered.empty:
            return px.imshow([[0]], title="No data available")


            # Pivot for heatmap
        pivot = filtered.pivot_table(index="Nationality", columns="Classification", values="Count", fill_value=0)
        pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100  # normalize to %

        # Create heatmap
        fig = px.imshow(
            pivot,
            color_continuous_scale="Blues",
            text_auto=".1f",
            title="Nationality × Classification Heatmap (Top 10 Nationalities × Top 6 Classifications)",
            labels=dict(x="Classification", y="Nationality", color="Number of Artworks")
    )
        
        # Styling
        fig.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color="#2c3e50", size=13),
            title_font=dict(size=16, color="#2c3e50"),
            margin=dict(l=80, r=80, t=120, b=100),
            coloraxis_colorbar=dict(
                title="LOW → HIGH",
                title_side="top",
        ),
           xaxis=dict(tickangle=15, tickfont=dict(size=12)),
           yaxis=dict(tickfont=dict(size=12))
    )
        

        # Add subtitle annotation
        fig.add_annotation(
            text="Darker cells show higher representation of a classification within each nationality.",
            xref="paper", yref="paper", x=0.5, y=1.12, showarrow=False,
            font=dict(size=13, color="#2c3e50"), align="center"
    )
        
        fig.update_traces(textfont=dict(size=12, color="#2c3e50"))
        
        return fig
    

    @app.callback(
        [Output("gender-department-chart", "figure"),
         Output("gender-department-comment", "children")],
        Input("gender-department-chart", "id")
    )

    def update_gender_department(_):

       
        df["Gender"] = df["Gender"].fillna("Unknown")

        # Clean Gender column
        df["Gender"] = df["Gender"].astype(str).str.lower().str.strip()

        df["Gender"] = df["Gender"].apply(lambda g: re.sub(r"[()]", "", str(g)).strip())

        df['Gender'] = df["Gender"].replace({
            "male": "Male",
            "female": "Female"
        })

        # Any other value becomes Unknown
        df["Gender"] = df["Gender"].where(df["Gender"].isin(["Male", "Female"]), "Unknown")

        print("Cleaned Gender values:", df["Gender"].unique()[:10])
        print("Gender counts:", df["Gender"].value_counts())

        dept_gender =(
            df.dropna(subset=["Department", "Gender"])
            .groupby(["Department", "Gender"])
            .size()
            .reset_index(name="Count")
         )
        
        print("Grouped data sample:", dept_gender.head(10))

        # Remove Unknown if you don’t want it
        dept_gender = dept_gender[dept_gender["Gender"].isin(["Male", "Female"])]


        dept_totals = dept_gender.groupby("Department")["Count"].sum().reset_index(name="Total")
        dept_gender = dept_gender.merge(dept_totals, on="Department")
        dept_gender["Percentage"] = (dept_gender["Count"] / dept_gender["Total"]) * 100

        # Create stacked bar chart
        fig = px.bar(
            dept_gender,
            x="Department",
            y="Count",
            color="Gender",
            barmode="stack",
            title="Gender Distribution Across Departments",
            color_discrete_map={"Male": "#4B77BE", "Female": "#F5B7B1"}
    )
        
        # Styling
        fig.update_layout(
            plot_bgcolor="#f9f9f9",
            paper_bgcolor="#ffffff",
            font=dict(color="#2c3e50", size=13),
            title_font=dict(size=16, color="#2c3e50"),
            xaxis_title="Department",
            yaxis_title="Count by Gender",
            hovermode="x unified",
            margin=dict(l=60, r=60, t=100, b=180),
            xaxis=dict(tickangle=0, tickfont=dict(size=10)),
            legend=dict(title="Gender", orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="center", x=0.5)
    )
        
        fig.update_traces(
            texttemplate="%{y:.1f}%",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=11, color="white")
    )
        female_share = dept_gender.query(
            "Department == 'Drawings & Prints' and Gender == 'Female'"
        )["Percentage"].mean()

        comment = (
            f"Across departments, male artists dominate overall, "
            f"but female representation is notably higher in Drawings & Prints "
            f"(≈ {female_share:.1f}% of artworks)."
        )


        
        return fig, comment






    
