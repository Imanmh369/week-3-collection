import pandas as pd

# Load dataset
df = pd.read_csv("https://media.githubusercontent.com/media/Imanmh369/week-3-collection/refs/heads/main/Artworks.csv")

# Clean up Gender
df["Gender"] = df["Gender"].str.lower().str.replace(r"[^a-z]", "", regex=True)
df["Gender"] = df["Gender"].replace({"male": "Male", "female": "Female"})
df["Gender"] = df["Gender"].where(df["Gender"].isin(["Male", "Female"]), "Unknown")

# Clean up Nationality
df["Nationality"] = df["Nationality"].str.replace(r"[\(\)]", "", regex=True).str.strip()
df["Nationality"] = df["Nationality"].replace("", "Unknown")

# Convert Date to numeric year
df["Year"] = pd.to_numeric(df["Date"], errors="coerce")
df["Century"] = (df["Year"] // 100 + 1).astype("Int64")
