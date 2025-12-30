"""
Hudson Valley Acupuncture Market Analyzer v2
A Streamlit application with 3D PyDeck visualization using CARTO basemap.
No Mapbox API token required.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Hudson Valley Acupuncture Market Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# County center coordinates for geocoding
COUNTY_DATA = {
    "Westchester": {
        "center": (41.05, -73.78),
        "spread": (0.15, 0.12),
        "towns": [
            ("Yonkers", 40.9312, -73.8987),
            ("White Plains", 41.0340, -73.7629),
            ("Tarrytown", 41.0762, -73.8585),
            ("Scarsdale", 40.9887, -73.7846),
            ("New Rochelle", 40.9115, -73.7824),
            ("Mount Kisco", 41.2048, -73.7268),
            ("Ossining", 41.1626, -73.8615),
            ("Peekskill", 41.2901, -73.9204),
            ("Bronxville", 40.9382, -73.8321),
            ("Dobbs Ferry", 41.0145, -73.8726),
            ("Hastings-on-Hudson", 40.9926, -73.8787),
            ("Ardsley", 41.0109, -73.8438),
            ("Hartsdale", 41.0190, -73.7985),
            ("Sleepy Hollow", 41.0859, -73.8585),
        ]
    },
    "Dutchess": {
        "center": (41.70, -73.88),
        "spread": (0.25, 0.15),
        "towns": [
            ("Poughkeepsie", 41.7004, -73.9210),
            ("Beacon", 41.5048, -73.9696),
            ("Rhinebeck", 41.9265, -73.9129),
            ("Hyde Park", 41.7843, -73.9332),
            ("Fishkill", 41.5354, -73.8987),
            ("Wappingers Falls", 41.5965, -73.9110),
            ("Red Hook", 41.9948, -73.8760),
            ("Tivoli", 42.0576, -73.9079),
        ]
    },
    "Rockland": {
        "center": (41.10, -73.98),
        "spread": (0.08, 0.10),
        "towns": [
            ("Nyack", 41.0907, -73.9179),
            ("New City", 41.1476, -74.0135),
            ("Spring Valley", 41.1132, -74.0438),
            ("Suffern", 41.1148, -74.1493),
            ("Pearl River", 41.0587, -74.0218),
            ("Haverstraw", 41.1976, -73.9643),
            ("Piermont", 41.0410, -73.9185),
            ("Stony Point", 41.2293, -73.9871),
            ("Upper Nyack", 41.1057, -73.9229),
        ]
    },
    "Orange": {
        "center": (41.40, -74.10),
        "spread": (0.15, 0.20),
        "towns": [
            ("Newburgh", 41.5034, -74.0104),
            ("Middletown", 41.4459, -74.4229),
            ("Monroe", 41.3307, -74.1868),
            ("Cornwall", 41.4426, -74.0135),
            ("Cornwall-on-Hudson", 41.4426, -74.0135),
            ("Warwick", 41.2565, -74.3593),
            ("Highland Falls", 41.3693, -73.9635),
            ("West Point", 41.3915, -73.9571),
        ]
    },
    "Ulster": {
        "center": (41.88, -74.05),
        "spread": (0.20, 0.18),
        "towns": [
            ("Kingston", 41.9270, -73.9974),
            ("New Paltz", 41.7465, -74.0868),
            ("Saugerties", 42.0776, -73.9529),
            ("Woodstock", 42.0409, -74.1182),
            ("Highland", 41.7209, -73.9610),
            ("Marlboro", 41.6065, -73.9735),
            ("Milton", 41.6559, -73.9760),
        ]
    },
    "Albany": {
        "center": (42.65, -73.80),
        "spread": (0.12, 0.10),
        "towns": [
            ("Albany", 42.6526, -73.7562),
            ("Delmar", 42.6193, -73.8335),
            ("Latham", 42.7476, -73.7535),
            ("Guilderland", 42.6876, -73.9035),
            ("Coeymans", 42.4743, -73.7929),
            ("Ravena", 42.4676, -73.8135),
        ]
    },
    "Columbia": {
        "center": (42.25, -73.75),
        "spread": (0.15, 0.12),
        "towns": [
            ("Hudson", 42.2526, -73.7907),
            ("Chatham", 42.3643, -73.5946),
            ("Kinderhook", 42.3943, -73.6907),
            ("Stuyvesant", 42.3826, -73.7307),
            ("Stockport", 42.3026, -73.7507),
        ]
    },
    "Putnam": {
        "center": (41.42, -73.75),
        "spread": (0.10, 0.12),
        "towns": [
            ("Cold Spring", 41.4201, -73.9546),
            ("Carmel", 41.4298, -73.6801),
            ("Brewster", 41.3973, -73.6168),
            ("Garrison", 41.3801, -73.9471),
        ]
    },
    "Greene": {
        "center": (42.28, -74.00),
        "spread": (0.12, 0.15),
        "towns": [
            ("Catskill", 42.2176, -73.8607),
            ("Athens", 42.2593, -73.8079),
            ("Windham", 42.3076, -74.2507),
            ("Coxsackie", 42.3509, -73.8029),
        ]
    },
    "Rensselaer": {
        "center": (42.65, -73.65),
        "spread": (0.10, 0.08),
        "towns": [
            ("Troy", 42.7284, -73.6918),
            ("Rensselaer", 42.6426, -73.7362),
            ("Castleton-on-Hudson", 42.5326, -73.7507),
        ]
    },
}


@st.cache_data
def load_clinic_data():
    """Load real clinic data from CSV and add coordinates."""

    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    filtered_path = script_dir / "hudson_valley_acupuncture_clinics_filtered.csv"
    raw_path = script_dir / "hudson_valley_acupuncture_clinics.csv"

    try:
        if filtered_path.exists():
            df = pd.read_csv(filtered_path)
        elif raw_path.exists():
            df = pd.read_csv(raw_path)
        else:
            st.error(f"CSV file not found. Looking in: {script_dir}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

    # Clean data
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["total_ratings"], errors="coerce").fillna(0).astype(int)
    df["county"] = df["search_county"]

    # Add coordinates based on address and search_city
    np.random.seed(42)

    def get_coordinates(row):
        address = str(row.get("address", "")).lower()
        city = str(row.get("search_city", "")).lower()
        county = str(row.get("search_county", ""))

        # Try to match town from address or search_city
        for county_name, county_info in COUNTY_DATA.items():
            for town_data in county_info["towns"]:
                town_name, town_lat, town_lon = town_data
                if town_name.lower() in address or town_name.lower() == city:
                    lat_offset = np.random.uniform(-0.008, 0.008)
                    lon_offset = np.random.uniform(-0.008, 0.008)
                    return town_lat + lat_offset, town_lon + lon_offset

        # Fall back to county center
        if county in COUNTY_DATA:
            center = COUNTY_DATA[county]["center"]
            spread = COUNTY_DATA[county]["spread"]
            lat_offset = np.random.uniform(-spread[0]/2, spread[0]/2)
            lon_offset = np.random.uniform(-spread[1]/2, spread[1]/2)
            return center[0] + lat_offset, center[1] + lon_offset

        # Default to Hudson Valley center
        return 41.5 + np.random.uniform(-0.1, 0.1), -73.9 + np.random.uniform(-0.1, 0.1)

    coords = df.apply(get_coordinates, axis=1)
    df["latitude"] = coords.apply(lambda x: x[0])
    df["longitude"] = coords.apply(lambda x: x[1])

    return df


def get_color_from_rating(rating):
    """Map rating to RGB color."""
    if pd.isna(rating):
        return [128, 128, 128, 200]  # Gray for no rating
    elif rating >= 5.0:
        return [34, 197, 94, 220]    # Bright Green
    elif rating >= 4.5:
        return [134, 239, 172, 220]  # Light Green
    elif rating >= 4.0:
        return [250, 204, 21, 220]   # Gold
    else:
        return [239, 68, 68, 220]    # Red


def create_3d_map(df, view_state):
    """Create PyDeck 3D visualization with ColumnLayer."""

    df = df.copy()
    df["color"] = df["rating"].apply(get_color_from_rating)
    df["elevation"] = df["review_count"] * 50

    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=150,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    deck = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        map_style="road",
        tooltip={
            "html": "<b>{name}</b><br/>County: {county}<br/>Rating: {rating}<br/>Reviews: {review_count}",
            "style": {"backgroundColor": "#1e293b", "color": "white"}
        }
    )

    return deck


def main():
    st.title("Hudson Valley Acupuncture Market Analyzer")
    st.markdown("**3D visualization of market saturation.** Taller columns = more reviews. Color = rating.")

    # Load data
    df = load_clinic_data()

    if df.empty:
        st.warning("No data available. Please check that CSV files exist in the repository.")
        st.stop()

    # Sidebar filters
    st.sidebar.header("Filters")

    all_counties = ["All Counties"] + sorted(df["county"].unique().tolist())
    selected_county = st.sidebar.selectbox("County", all_counties)

    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
    max_reviews = st.sidebar.slider("Max Reviews", 10, 400, 400, 10)

    # Filter data
    filtered_df = df.copy()
    if selected_county != "All Counties":
        filtered_df = filtered_df[filtered_df["county"] == selected_county]
    filtered_df = filtered_df[(filtered_df["rating"] >= min_rating) | (filtered_df["rating"].isna())]
    filtered_df = filtered_df[filtered_df["review_count"] <= max_reviews]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clinics", len(filtered_df))
    col2.metric("Avg Rating", f"{filtered_df['rating'].mean():.2f}" if len(filtered_df) > 0 else "N/A")
    col3.metric("Avg Reviews", f"{filtered_df['review_count'].mean():.1f}" if len(filtered_df) > 0 else "N/A")
    col4.metric("Total Reviews", f"{filtered_df['review_count'].sum():,}")

    # Color legend
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Color Legend**")
    st.sidebar.markdown("🟢 Bright Green: 5.0 | 🟢 Light Green: 4.5-4.9")
    st.sidebar.markdown("🟡 Gold: 4.0-4.4 | 🔴 Red: <4.0 | ⚪ Gray: No rating")

    # Map
    st.subheader("Competitor Map")

    col1, col2, col3 = st.columns(3)
    pitch = col1.slider("Tilt", 0, 75, 55)
    bearing = col2.slider("Rotation", -180, 180, 15)
    zoom = col3.slider("Zoom", 7.0, 11.0, 8.0, 0.5)

    if len(filtered_df) > 0:
        center_lat = filtered_df["latitude"].mean()
        center_lon = filtered_df["longitude"].mean()
    else:
        center_lat, center_lon = 41.5, -73.9

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=pitch,
        bearing=bearing
    )

    if len(filtered_df) > 0:
        deck = create_3d_map(filtered_df, view_state)
        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.warning("No clinics match filters.")

    # Data tables
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 by Reviews")
        top = filtered_df.nlargest(10, "review_count")[["name", "county", "rating", "review_count"]]
        top.columns = ["Clinic", "County", "Rating", "Reviews"]
        st.dataframe(top, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Market Opportunities")
        bottom = filtered_df[filtered_df["review_count"] > 0].nsmallest(10, "review_count")[["name", "county", "rating", "review_count"]]
        bottom.columns = ["Clinic", "County", "Rating", "Reviews"]
        st.dataframe(bottom, hide_index=True, use_container_width=True)

    # County breakdown
    st.markdown("---")
    st.subheader("County Analysis")
    county_stats = filtered_df.groupby("county").agg({
        "name": "count",
        "rating": "mean",
        "review_count": ["mean", "sum"]
    }).round(2)
    county_stats.columns = ["Clinics", "Avg Rating", "Avg Reviews", "Total Reviews"]
    county_stats = county_stats.sort_values("Clinics", ascending=False)
    st.dataframe(county_stats, use_container_width=True)

    st.caption("Data: Google Maps Places API | Visualization: PyDeck ColumnLayer")


if __name__ == "__main__":
    main()
