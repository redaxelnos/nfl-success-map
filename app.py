import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="NFL Analytics Hub", layout="wide")

# 1. Complete 32-Team Dataset with Stats & Ticket Links
@st.cache_data
def load_team_data():
    data = [
        {"team": "Arizona Cardinals", "abbr": "ARI", "lat": 33.5276, "lon": -112.2626, "Off": 18, "Def": 22, "SOS": ".512", "TO": -2},
        {"team": "Atlanta Falcons", "abbr": "ATL", "lat": 33.7554, "lon": -84.4010, "Off": 14, "Def": 16, "SOS": ".485", "TO": +1},
        {"team": "Baltimore Ravens", "abbr": "BAL", "lat": 39.2779, "lon": -76.6227, "Off": 2, "Def": 3, "SOS": ".524", "TO": +7},
        {"team": "Buffalo Bills", "abbr": "BUF", "lat": 42.7738, "lon": -78.7870, "Off": 3, "Def": 8, "SOS": ".508", "TO": +5},
        {"team": "Carolina Panthers", "abbr": "CAR", "lat": 35.2258, "lon": -80.8528, "Off": 30, "Def": 31, "SOS": ".492", "TO": -9},
        {"team": "Chicago Bears", "abbr": "CHI", "lat": 41.8623, "lon": -87.6167, "Off": 20, "Def": 12, "SOS": ".478", "TO": 0},
        {"team": "Cincinnati Bengals", "abbr": "CIN", "lat": 39.0955, "lon": -84.5160, "Off": 6, "Def": 19, "SOS": ".531", "TO": +3},
        {"team": "Cleveland Browns", "abbr": "CLE", "lat": 41.5061, "lon": -81.6995, "Off": 22, "Def": 4, "SOS": ".542", "TO": -4},
        {"team": "Dallas Cowboys", "abbr": "DAL", "lat": 32.7473, "lon": -97.0945, "Off": 5, "Def": 11, "SOS": ".495", "TO": +4},
        {"team": "Denver Broncos", "abbr": "DEN", "lat": 39.7439, "lon": -105.0201, "Off": 24, "Def": 15, "SOS": ".515", "TO": -1},
        {"team": "Detroit Lions", "abbr": "DET", "lat": 42.3400, "lon": -83.0456, "Off": 1, "Def": 10, "SOS": ".510", "TO": +6},
        {"team": "Green Bay Packers", "abbr": "GB", "lat": 44.5013, "lon": -88.0622, "Off": 8, "Def": 13, "SOS": ".502", "TO": +3},
        {"team": "Houston Texans", "abbr": "HOU", "lat": 29.6847, "lon": -95.4107, "Off": 9, "Def": 9, "SOS": ".488", "TO": +5},
        {"team": "Indianapolis Colts", "abbr": "IND", "lat": 39.7601, "lon": -86.1639, "Off": 17, "Def": 21, "SOS": ".490", "TO": -1},
        {"team": "Jacksonville Jaguars", "abbr": "JAX", "lat": 30.3239, "lon": -81.6373, "Off": 16, "Def": 20, "SOS": ".500", "TO": 0},
        {"team": "Kansas City Chiefs", "abbr": "KC", "lat": 39.0489, "lon": -94.4839, "Off": 4, "Def": 2, "SOS": ".535", "TO": +8},
        {"team": "Las Vegas Raiders", "abbr": "LV", "lat": 36.0909, "lon": -115.1833, "Off": 27, "Def": 14, "SOS": ".520", "TO": -3},
        {"team": "Los Angeles Chargers", "abbr": "LAC", "lat": 33.9535, "lon": -118.3390, "Off": 15, "Def": 7, "SOS": ".475", "TO": +2},
        {"team": "Los Angeles Rams", "abbr": "LAR", "lat": 33.9535, "lon": -118.3390, "Off": 7, "Def": 18, "SOS": ".512", "TO": +1},
        {"team": "Miami Dolphins", "abbr": "MIA", "lat": 25.9580, "lon": -80.2389, "Off": 10, "Def": 17, "SOS": ".482", "TO": +2},
        {"team": "Minnesota Vikings", "abbr": "MIN", "lat": 44.9738, "lon": -93.2575, "Off": 19, "Def": 16, "SOS": ".505", "TO": 0},
        {"team": "New England Patriots", "abbr": "NE", "lat": 42.0909, "lon": -71.2643, "Off": 31, "Def": 25, "SOS": ".518", "TO": -6},
        {"team": "New Orleans Saints", "abbr": "NO", "lat": 29.9511, "lon": -90.0812, "Off": 13, "Def": 23, "SOS": ".470", "TO": +1},
        {"team": "New York Giants", "abbr": "NYG", "lat": 40.8135, "lon": -74.0744, "Off": 28, "Def": 26, "SOS": ".525", "TO": -5},
        {"team": "New York Jets", "abbr": "NYJ", "lat": 40.8135, "lon": -74.0744, "Off": 21, "Def": 5, "SOS": ".502", "TO": +2},
        {"team": "Philadelphia Eagles", "abbr": "PHI", "lat": 39.9008, "lon": -75.1675, "Off": 11, "Def": 6, "SOS": ".498", "TO": +4},
        {"team": "Pittsburgh Steelers", "abbr": "PIT", "lat": 40.4468, "lon": -80.0158, "Off": 23, "Def": 1, "SOS": ".545", "TO": +6},
        {"team": "San Francisco 49ers", "abbr": "SF", "lat": 37.4033, "lon": -121.9694, "Off": 2, "Def": 5, "SOS": ".510", "TO": +7},
        {"team": "Seattle Seahawks", "abbr": "SEA", "lat": 47.5952, "lon": -122.3316, "Off": 12, "Def": 24, "SOS": ".492", "TO": 0},
        {"team": "Tampa Bay Buccaneers", "abbr": "TB", "lat": 27.9759, "lon": -82.5033, "Off": 17, "Def": 22, "SOS": ".488", "TO": +2},
        {"team": "Tennessee Titans", "abbr": "TEN", "lat": 36.1665, "lon": -86.7713, "Off": 29, "Def": 27, "SOS": ".515", "TO": -4},
        {"team": "Washington Commanders", "abbr": "WAS", "lat": 38.9076, "lon": -76.8645, "Off": 25, "Def": 28, "SOS": ".485", "TO": -2},
    ]
    df = pd.DataFrame(data)
    df["logo_url"] = df["abbr"].apply(lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png")
    df["ticket_link"] = df["team"].apply(lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets")
    return df

df_teams = load_team_data()

# 2. State Sync Logic
if "selected_team" not in st.session_state:
    st.session_state.selected_team = "Kansas City Chiefs"

team_names = df_teams["team"].tolist()

# 3. Sidebar UI
st.sidebar.title("NFL Analytics & Tickets")
selected_name = st.sidebar.selectbox("Select Team", team_names, 
                                     index=team_names.index(st.session_state.selected_team),
                                     key="team_dropdown")

# Update state if dropdown changes
if st.session_state.team_dropdown != st.session_state.selected_team:
    st.session_state.selected_team = st.session_state.team_dropdown
    st.rerun()

team_row = df_teams[df_teams["team"] == st.session_state.selected_team].iloc[0]

# Display Stats & Tickets
st.sidebar.markdown(f"### {team_row['team']} Analytics")
st.sidebar.metric("Offensive Rank", f"#{team_row['Off']}")
st.sidebar.metric("Defensive Rank", f"#{team_row['Def']}")
st.sidebar.metric("Turnover Margin", f"{team_row['TO']:+d}")
st.sidebar.metric("Strength of Schedule", team_row['SOS'])
st.sidebar.link_button("🎟️ Get Tickets", team_row['ticket_link'])

# 4. Build GeoJSON structure for robust click handling
features = []
for _, row in df_teams.iterrows():
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [row["lon"], row["lat"]]},
        "properties": {
            "team": row["team"],
            "abbr": row["abbr"],
            "logo_url": row["logo_url"]
        }
    }
    features.append(feature)

geojson_data = {"type": "FeatureCollection", "features": features}

# 5. Generate Map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

folium.GeoJson(
    geojson_data,
    marker_function=lambda feature, latlng: folium.Marker(
        location=latlng,
        icon=folium.CustomIcon(feature["properties"]["logo_url"], icon_size=(35, 35)),
        tooltip=feature["properties"]["team"]
    )
).add_to(m)

# 6. Render Map & Capture Reliable Clicks
output = st_folium(m, width=900, height=500, key="geojson_map")

# Capture clicks on GeoJson properties
if output and output.get("last_object_clicked"):
    props = output["last_object_clicked"].get("properties")
    if props and "team" in props:
        clicked_name = props["team"]
        if clicked_name != st.session_state.selected_team:
            st.session_state.selected_team = clicked_name
            st.rerun()