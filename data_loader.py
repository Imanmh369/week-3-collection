import pandas as pd

# -------------------------
# Load datasets
# -------------------------
artworks = pd.read_csv("Artworks.csv")
artists = pd.read_csv("Artists.csv")

# -------------------------
# Ensure IDs match type
# -------------------------
artworks["ConstituentID"] = artworks["ConstituentID"].astype(str)
artists["ConstituentID"] = artists["ConstituentID"].astype(str)

# -------------------------
# Clean Gender column in Artists
# -------------------------
artists["Gender"] = artists["Gender"].str.lower().str.replace(r"[^a-z]", "", regex=True)
artists["Gender"] = artists["Gender"].replace({"male": "Male", "female": "Female"})
artists["Gender"] = artists["Gender"].where(artists["Gender"].isin(["Male", "Female"]), "Unknown")

# -------------------------
# Clean Nationality column in Artists
# -------------------------
artists["Nationality"] = artists["Nationality"].str.replace(r"[\(\)]", "", regex=True).str.strip()
artists["Nationality"] = artists["Nationality"].replace("", "Unknown")

# -------------------------
# Clean Date in Artworks
# -------------------------
artworks["Year"] = pd.to_numeric(artworks["Date"], errors="coerce")
artworks["Century"] = (artworks["Year"] // 100 + 1).astype("Int64")

# -------------------------
# Merge datasets on ConstituentID
# -------------------------
merged = artworks.merge(
    artists,
    on="ConstituentID",
    how="left"
)

# -------------------------
# Export for use in Dash
# -------------------------
df = artworks          # keep artworks as df
artist_df = artists    # keep artists as artist_df
df_merged = merged     # merged dataset

