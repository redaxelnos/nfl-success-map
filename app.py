import os
import math
import requests
import folium
import nfl_data_py as nfl
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Official NFL Matchup, Travel & Vitals Hub", 
    layout="wide"
)

st.title("Official NFL Schedule, Distance Travel & Intelligence Hub")
st.markdown(
    "**Click any team's logo on the map** or use the dropdown in the sidebar to inspect "
    "official schedules, stadium facility profiles, exact travel distances, team news vitals, and "
    "interactive what-if simulation sliders."
)

# 1. Complete 32-Team Dataset with Official Baseline SOS & Dynamic Integration
def load_team_data():
    data = [
        {"team": "Arizona Cardinals", "abbr": "ARI", "lat": 33.5276, "lon": -112.2626, "stadium": "State Farm Stadium", "surface": "Bermuda Grass", "roof": "Retractable Roof", "capacity": 63400, "Off": 18, "Def": 22, "SOS": ".536", "TO": -2, "BasePlayoff": 32.0, "Rating": 1500},
        {"team": "Atlanta Falcons", "abbr": "ATL", "lat": 33.7554, "lon": -84.4010, "stadium": "Mercedes-Benz Stadium", "surface": "FieldTurf CORE", "roof": "Retractable Roof", "capacity": 71000, "Off": 14, "Def": 16, "SOS": ".519", "TO": +1, "BasePlayoff": 45.0, "Rating": 1520},
        {"team": "Baltimore Ravens", "abbr": "BAL", "lat": 39.2779, "lon": -76.6227, "stadium": "M&T Bank Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 71008, "Off": 2, "Def": 3, "SOS": ".529", "TO": +7, "BasePlayoff": 82.0, "Rating": 1620},
        {"team": "Buffalo Bills", "abbr": "BUF", "lat": 42.7738, "lon": -78.7870, "stadium": "Highmark Stadium", "surface": "A-Turf Titan", "roof": "Open / Outdoor", "capacity": 71608, "Off": 3, "Def": 8, "SOS": ".467", "TO": +5, "BasePlayoff": 78.0, "Rating": 1610},
        {"team": "Carolina Panthers", "abbr": "CAR", "lat": 35.2258, "lon": -80.8528, "stadium": "Bank of America Stadium", "surface": "FieldTurf", "roof": "Open / Outdoor", "capacity": 74867, "Off": 30, "Def": 31, "SOS": ".498", "TO": -9, "BasePlayoff": 18.0, "Rating": 1470},
        {"team": "Chicago Bears", "abbr": "CHI", "lat": 41.8623, "lon": -87.6167, "stadium": "Soldier Field", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 61500, "Off": 20, "Def": 12, "SOS": ".554", "TO": 0, "BasePlayoff": 40.0, "Rating": 1510},
        {"team": "Cincinnati Bengals", "abbr": "CIN", "lat": 39.0955, "lon": -84.5160, "stadium": "Paycor Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 65515, "Off": 6, "Def": 19, "SOS": ".478", "TO": +3, "BasePlayoff": 68.0, "Rating": 1580},
        {"team": "Cleveland Browns", "abbr": "CLE", "lat": 41.5061, "lon": -81.6995, "stadium": "Huntington Bank Field", "surface": "Kentucky Bluegrass", "roof": "Open / Outdoor", "capacity": 67431, "Off": 22, "Def": 4, "SOS": ".536", "TO": -4, "BasePlayoff": 48.0, "Rating": 1530},
        {"team": "Dallas Cowboys", "abbr": "DAL", "lat": 32.7473, "lon": -97.0945, "stadium": "AT&T Stadium", "surface": "Matrix Helix Turf", "roof": "Retractable Roof", "capacity": 80000, "Off": 5, "Def": 11, "SOS": ".522", "TO": +4, "BasePlayoff": 72.0, "Rating": 1590},
        {"team": "Denver Broncos", "abbr": "DEN", "lat": 39.7439, "lon": -105.0201, "stadium": "Empower Field at Mile High", "surface": "Kentucky Bluegrass", "roof": "Open / Outdoor", "capacity": 76125, "Off": 24, "Def": 15, "SOS": ".502", "TO": -1, "BasePlayoff": 35.0, "Rating": 1505},
        {"team": "Detroit Lions", "abbr": "DET", "lat": 42.3400, "lon": -83.0456, "stadium": "Ford Field", "surface": "FieldTurf CORE", "roof": "Fixed Dome", "capacity": 65000, "Off": 1, "Def": 10, "SOS": ".516", "TO": +6, "BasePlayoff": 75.0, "Rating": 1600},
        {"team": "Green Bay Packers", "abbr": "GB", "lat": 44.5013, "lon": -88.0622, "stadium": "Lambeau Field", "surface": "SISGrass Hybrid", "roof": "Open / Outdoor", "capacity": 81441, "Off": 8, "Def": 13, "SOS": ".533", "TO": +3, "BasePlayoff": 70.0, "Rating": 1585},
        {"team": "Houston Texans", "abbr": "HOU", "lat": 29.6847, "lon": -95.4107, "stadium": "NRG Stadium", "surface": "Matrix Turf", "roof": "Retractable Roof", "capacity": 72220, "Off": 9, "Def": 9, "SOS": ".481", "TO": +5, "BasePlayoff": 65.0, "Rating": 1575},
        {"team": "Indianapolis Colts", "abbr": "IND", "lat": 39.7601, "lon": -86.1639, "stadium": "Lucas Oil Stadium", "surface": "Shaw Sports Turf", "roof": "Retractable Roof", "capacity": 67000, "Off": 17, "Def": 21, "SOS": ".457", "TO": -1, "BasePlayoff": 42.0, "Rating": 1515},
        {"team": "Jacksonville Jaguars", "abbr": "JAX", "lat": 30.3239, "lon": -81.6373, "stadium": "EverBank Stadium", "surface": "Tifway 419 Bermuda", "roof": "Open / Outdoor", "capacity": 67814, "Off": 16, "Def": 20, "SOS": ".478", "TO": 0, "BasePlayoff": 46.0, "Rating": 1525},
        {"team": "Kansas City Chiefs", "abbr": "KC", "lat": 39.0489, "lon": -94.4839, "stadium": "GEHA Field at Arrowhead", "surface": "Latitude 36 Bermuda", "roof": "Open / Outdoor", "capacity": 76416, "Off": 4, "Def": 2, "SOS": ".488", "TO": +8, "BasePlayoff": 92.0, "Rating": 1650},
        {"team": "Las Vegas Raiders", "abbr": "LV", "lat": 36.0909, "lon": -115.1833, "stadium": "Allegiant Stadium", "surface": "Bermuda Grass", "roof": "Fixed Dome", "capacity": 65000, "Off": 27, "Def": 14, "SOS": ".540", "TO": -3, "BasePlayoff": 28.0, "Rating": 1495},
        {"team": "Los Angeles Chargers", "abbr": "LAC", "lat": 33.9535, "lon": -118.3390, "stadium": "SoFi Stadium", "surface": "Matrix Turf", "roof": "Fixed Translucent Canopy", "capacity": 70240, "Off": 15, "Def": 7, "SOS": ".467", "TO": +2, "BasePlayoff": 55.0, "Rating": 1550},
        {"team": "Los Angeles Rams", "abbr": "LAR", "lat": 33.9535, "lon": -118.3390, "stadium": "SoFi Stadium", "surface": "Matrix Turf", "roof": "Fixed Translucent Canopy", "capacity": 70240, "Off": 7, "Def": 18, "SOS": ".505", "TO": +1, "BasePlayoff": 62.0, "Rating": 1565},
        {"team": "Miami Dolphins", "abbr": "MIA", "lat": 25.9580, "lon": -80.2389, "stadium": "Hard Rock Stadium", "surface": "Tifway 419 Bermuda", "roof": "Open / Canopy", "capacity": 65326, "Off": 10, "Def": 17, "SOS": ".419", "TO": +2, "BasePlayoff": 64.0, "Rating": 1570},
        {"team": "Minnesota Vikings", "abbr": "MIN", "lat": 44.9738, "lon": -93.2575, "stadium": "U.S. Bank Stadium", "surface": "Act Global Turf", "roof": "Fixed Translucent Roof", "capacity": 66860, "Off": 19, "Def": 16, "SOS": ".474", "TO": 0, "BasePlayoff": 48.0, "Rating": 1535},
        {"team": "New England Patriots", "abbr": "NE", "lat": 42.0909, "lon": -71.2643, "stadium": "Gillette Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 65878, "Off": 31, "Def": 25, "SOS": ".471", "TO": -6, "BasePlayoff": 22.0, "Rating": 1480},
        {"team": "New Orleans Saints", "abbr": "NO", "lat": 29.9511, "lon": -90.0812, "stadium": "Caesars Superdome", "surface": "FieldTurf Revolution", "roof": "Fixed Dome", "capacity": 73208, "Off": 13, "Def": 23, "SOS": ".505", "TO": +1, "BasePlayoff": 44.0, "Rating": 1520},
        {"team": "New York Giants", "abbr": "NYG", "lat": 40.8135, "lon": -74.0744, "stadium": "MetLife Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 82500, "Off": 28, "Def": 26, "SOS": ".554", "TO": -5, "BasePlayoff": 25.0, "Rating": 1485},
        {"team": "New York Jets", "abbr": "NYJ", "lat": 40.8135, "lon": -74.0744, "stadium": "MetLife Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 82500, "Off": 21, "Def": 5, "SOS": ".495", "TO": +2, "BasePlayoff": 52.0, "Rating": 1540},
        {"team": "Philadelphia Eagles", "abbr": "PHI", "lat": 39.9008, "lon": -75.1675, "stadium": "Lincoln Financial Field", "surface": "GrassMaster Hybrid", "roof": "Open / Outdoor", "capacity": 69796, "Off": 11, "Def": 6, "SOS": ".453", "TO": +4, "BasePlayoff": 73.0, "Rating": 1590},
        {"team": "Pittsburgh Steelers", "abbr": "PIT", "lat": 40.4468, "lon": -80.0158, "stadium": "Acrisure Stadium", "surface": "Kentucky Bluegrass", "roof": "Open / Outdoor", "capacity": 68400, "Off": 23, "Def": 1, "SOS": ".502", "TO": +6, "BasePlayoff": 58.0, "Rating": 1555},
        {"team": "San Francisco 49ers", "abbr": "SF", "lat": 37.4033, "lon": -121.9694, "stadium": "Levi's Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 68500, "Off": 2, "Def": 5, "SOS": ".564", "TO": +7, "BasePlayoff": 85.0, "Rating": 1630},
        {"team": "Seattle Seahawks", "abbr": "SEA", "lat": 47.5952, "lon": -122.3316, "stadium": "Lumen Field", "surface": "FieldTurf Revolution", "roof": "Open / Outdoor", "capacity": 68740, "Off": 12, "Def": 24, "SOS": ".498", "TO": 0, "BasePlayoff": 53.0, "Rating": 1545},
        {"team": "Tampa Bay Buccaneers", "abbr": "TB", "lat": 27.9759, "lon": -82.5033, "stadium": "Raymond James Stadium", "surface": "Tifway 419 Bermuda", "roof": "Open / Outdoor", "capacity": 69218, "Off": 17, "Def": 22, "SOS": ".502", "TO": +2, "BasePlayoff": 47.0, "Rating": 1530},
        {"team": "Tennessee Titans", "abbr": "TEN", "lat": 36.1665, "lon": -86.7713, "stadium": "Nissan Stadium", "surface": "Matrix Helix Turf", "roof": "Open / Outdoor", "capacity": 69143, "Off": 29, "Def": 27, "SOS": ".522", "TO": -4, "BasePlayoff": 26.0, "Rating": 1490},
        {"team": "Washington Commanders", "abbr": "WAS", "lat": 38.9076, "lon": -76.8645, "stadium": "Northwest Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 67617, "Off": 25, "Def": 28, "SOS": ".436", "TO": -2, "BasePlayoff": 38.0, "Rating": 1510},
    ]
    df = pd.DataFrame(data)
    
    rank_file = "team_rankings.csv"
    if os.path.exists(rank_file):
        try:
            rank_df = pd.read_csv(rank_file)
            df = df.drop(columns=['Off', 'Def', 'TO', 'SOS', 'Rating', 'BasePlayoff'], errors='ignore')
            df = df.merge(rank_df, on="abbr", how="left")
        except Exception:
            pass

    df["logo_url"] = df["abbr"].apply(
        lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png"
    )
    df["ticket_link"] = df["team"].apply(
        lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets"
    )
    return df

df_teams = load_team_data()
team_dict = df_teams.set_index("abbr").to_dict("index")

# 2. Mock Live News / Vitals Feed
@st.cache_data
def load_team_news():
    return {
        "KC": ["⚡ Practice Report: Full participation for offensive starters."],
        "SF": ["🏥 Injury Update: Star running back listed as limited in drills."]
    }
team_news = load_team_news()

# 3. Fetch Official Schedules
@st.cache_data
def load_official_schedules():
    try:
        sched_df = nfl.import_schedules([2026])
        return sched_df[sched_df["game_type"] == "REG"]
    except Exception:
        return pd.DataFrame()
official_schedule = load_official_schedules()

# 4. Fetch LIVE ESPN Data (Cached for 30 seconds to prevent rate limiting)
@st.cache_data(ttl=30)
def get_live_game_data(team_abbr):
    # Map abbreviation for ESPN (WAS is WSH in ESPN's system)
    espn_abbr = 'WSH' if team_abbr == 'WAS' else team_abbr
        
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        for event in data.get('events', []):
            competition = event['competitions'][0]
            competitors = competition['competitors']
            team_abbrs = [c['team']['abbreviation'] for c in competitors]
            
            if espn_abbr in team_abbrs:
                status = event['status']['type']['state']
                short_detail = event['status']['type']['shortDetail']
                
                home_team = competitors[0] if competitors[0]['homeAway'] == 'home' else competitors[1]
                away_team = competitors[1] if competitors[0]['homeAway'] == 'home' else competitors[0]
                
                game_info = {
                    'status': status,
                    'clock': short_detail,
                    'home_abbr': home_team['team']['abbreviation'],
                    'home_score': home_team.get('score', '0'),
                    'away_abbr': away_team['team']['abbreviation'],
                    'away_score': away_team.get('score', '0'),
                    'wp': None,
                    'possession': None
                }
                
                if status == 'in':
                    situation = competition.get('situation', {})
                    game_info['possession'] = situation.get('lastPlay', {}).get('text', 'Play in progress...')
                    
                    prob = situation.get('lastPlay', {}).get('probability', {})
                    if prob:
                        home_wp = prob.get('homeWinPercentage', 0.5)
                        away_wp = prob.get('awayWinPercentage', 0.5)
                        
                        if espn_abbr == home_team['team']['abbreviation']:
                            game_info['wp'] = round(home_wp * 100, 1)
                        else:
                            game_info['wp'] = round(away_wp * 100, 1)
                
                return game_info
    except Exception:
        pass
    return None

# 5. Haversine Distance Calculator
def calculate_travel_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

# State Initialization & Sidebar Sync
if "selected_team" not in st.session_state:
    st.session_state.selected_team = "Kansas City Chiefs"
team_names = df_teams["team"].tolist()

st.sidebar.title("Matchup & Vitals Hub")
current_index = team_names.index(st.session_state.selected_team)
selected_name = st.sidebar.selectbox("Select Team", team_names, index=current_index)

if selected_name != st.session_state.selected_team:
    st.session_state.selected_team = selected_name
    st.rerun()

team_df_row = df_teams[df_teams["team"] == st.session_state.selected_team].iloc[0]
selected_abbr = team_df_row["abbr"]

# Safe metric parsing
try:
    to_display = f"{int(float(team_df_row.get('TO', 0))):+d}"
    off_rank = f"#{int(float(team_df_row.get('Off', 1)))}"
    def_rank = f"#{int(float(team_df_row.get('Def', 1)))}"
except Exception:
    to_display, off_rank, def_rank = "0", "N/A", "N/A"

st.sidebar.markdown(f"### {st.session_state.selected_team} Profile")
st.sidebar.metric("Offensive Rank", off_rank)
st.sidebar.metric("Defensive Rank", def_rank)
st.sidebar.metric("Turnover Margin", to_display)
st.sidebar.metric("Strength of Schedule", str(team_df_row.get("SOS", ".500")))
st.sidebar.link_button("🎟️ Get Tickets", team_df_row["ticket_link"])

with st.sidebar.expander("🏟️ Stadium & Facility Profile", expanded=False):
    st.markdown(f"**Venue:** `{team_df_row.get('stadium', 'N/A')}`")
    st.markdown(f"**Capacity:** `{int(team_df_row.get('capacity', 0)):,} seats`")

# Sliding-Scale Variables
st.sidebar.markdown("---")
st.sidebar.subheader("Variable Impact Controls")
inj_val = st.sidebar.slider("Injury Attrition", 0, 10, 0)
wea_val = st.sidebar.slider("Weather Severity", 0, 10, 0)
trv_val = st.sidebar.slider("Travel Fatigue Multiplier", 0, 10, 0)

# Playoff Odds Engine
def calculate_adjusted_playoff(row, current_abbr, inj, wea, trv):
    base = float(row.get("BasePlayoff", 50.0))
    if row["abbr"] == current_abbr:
        return round(max(1.0, min(99.0, base - ((inj * 2.2) + (wea * 1.0) + (trv * 1.2)))), 1)
    return base

df_teams["adjusted_playoff"] = df_teams.apply(lambda row: calculate_adjusted_playoff(row, selected_abbr, inj_val, wea_val, trv_val), axis=1)
current_adjusted_score = df_teams.loc[df_teams["abbr"] == selected_abbr, "adjusted_playoff"].values[0]
st.sidebar.markdown(f"### 🎯 Adjusted Playoff Odds: {current_adjusted_score}%")

with st.sidebar.expander("🏈 Official Schedule & Travel Distance", expanded=False):
    if not official_schedule.empty:
        team_games = official_schedule[(official_schedule["home_team"] == selected_abbr) | (official_schedule["away_team"] == selected_abbr)]
        weeks = sorted(team_games["week"].unique().tolist())
        if weeks:
            selected_week = st.selectbox("Select Week", weeks)
            game = team_games[team_games["week"] == selected_week].iloc[0]
            is_home = (game["home_team"] == selected_abbr)
            opp_abbr = game["away_team"] if is_home else game["home_team"]
            st.markdown(f"**Opponent:** {opp_abbr} ({'Home' if is_home else 'Away'})")
            
            ml_file = "weekly_predictions.csv"
            used_ml = False
            if os.path.exists(ml_file):
                try:
                    ml_df = pd.read_csv(ml_file)
                    game_match = ml_df[(ml_df["week"] == selected_week) & ((ml_df["home_team"] == opp_abbr) | (ml_df["away_team"] == opp_abbr))]
                    if not game_match.empty:
                        win_prob = round(game_match.iloc[0]["home_win_prob" if is_home else "away_win_prob"] * 100, 1)
                        used_ml = True
                        st.caption("🤖 *Odds powered by ML model*")
                except Exception:
                    pass
            if not used_ml:
                st.caption("🧮 *Waiting for active ML odds*")

# 12. Live Game Tracker
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Live Game Tracker")

live_data = get_live_game_data(selected_abbr)

if live_data:
    st.sidebar.markdown(f"**{live_data['away_abbr']} @ {live_data['home_abbr']}**")
    st.sidebar.markdown(f"Score: `{live_data['away_score']} - {live_data['home_score']}`")
    st.sidebar.caption(f"Status: {live_data['clock']}")
    
    if live_data['status'] == 'in':
        if live_data['wp'] is not None:
            # Display large metric and dynamic visual progress bar
            st.sidebar.metric(label="Live Win Probability", value=f"{live_data['wp']}%")
            st.sidebar.progress(live_data['wp'] / 100.0)
        if live_data['possession']:
            st.sidebar.caption(f"Last Play: {live_data['possession']}")
    elif live_data['status'] == 'pre':
        st.sidebar.info("Game scheduled. Live odds will stream here after kickoff.")
    elif live_data['status'] == 'post':
        st.sidebar.success("Game Final.")
else:
    st.sidebar.info("No active game detected on the scoreboard.")

# 13. Interactive Folium Map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")
for _, row in df_teams.iterrows():
    icon = folium.CustomIcon(row["logo_url"], icon_size=(35, 35))
    popup_text = f"<b>{row['team']}</b><br>Adjusted Playoff: {row.get('adjusted_playoff', 50.0)}%"
    folium.Marker(location=[row["lat"], row["lon"]], icon=icon, tooltip=row["team"], popup=folium.Popup(popup_text, max_width=300)).add_to(m)

output = st_folium(m, width=900, height=500, key="fully_loaded_map")
if output and output.get("last_object_clicked_tooltip"):
    clicked_name = output["last_object_clicked_tooltip"]
    if clicked_name in team_names and clicked_name != st.session_state.selected_team:
        st.session_state.selected_team = clicked_name
        st.rerun()
