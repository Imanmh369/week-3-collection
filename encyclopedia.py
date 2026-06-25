from dash import dcc, html, Input, Output
import pandas as pd
from data_loader import df
from PIL import Image
import requests
from io import BytesIO

# Normalize mediums into categories
medium_map = {
    "oil on canvas": "Painting",
    "oil painting": "Painting",
    "watercolor": "Painting",
    "acrylic": "Painting",
    "tempera": "Painting",
    "ink": "Drawing",
    "ink on paper": "Drawing",
    "charcoal": "Drawing",
    "graphite": "Graphite",
    "pencil": "Drawing",
    "bronze": "Sculpture",
    "marble": "Sculpture",
    "wood": "Sculpture",
    "clay": "Sculpture",
    "digital": "Digital",
    "digital print": "Digital",
    "photography": "Digital",
    "mixed media": "Mixed Media",
    "collage": "Mixed Media",
    "assemblage": "Mixed Media",
    "other": "Other"
}

def normalize_medium(medium):
    if not isinstance(medium, str):
        return "Unknown"
    m = medium.strip().lower()
    return medium_map.get(m, "Other")

# Distinct colors per category
category_colors = {
    "Painting": "#b58900",
    "Drawing": "#444",
    "Graphite": "#2ca02c",
    "Digital": "#0044cc",
    "Sculpture": "#8c6239",
    "Mixed Media": "#6a0dad",
    "Other": "#e377c2",
    "Unknown": "#ccc"
}

# Build proportional gradient
def build_gradient(counts):
    total = counts.sum()
    stops = []
    current = 0
    for category, count in counts.items():
        color = category_colors.get(category, "#999")
        start = int((current / total) * 100)
        end = int(((current + count) / total) * 100)
        stops.append(f"{color} {start}%")
        stops.append(f"{color} {end}%")
        current += count
    return "linear-gradient(to right, " + ", ".join(stops) + ")"

# Improved palette extraction using Pillow adaptive quantization
def extract_palette(url, n=5):
    """
    Fetch image from URL and return up to n dominant colors as CSS rgb(...) strings.
    Returns a list like ['rgb(12,34,56)', ...]. On failure returns ['#ccc'].
    """
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        img.thumbnail((200, 200))
        paletted = img.convert("P", palette=Image.ADAPTIVE, colors=n)
        palette = paletted.getpalette()
        color_counts = paletted.getcolors()
        if not color_counts or not palette:
            return ["#ccc"]
        dominant = sorted(color_counts, reverse=True)
        swatches = []
        for count, idx in dominant[:n]:
            r, g, b = palette[idx*3:idx*3+3]
            swatches.append(f"rgb({r},{g},{b})")
        return swatches
    except Exception as e:
        print("Palette extraction failed for", url, ":", e)
        return ["#ccc"]

# Layout
classifications = df["Classification"].dropna().unique()

layout = html.Div([
    html.H2("Encyclopedia Timeline"),
    html.Div([
        dcc.Dropdown(
            options=[{"label": c, "value": c} for c in classifications],
            id="classification-dropdown",
            placeholder="Select classification",
            style={"width": "45%", "display": "inline-block", "margin-right": "10px"}
        ),
        dcc.Dropdown(
            id="artist-dropdown",
            placeholder="Select an artist",
            style={"width": "45%", "display": "inline-block"}
        )
    ]),
    # Medium Bar at top-right corner
    html.Div([
        html.Div(id="medium-gradient", style={
            "width": "200px",
            "height": "15px",
            "border-radius": "6px",
            "box-shadow": "0 0 6px rgba(0,0,0,0.1)"
        }),
        html.Div("Medium Bar", style={
            "margin-top": "5px",
            "font-size": "12px",
            "color": "#444",
            "text-align": "center",
            "font-weight": "bold"
        }),
        html.Div(id="medium-legend", style={
            "margin-top": "5px",
            "font-size": "11px",
            "color": "#555",
            "text-align": "center"
        })
    ], style={
        "position": "absolute",
        "top": "70px",
        "right": "40px",
        "width": "200px",
        "text-align": "center"
    }),
    html.Div(id="timeline-container")
])

def register_callbacks(app):
    @app.callback(
        Output("artist-dropdown", "options"),
        Input("classification-dropdown", "value")
    )
    def update_artists(selected_classification):
        if not selected_classification:
            return []
        filtered = df[df["Classification"] == selected_classification]
        artists = filtered["Artist"].dropna().unique()
        return [{"label": artist, "value": artist} for artist in artists]

    @app.callback(
        [Output("medium-gradient", "style"),
         Output("medium-legend", "children")],
        [Input("artist-dropdown", "value"),
         Input("classification-dropdown", "value")]
    )
    def update_gradient(clicked_artist, selected_classification):
        base_style = {
            "width": "200px",
            "height": "15px",
            "border-radius": "6px",
            "box-shadow": "0 0 6px rgba(0,0,0,0.1)"
        }
        dominant = None
        if not clicked_artist or not selected_classification:
            base_style["background"] = category_colors["Unknown"]
        else:
            artist_data = df[(df["Artist"] == clicked_artist) &
                             (df["Classification"] == selected_classification)].copy()
            artist_data["Medium"] = artist_data["Medium"].apply(normalize_medium)
            if not artist_data.empty:
                counts = artist_data["Medium"].value_counts()
                dominant = counts.idxmax()
                gradient = build_gradient(counts)
                base_style["background"] = gradient
            else:
                base_style["background"] = category_colors["Unknown"]

        def style_item(text, category):
            if dominant == category:
                return html.Span(text, style={"margin-right": "10px", "font-weight": "bold", "color": "#000"})
            return html.Span(text, style={"margin-right": "10px"})

        legend = html.Div([
            style_item("🟡 Painting", "Painting"),
            style_item("⚫ Drawing", "Drawing"),
            style_item("🟢 Graphite", "Graphite"),
            style_item("🟤 Sculpture", "Sculpture"),
            style_item("🔵 Digital", "Digital"),
            style_item("🟣 Mixed Media", "Mixed Media"),
            style_item("🌸 Other", "Other")
        ])
        return base_style, legend

    @app.callback(
        Output("timeline-container", "children"),
        [Input("artist-dropdown", "value"),
         Input("classification-dropdown", "value")]
    )
    def show_timeline(clicked_artist, selected_classification):
        if not clicked_artist or not selected_classification:
            return html.Div("Select classification and artist to view timeline.")

        artist_data = df[(df["Artist"] == clicked_artist) &
                         (df["Classification"] == selected_classification)].copy()
        artist_data["Date"] = pd.to_numeric(artist_data["Date"], errors="coerce")
        artist_data["Medium"] = artist_data["Medium"].apply(normalize_medium)
        artist_data = artist_data.sort_values("Date")

        if artist_data.empty:
            return html.Div("No works found for this artist in that classification.")

        items = []
        for i, (_, row) in enumerate(artist_data.head(20).iterrows()):
            side = "left" if i % 2 == 0 else "right"
            image_component = None
            palette_div = None

            if "ImageURL" in row and pd.notna(row["ImageURL"]) and str(row["ImageURL"]).startswith("http"):
                image_component = html.Img(src=row["ImageURL"], style={"width": "200px", "margin-top": "5px"})
                # Only add palette for Painting classification
                if isinstance(selected_classification, str) and selected_classification.lower() == "painting":
                    palette = extract_palette(row["ImageURL"], n=5)
                    swatches = []
                    for c in palette:
                        swatches.append(html.Div(
                            title=str(c),
                            style={
                                "background": c,
                                "width": "40px",
                                "height": "20px",
                                "display": "inline-block",
                                "margin-right": "2px",
                                "border": "1px solid rgba(0,0,0,0.08)"
                            }
                        ))
                    palette_div = html.Div(swatches, style={"margin-top": "5px", "display": "inline-block"})

            entry_children = [
                html.H4(f"{row.get('Date', '')} — {row.get('Title', '')}"),
                html.P(f"Medium: {row.get('Medium', '')}"),
                html.P(f"Classification: {row.get('Classification', '')}"),
                html.P(f"Nationality: {row.get('Nationality', '')}"),
                html.P(f"Gender: {row.get('Gender', '')}"),
                image_component
            ]
            if palette_div:
                entry_children.append(palette_div)

            items.append(html.Div([
                html.Div(entry_children, style={
                    "width": "45%",
                    "text-align": "left" if side == "left" else "right",
                    "float": side,
                    "margin-bottom": "30px",
                    "padding": "5px",
                    "z-index": "1"
                })
            ], style={"position": "relative", "clear": "both", "margin-bottom": "40px"}))

        timeline = html.Div([
            html.Div(style={
                "position": "absolute",
                "top": "0",
                "bottom": "0",
                "left": "50%",
                "transform": "translateX(-50%)",
                "width": "3px",
                "background-color": "black",
                "z-index": "0"
            }),
            html.Div(items)
        ], style={
            "position": "relative",
            "margin": "50px auto",
            "width": "80%",
            "min-height": "100vh",
            "overflow": "hidden"
        })

        return timeline
