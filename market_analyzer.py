"""
Hudson Valley Acupuncture Market Analyzer
A Streamlit application for visualizing market saturation and competitor dominance
using 3D PyDeck visualization.
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

# Hudson Valley town coordinates (approximate centers)
TOWN_COORDINATES = {
    # Westchester County
    "yonkers": (40.9312, -73.8987),
    "hastings-on-hudson": (40.9926, -73.8787),
    "hastings on hudson": (40.9926, -73.8787),
    "dobbs ferry": (41.0145, -73.8726),
    "irvington": (41.0393, -73.8685),
    "tarrytown": (41.0762, -73.8585),
    "sleepy hollow": (41.0859, -73.8585),
    "ossining": (41.1626, -73.8615),
    "croton-on-hudson": (41.2084, -73.8912),
    "croton on hudson": (41.2084, -73.8912),
    "peekskill": (41.2901, -73.9204),
    "white plains": (41.0340, -73.7629),
    "scarsdale": (40.9887, -73.7846),
    "bronxville": (40.9382, -73.8321),
    "eastchester": (40.9582, -73.8088),
    "tuckahoe": (40.9501, -73.8277),
    "hartsdale": (41.0190, -73.7985),
    "ardsley": (41.0109, -73.8438),
    "elmsford": (41.0551, -73.8201),
    "mt vernon": (40.9126, -73.8371),
    "mount vernon": (40.9126, -73.8371),
    "new rochelle": (40.9115, -73.7824),
    "mamaroneck": (40.9487, -73.7324),
    "larchmont": (40.9276, -73.7518),
    "mt kisco": (41.2048, -73.7268),
    "mount kisco": (41.2048, -73.7268),
    "chappaqua": (41.1598, -73.7651),
    "somers": (41.2548, -73.7151),
    "yorktown heights": (41.2709, -73.7776),
    "riverdale": (40.8968, -73.9143),
    "bronx": (40.8448, -73.8648),

    # Rockland County
    "nyack": (41.0907, -73.9179),
    "upper nyack": (41.1057, -73.9229),
    "piermont": (41.0410, -73.9185),
    "haverstraw": (41.1976, -73.9643),
    "stony point": (41.2293, -73.9871),
    "new city": (41.1476, -74.0135),
    "nanuet": (41.0887, -74.0135),
    "spring valley": (41.1132, -74.0438),
    "suffern": (41.1148, -74.1493),
    "pearl river": (41.0587, -74.0218),
    "tappan": (41.0226, -73.9471),
    "orangeburg": (41.0476, -73.9487),
    "west nyack": (41.0957, -73.9713),
    "valley cottage": (41.1207, -73.9429),
    "pomona": (41.1657, -74.0438),
    "bardonia": (41.1087, -73.9935),
    "blauvelt": (41.0626, -73.9579),
    "chestnut ridge": (41.0826, -74.0535),

    # Putnam County
    "cold spring": (41.4201, -73.9546),
    "garrison": (41.3801, -73.9471),
    "brewster": (41.3973, -73.6168),
    "carmel hamlet": (41.4298, -73.6801),

    # Orange County
    "highland falls": (41.3693, -73.9635),
    "west point": (41.3915, -73.9571),
    "cornwall-on-hudson": (41.4426, -74.0135),
    "cornwall on hudson": (41.4426, -74.0135),
    "cornwall": (41.4426, -74.0135),
    "newburgh": (41.5034, -74.0104),
    "new windsor": (41.4737, -74.0235),
    "middletown": (41.4459, -74.4229),
    "monroe": (41.3307, -74.1868),
    "warwick": (41.2565, -74.3593),
    "goshen": (41.4015, -74.3243),
    "pine bush": (41.6082, -74.3010),
    "rock tavern": (41.4637, -74.1635),

    # Dutchess County
    "beacon": (41.5048, -73.9696),
    "fishkill": (41.5354, -73.8987),
    "wappingers falls": (41.5965, -73.9110),
    "poughkeepsie": (41.7004, -73.9210),
    "hyde park": (41.7843, -73.9332),
    "rhinebeck": (41.9265, -73.9129),
    "red hook": (41.9948, -73.8760),
    "tivoli": (42.0576, -73.9079),
    "pleasant valley": (41.7454, -73.8210),
    "hopewell junction": (41.5798, -73.8210),
    "millbrook": (41.7848, -73.6929),

    # Ulster County
    "highland": (41.7209, -73.9610),
    "milton": (41.6559, -73.9760),
    "marlboro": (41.6065, -73.9735),
    "kingston": (41.9270, -73.9974),
    "saugerties": (42.0776, -73.9529),
    "woodstock": (42.0409, -74.1182),
    "new paltz": (41.7465, -74.0868),
    "rosendale": (41.8498, -74.0785),
    "stone ridge": (41.8598, -74.1435),
    "phoenicia": (42.0826, -74.3085),
    "shady": (42.0509, -74.1485),
    "cairo": (42.2976, -74.0135),

    # Columbia County
    "hudson": (42.2526, -73.7907),
    "stuyvesant": (42.3826, -73.7307),
    "stockport": (42.3026, -73.7507),
    "ghent": (42.3326, -73.6507),
    "chatham": (42.3643, -73.5946),
    "kinderhook": (42.3943, -73.6907),
    "philmont": (42.2476, -73.6507),
    "germantown": (42.1326, -73.8807),
    "elizaville": (42.0826, -73.8007),

    # Greene County
    "catskill": (42.2176, -73.8607),
    "athens": (42.2593, -73.8079),
    "coxsackie": (42.3509, -73.8029),
    "windham": (42.3076, -74.2507),
    "greenville": (42.4143, -74.0035),

    # Albany County
    "albany": (42.6526, -73.7562),
    "coeymans": (42.4743, -73.7929),
    "ravena": (42.4676, -73.8135),
    "delmar": (42.6193, -73.8335),
    "latham": (42.7476, -73.7535),
    "guilderland": (42.6876, -73.9035),
    "loudonville": (42.7026, -73.7635),
    "colonie": (42.7176, -73.8335),

    # Rensselaer County
    "rensselaer": (42.6426, -73.7362),
    "castleton-on-hudson": (42.5326, -73.7507),
    "castleton on hudson": (42.5326, -73.7507),
    "troy": (42.7284, -73.6918),
    "clifton park": (42.8576, -73.7935),

    # Long Island / NYC areas (some clinics listed with these)
    "long island city": (40.7447, -73.9485),
    "new hyde park": (40.7351, -73.6879),
    "north new hyde park": (40.7451, -73.6879),
    "syosset": (40.8265, -73.5018),
    "rochester": (43.1566, -77.6088),
    "rye": (40.9807, -73.6835),
}


def get_coordinates(address, search_city):
    """Extract coordinates based on address or search city."""
    address_lower = address.lower()
    city_lower = search_city.lower()

    # Try to find coordinates from address first
    for town, coords in TOWN_COORDINATES.items():
        if town in address_lower:
            # Add small random offset to prevent exact overlaps
            lat_offset = np.random.uniform(-0.008, 0.008)
            lon_offset = np.random.uniform(-0.008, 0.008)
            return coords[0] + lat_offset, coords[1] + lon_offset

    # Fall back to search city
    if city_lower in TOWN_COORDINATES:
        lat_offset = np.random.uniform(-0.01, 0.01)
        lon_offset = np.random.uniform(-0.01, 0.01)
        coords = TOWN_COORDINATES[city_lower]
        return coords[0] + lat_offset, coords[1] + lon_offset

    # Default to center of Hudson Valley if no match
    return 41.5 + np.random.uniform(-0.1, 0.1), -73.9 + np.random.uniform(-0.1, 0.1)


def load_and_process_data():
    """Load the CSV data and add coordinates."""
    try:
        df = pd.read_csv("hudson_valley_acupuncture_clinics_filtered.csv")
    except FileNotFoundError:
        df = pd.read_csv("hudson_valley_acupuncture_clinics.csv")

    # Clean the data
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['total_ratings'] = pd.to_numeric(df['total_ratings'], errors='coerce').fillna(0).astype(int)

    # Add coordinates
    coords = df.apply(lambda row: get_coordinates(row['address'], row['search_city']), axis=1)
    df['latitude'] = coords.apply(lambda x: x[0])
    df['longitude'] = coords.apply(lambda x: x[1])

    # Add color based on rating
    def get_color(rating):
        if pd.isna(rating):
            return [128, 128, 128, 200]  # Gray for no rating
        elif rating >= 4.9:
            return [34, 139, 34, 220]     # Forest green for excellent
        elif rating >= 4.5:
            return [144, 238, 144, 220]   # Light green for very good
        elif rating >= 4.0:
            return [255, 215, 0, 220]     # Gold for good
        else:
            return [255, 99, 71, 220]     # Tomato red for lower

    df['color'] = df['rating'].apply(get_color)

    # Normalize review count for elevation (cap at 400 for visualization)
    df['elevation'] = df['total_ratings'].clip(upper=400) * 15

    return df


def create_deck_map(df, view_state):
    """Create the PyDeck 3D map visualization."""

    # Column layer for 3D bars
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=300,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # Scatterplot layer for base markers
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color=[255, 255, 255, 100],
        get_radius=150,
        pickable=True,
    )

    # Create the deck
    deck = pdk.Deck(
        layers=[column_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={
            "html": """
                <div style="background-color: #1a1a2e; padding: 10px; border-radius: 5px; color: white;">
                    <b style="color: #00d4ff;">{name}</b><br/>
                    <b>Location:</b> {search_city}, {search_county} County<br/>
                    <b>Rating:</b> {rating} / 5.0<br/>
                    <b>Reviews:</b> {total_ratings}<br/>
                    <b>Status:</b> {business_status}
                </div>
            """,
            "style": {
                "backgroundColor": "#1a1a2e",
                "color": "white",
                "border": "1px solid #00d4ff"
            }
        }
    )

    return deck


def main():
    # Title and description
    st.title("Hudson Valley Acupuncture Market Analyzer")
    st.markdown("""
    **Strategic market intelligence for practitioners planning a business location.**

    This 3D visualization shows competitor dominance across the Hudson River Valley.
    **Taller columns = more established competitors** (more reviews). Use this to identify market gaps.
    """)

    # Load data
    np.random.seed(42)  # For reproducible coordinate offsets
    df = load_and_process_data()

    # Sidebar filters
    st.sidebar.header("Market Opportunity Filters")

    # Review count filter
    max_reviews = st.sidebar.slider(
        "Max Competitor Review Count",
        min_value=0,
        max_value=400,
        value=400,
        step=10,
        help="Filter to show only clinics with reviews below this threshold. Lower values reveal potential market gaps."
    )

    # County filter
    all_counties = sorted(df['search_county'].unique())
    selected_counties = st.sidebar.multiselect(
        "Select Counties",
        options=all_counties,
        default=all_counties,
        help="Focus on specific counties in the Hudson Valley"
    )

    # Rating filter
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.5,
        help="Filter clinics by minimum rating"
    )

    # Apply filters
    filtered_df = df[
        (df['total_ratings'] <= max_reviews) &
        (df['search_county'].isin(selected_counties)) &
        ((df['rating'] >= min_rating) | (df['rating'].isna()))
    ].copy()

    # Sidebar metrics
    st.sidebar.markdown("---")
    st.sidebar.header("Strategic Metrics")

    col1, col2 = st.sidebar.columns(2)
    col1.metric("Visible Clinics", len(filtered_df))
    col2.metric("Total in Region", len(df))

    if len(filtered_df) > 0:
        avg_reviews = filtered_df['total_ratings'].mean()
        avg_rating = filtered_df['rating'].mean()
        st.sidebar.metric("Avg Reviews (Filtered)", f"{avg_reviews:.1f}")
        st.sidebar.metric("Avg Rating (Filtered)", f"{avg_rating:.2f}")

    # County breakdown
    st.sidebar.markdown("---")
    st.sidebar.subheader("Clinics by County")
    county_counts = filtered_df['search_county'].value_counts()
    for county, count in county_counts.items():
        avg_rev = filtered_df[filtered_df['search_county'] == county]['total_ratings'].mean()
        st.sidebar.text(f"{county}: {count} clinics (avg {avg_rev:.0f} reviews)")

    # Color legend
    st.sidebar.markdown("---")
    st.sidebar.subheader("Color Legend")
    st.sidebar.markdown("""
    - 🟢 **Dark Green**: Rating 4.9-5.0 (Excellent)
    - 🟢 **Light Green**: Rating 4.5-4.8 (Very Good)
    - 🟡 **Gold**: Rating 4.0-4.4 (Good)
    - 🔴 **Red**: Rating < 4.0 (Lower)
    - ⚪ **Gray**: No rating data
    """)

    # Main map area
    st.subheader("Competitor Landscape Map")

    # View state options
    col1, col2, col3 = st.columns(3)
    with col1:
        pitch = st.slider("Camera Pitch", 0, 80, 60, help="Tilt angle of the view")
    with col2:
        bearing = st.slider("Camera Bearing", -180, 180, 15, help="Rotation of the view")
    with col3:
        zoom = st.slider("Zoom Level", 7.0, 12.0, 8.5, step=0.5)

    # Calculate center based on filtered data
    if len(filtered_df) > 0:
        center_lat = filtered_df['latitude'].mean()
        center_lon = filtered_df['longitude'].mean()
    else:
        center_lat = 41.5
        center_lon = -73.9

    # Create view state
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=pitch,
        bearing=bearing
    )

    # Create and display map
    if len(filtered_df) > 0:
        deck = create_deck_map(filtered_df, view_state)
        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.warning("No clinics match the current filter criteria.")

    # Data insights section
    st.markdown("---")
    st.subheader("Market Opportunity Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 10 Most Established Competitors")
        top_competitors = filtered_df.nlargest(10, 'total_ratings')[
            ['name', 'search_city', 'search_county', 'rating', 'total_ratings']
        ].rename(columns={
            'name': 'Clinic',
            'search_city': 'City',
            'search_county': 'County',
            'rating': 'Rating',
            'total_ratings': 'Reviews'
        })
        st.dataframe(top_competitors, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Potential Market Gaps (Fewest Reviews)")
        market_gaps = filtered_df[filtered_df['total_ratings'] > 0].nsmallest(10, 'total_ratings')[
            ['name', 'search_city', 'search_county', 'rating', 'total_ratings']
        ].rename(columns={
            'name': 'Clinic',
            'search_city': 'City',
            'search_county': 'County',
            'rating': 'Rating',
            'total_ratings': 'Reviews'
        })
        st.dataframe(market_gaps, use_container_width=True, hide_index=True)

    # County saturation analysis
    st.markdown("---")
    st.subheader("County Saturation Analysis")

    county_analysis = filtered_df.groupby('search_county').agg({
        'name': 'count',
        'total_ratings': ['mean', 'sum'],
        'rating': 'mean'
    }).round(2)
    county_analysis.columns = ['Clinic Count', 'Avg Reviews', 'Total Reviews', 'Avg Rating']
    county_analysis = county_analysis.sort_values('Clinic Count', ascending=False)

    st.dataframe(county_analysis, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption("""
    **Data Source:** Google Maps Places API search for acupuncture and Chinese medicine providers in the Hudson River Valley.
    **Visualization:** Column height represents review count (market presence). Color represents rating quality.
    **Strategy:** Look for areas with short columns (low review counts) but high demand potential.
    """)


if __name__ == "__main__":
    main()
