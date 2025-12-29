"""
Hudson Valley Acupuncture Market Analyzer v2
A Streamlit application with 3D PyDeck visualization using CARTO basemap.
No Mapbox API token required.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Hudson Valley Acupuncture Market Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# County center coordinates and bounding boxes for realistic distribution
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
            ("Warwick", 41.2565, -74.3593),
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
        ]
    },
    "Columbia": {
        "center": (42.25, -73.75),
        "spread": (0.15, 0.12),
        "towns": [
            ("Hudson", 42.2526, -73.7907),
            ("Chatham", 42.3643, -73.5946),
            ("Kinderhook", 42.3943, -73.6907),
        ]
    },
    "Putnam": {
        "center": (41.42, -73.75),
        "spread": (0.10, 0.12),
        "towns": [
            ("Cold Spring", 41.4201, -73.9546),
            ("Carmel", 41.4298, -73.6801),
            ("Brewster", 41.3973, -73.6168),
        ]
    },
    "Greene": {
        "center": (42.28, -74.00),
        "spread": (0.12, 0.15),
        "towns": [
            ("Catskill", 42.2176, -73.8607),
            ("Athens", 42.2593, -73.8079),
            ("Windham", 42.3076, -74.2507),
        ]
    },
    "Rensselaer": {
        "center": (42.65, -73.65),
        "spread": (0.10, 0.08),
        "towns": [
            ("Troy", 42.7284, -73.6918),
            ("Rensselaer", 42.6426, -73.7362),
        ]
    },
}

# County distribution percentages (from Clinic_Summary.md)
COUNTY_DISTRIBUTION = {
    "Westchester": 0.323,   # 82 clinics
    "Dutchess": 0.185,      # 47 clinics
    "Rockland": 0.150,      # 38 clinics
    "Orange": 0.098,        # 25 clinics
    "Ulster": 0.094,        # 24 clinics
    "Albany": 0.059,        # 15 clinics
    "Columbia": 0.035,      # 9 clinics
    "Putnam": 0.031,        # 8 clinics
    "Rensselaer": 0.012,    # 3 clinics
    "Greene": 0.012,        # 3 clinics
}


@st.cache_data
def load_clinic_data():
    """
    Load real clinic data from CSV and add coordinates.
    """
    from pathlib import Path

    # Get the directory where this script is located (works on Streamlit Cloud)
    script_dir = Path(__file__).parent.resolve()
    filtered_path = script_dir / "hudson_valley_acupuncture_clinics_filtered.csv"
    raw_path = script_dir / "hudson_valley_acupuncture_clinics.csv"

    try:
        if filtered_path.exists():
            df = pd.read_csv(filtered_path)
        elif raw_path.exists():
            df = pd.read_csv(raw_path)
        else:
            st.error(f"CSV data file not found in {script_dir}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

    # Clean data
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["total_ratings"], errors="coerce").fillna(0).astype(int)
    df["county"] = df["search_county"]

    # Add coordinates based on address and search_city
    np.random.seed(42)  # For reproducible offsets

    def get_coordinates(row):
        address = str(row.get("address", "")).lower()
        city = str(row.get("search_city", "")).lower()
        county = str(row.get("search_county", ""))

        # Try to match town from address or search_city
        for county_name, county_info in COUNTY_DATA.items():
            for town_name, town_lat, town_lon in county_info["towns"]:
                if town_name.lower() in address or town_name.lower() == city:
                    # Add small random offset to prevent exact overlaps
                    lat_offset = np.random.uniform(-0.008, 0.008)
                    lon_offset = np.random.uniform(-0.008, 0.008)
                    return town_lat + lat_offset, town_lon + lon_offset

        # Fall back to county center if available
        if county in COUNTY_DATA:
            center = COUNTY_DATA[county]["center"]
            spread = COUNTY_DATA[county]["spread"]
            lat_offset = np.random.uniform(-spread[0]/2, spread[0]/2)
            lon_offset = np.random.uniform(-spread[1]/2, spread[1]/2)
            return center[0] + lat_offset, center[1] + lon_offset

        # Default to center of Hudson Valley
        return 41.5 + np.random.uniform(-0.1, 0.1), -73.9 + np.random.uniform(-0.1, 0.1)

    coords = df.apply(get_coordinates, axis=1)
    df["latitude"] = coords.apply(lambda x: x[0])
    df["longitude"] = coords.apply(lambda x: x[1])

    return df


def get_color_from_rating(rating):
    """
    Map rating to RGB color.
    5.0: Bright Green
    4.5-4.9: Light Green
    4.0-4.4: Yellow/Gold
    <4.0: Red/Orange
    """
    if rating >= 5.0:
        return [34, 197, 94, 220]      # Bright Green
    elif rating >= 4.5:
        return [134, 239, 172, 220]    # Light Green
    elif rating >= 4.0:
        return [250, 204, 21, 220]     # Gold/Yellow
    else:
        return [239, 68, 68, 220]      # Red


def create_3d_map(df, view_state):
    """
    Create PyDeck 3D visualization with ColumnLayer.
    Uses CARTO basemap - no Mapbox token required.
    """

    # Add color column based on rating
    df = df.copy()
    df["color"] = df["rating"].apply(get_color_from_rating)

    # Scale review count for column height
    df["elevation"] = df["review_count"] * 50

    # ColumnLayer for 3D bars - thin columns to see individual clinics
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=150,  # Thin columns to distinguish individual clinics
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # Create deck with CARTO basemap (no API key needed!)
    deck = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        map_style="road",  # CARTO road style - shows labels without Mapbox token
        tooltip={
            "html": """
                <div style="background: #1e293b; padding: 12px; border-radius: 8px;
                            font-family: system-ui; color: white; min-width: 200px;">
                    <div style="font-size: 14px; font-weight: bold; color: #38bdf8; margin-bottom: 8px;">
                        {name}
                    </div>
                    <div style="font-size: 12px; margin-bottom: 4px;">
                        <b>County:</b> {county}
                    </div>
                    <div style="font-size: 12px; margin-bottom: 4px;">
                        <b>Rating:</b> {rating} / 5.0
                    </div>
                    <div style="font-size: 12px;">
                        <b>Reviews:</b> {review_count}
                    </div>
                </div>
            """,
            "style": {
                "backgroundColor": "transparent",
                "color": "white"
            }
        }
    )

    return deck


def main():
    # Title
    st.title("Hudson Valley Acupuncture Market Analyzer")
    st.markdown("""
    **3D visualization of market saturation and competitor dominance.**
    Taller columns = more reviews (established competitors). Color = rating quality.
    """)

    # Load real clinic data from CSV
    st.write("Loading data...")  # Debug
    df = load_clinic_data()
    st.write(f"Loaded {len(df)} rows")  # Debug

    if df.empty:
        st.error("No data loaded - check CSV file")
        st.stop()

    # === SIDEBAR FILTERS ===
    st.sidebar.header("Filters")

    # County filter
    all_counties = ["All Counties"] + sorted(df["county"].unique().tolist())
    selected_county = st.sidebar.selectbox(
        "Select County",
        options=all_counties,
        index=0
    )

    # Minimum rating filter
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=3.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )

    # Max reviews filter (to find market gaps)
    max_reviews = st.sidebar.slider(
        "Max Review Count",
        min_value=10,
        max_value=400,
        value=400,
        step=10,
        help="Lower this to find areas with less established competitors"
    )

    # Apply filters
    filtered_df = df.copy()
    if selected_county != "All Counties":
        filtered_df = filtered_df[filtered_df["county"] == selected_county]
    filtered_df = filtered_df[filtered_df["rating"] >= min_rating]
    filtered_df = filtered_df[filtered_df["review_count"] <= max_reviews]

    # === SUMMARY METRICS ===
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Clinics", len(filtered_df))
    with col2:
        avg_rating = filtered_df["rating"].mean() if len(filtered_df) > 0 else 0
        st.metric("Avg Rating", f"{avg_rating:.2f}")
    with col3:
        avg_reviews = filtered_df["review_count"].mean() if len(filtered_df) > 0 else 0
        st.metric("Avg Reviews", f"{avg_reviews:.1f}")
    with col4:
        total_reviews = filtered_df["review_count"].sum()
        st.metric("Total Reviews", f"{total_reviews:,}")

    # === COLOR LEGEND ===
    st.sidebar.markdown("---")
    st.sidebar.subheader("Color Legend")
    st.sidebar.markdown("""
    - 🟢 **Bright Green**: Rating 5.0
    - 🟢 **Light Green**: Rating 4.5-4.9
    - 🟡 **Gold**: Rating 4.0-4.4
    - 🔴 **Red**: Rating < 4.0
    """)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Height = Reviews")
    st.sidebar.markdown("""
    Taller columns indicate clinics with more Google reviews,
    representing **market dominance**.

    Look for areas with **short columns** to find potential market gaps.
    """)

    # === 3D MAP ===
    st.subheader("Competitor Landscape")

    # Camera controls
    col1, col2, col3 = st.columns(3)
    with col1:
        pitch = st.slider("Camera Tilt", 0, 75, 55)
    with col2:
        bearing = st.slider("Rotation", -180, 180, 15)
    with col3:
        zoom = st.slider("Zoom", 7.0, 11.0, 8.0, step=0.5)

    # Calculate view center based on filtered data
    if len(filtered_df) > 0:
        center_lat = filtered_df["latitude"].mean()
        center_lon = filtered_df["longitude"].mean()
    else:
        center_lat = 41.5
        center_lon = -73.9

    # Create view state - looking "up the river" towards Albany
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=pitch,
        bearing=bearing
    )

    # Render map
    if len(filtered_df) > 0:
        deck = create_3d_map(filtered_df, view_state)
        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.warning("No clinics match the current filters.")

    # === DATA TABLES ===
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Market Leaders")
        st.markdown("*Highest review counts - established competitors*")
        top_clinics = filtered_df.nlargest(10, "review_count")[
            ["name", "county", "rating", "review_count"]
        ].reset_index(drop=True)
        top_clinics.columns = ["Clinic", "County", "Rating", "Reviews"]
        st.dataframe(top_clinics, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Market Opportunities")
        st.markdown("*Lowest review counts - potential gaps*")
        opportunities = filtered_df.nsmallest(10, "review_count")[
            ["name", "county", "rating", "review_count"]
        ].reset_index(drop=True)
        opportunities.columns = ["Clinic", "County", "Rating", "Reviews"]
        st.dataframe(opportunities, use_container_width=True, hide_index=True)

    # === COUNTY BREAKDOWN ===
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

    # === FOOTER ===
    st.markdown("---")
    st.caption("""
    **Data:** Real clinic data from Google Maps Places API search (hudson_valley_acupuncture_clinics_filtered.csv).
    **Visualization:** Column height = review count (market presence). Color = rating quality.
    **Strategy:** Look for areas with short columns (low competition) in desirable locations.
    """)


if __name__ == "__main__":
    main()
