import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="NFL Analytics Hub", layout="wide")

# 1. Team Data with Stats & Ticket Links
@st.cache_data
def load_team_data():
    data = [
        {"team": "Kansas City Chiefs", "abbr": "KC", "lat": 39.0489, "lon": -94.4839, "Off": 4, "Def": 2, "SOS": ".535", "TO": +8},
        {"team": "San Francisco 49ers", "abbr": "SF", "lat": 37.4033, "lon": -121.9694, "Off": 2, "Def": 5, "SOS": ".510", "TO": +7},
        {"team": "Baltimore Ravens", "abbr": "BAL", "lat": 39.2779, "lon": -76.6227, "Off": 2, "Def": 3, "SOS": ".524", "TO": +7},
        {"team": "Philadelphia Eagles", "abbr": "PHI", "lat": 39.9008, "lon": -75.1675, "Off": 11, "Def": 6, "SOS": ".498", "TO": +4},
        {"team": "Detroit Lions", "abbr": "DET", "lat": 42.3400, "lon": -83.0456, "Off": 1, "Def": 10, "SOS": ".510", "TO": +6},
        {"team": "Pittsburgh Steelers", "abbr": "PIT", "lat": 40.4468, "lon": -80.0158, "Off": 23, "Def": 1, "SOS": ".545", "TO": +6},
        # Add all 32 teams here
    ]
    df = pd.DataFrame(data)
    df["logo_url"] = df["abbr"].apply(lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png")
    # Generate dynamic ticket link
    df["ticket_link"] = df["team"].apply(lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets")
    return df

df_teams = load_team_data()

# 2. State Sync Logic
if "selected_team" not in st.session_state:
    st.session_state.selected_team = df_teams["team"].iloc[0]

# 3. Sidebar UI
st.sidebar.title("NFL Analytics & Tickets")
selected_name = st.sidebar.selectbox("Select Team", df_teams["team"].tolist(), 
                                     index=df_teams["team"].tolist().index(st.session_state.selected_team),
                                     key="team_dropdown")

# Update state if dropdown changes
if st.session_state.team_dropdown != st.session_state.selected_team:
    st.session_state.selected_team = st.session_state.team_dropdown
    st.rerun()

team_row = df_teams[df_teams["team"] == st.session_state.selected_team].iloc[0]

# Display Stats & Tickets
st.sidebar.markdown(f"### {team_row['team']} Analytics")
st.sidebar.metric("Offensive Rank", f"#{team_row['Off']")
st.sidebar.metric("Defensive Rank", f"#{team_row['Def']}")
st.sidebar.metric("Turnover Margin", f"{team_row['TO']:+d}")
st.sidebar.link_button("🎟️ Get Tickets", team_row['ticket_link'])

# 4. Map Generation
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
    # Use a FeatureGroup to make interaction clearer
    icon = folium.CustomIcon(row['logo_url'], icon_size=(40, 40))
    marker = folium.Marker(
        location=[row['lat'], row['lon']], 
        icon=icon, 
        tooltip=row['team'],
        # Use an ID (abbr) for robust click capture
        popup=row['team']
    )
    marker.add_to(m)

# 5. Render Map & Capture Clicks
output = st_folium(m, width=900, height=500)

# Capture clicks on map
if output["last_object_clicked_tooltip"]:
    clicked_name = output["last_object_clicked_tooltip"]
    if clicked_name != st.session_state.selected_team:
        st.session_state.selected_team = clicked_name
        st.rerun()