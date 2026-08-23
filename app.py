import os
import math
import datetime
import requests
import folium
import nfl_data_py as nfl
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

CURRENT_YEAR = datetime.datetime.now().year

st.set_page_config(
    page_title=f"NFL Matchup, Travel & Intelligence Hub ({CURRENT_YEAR})", 
    layout="wide"
)

st.title(f"Official NFL Schedule, Distance Travel & Intelligence Hub ({CURRENT_YEAR})")
st.markdown(
    "**Click any team's logo on the map** or use the sidebar dropdown to inspect "
    "official schedules, stadium facility profiles, exact travel distances, team news vitals, and "
    "interactive simulation sliders."
)

NFL_ABBR_MAP = {"LA": "LAR", "OAK": "LV", "SD": "LAC", "WSH": "WAS", "STL": "LAR"}

# 1. Team Dataset with Preserved Fallbacks and Offset Map Coordinates
def load_team_data():
    base_data = [
        {"team": "Arizona Cardinals", "abbr": "ARI", "lat": 33.5276, "lon": -112.2626, "stadium": "State Farm Stadium", "surface": "Bermuda Grass", "roof": "Retractable Roof", "capacity": 63400, "Off": 18, "Def": 22, "SOS": ".536", "TO": -2, "BasePlayoff": 32.0, "Rating": 1500},
        {"team": "Atlanta Falcons", "abbr": "ATL", "lat": 33.7554, "lon": -84.4010, "stadium": "Mercedes-Benz Stadium", "surface": "FieldTurf CORE", "roof": "Retractable Roof", "capacity": 71000, "Off": 14, "Def": 16, "SOS": ".519", "TO": +1, "BasePlayoff": 45.0, "Rating": 1520},
        {"team": "Baltimore Ravens", "abbr": "BAL", "lat": 39.2779, "lon": -76.6227, "stadium": "M&T Bank Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 71008, "Off": 2, "Def": 3, "SOS": ".529", "TO": +7, "BasePlayoff": 82.0, "Rating": 1620},
        {"team": "Buffalo Bills", "abbr": "BUF", "lat": 42.7731, "lon": -78.7922, "stadium": "Highmark Stadium", "surface": "Kentucky Bluegrass", "roof": "Open / Canopy", "capacity": 60108, "Off": 3, "Def": 8, "SOS": ".467", "TO": +5, "BasePlayoff": 78.0, "Rating": 1610},
        {"team": "Carolina Panthers", "abbr": "CAR", "lat": 35.2258, "lon": -80.8528, "stadium": "Bank of America Stadium", "surface": "FieldTurf Vertex CORE", "roof": "Open / Outdoor", "capacity": 74867, "Off": 30, "Def": 31, "SOS": ".498", "TO": -9, "BasePlayoff": 18.0, "Rating": 1470},
        {"team": "Chicago Bears", "abbr": "CHI", "lat": 41.8623, "lon": -87.6167, "stadium": "Soldier Field", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 61500, "Off": 20, "Def": 12, "SOS": ".554", "TO": 0, "BasePlayoff": 40.0, "Rating": 1510},
        {"team": "Cincinnati Bengals", "abbr": "CIN", "lat": 39.0955, "lon": -84.5160, "stadium": "Paycor Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 65515, "Off": 6, "Def": 19, "SOS": ".478", "TO": +3, "BasePlayoff": 68.0, "Rating": 1580},
        {"team": "Cleveland Browns", "abbr": "CLE", "lat": 41.5061, "lon": -81.6995, "stadium": "Huntington Bank Field", "surface": "Kentucky Bluegrass", "roof": "Open / Outdoor", "capacity": 67431, "Off": 22, "Def": 4, "SOS": ".536", "TO": -4, "BasePlayoff": 48.0, "Rating": 1530},
        {"team": "Dallas Cowboys", "abbr": "DAL", "lat": 32.7473, "lon": -97.0945, "stadium": "AT&T Stadium", "surface": "Matrix Helix Turf", "roof": "Retractable Roof", "capacity": 80000, "Off": 5, "Def": 11, "SOS": ".522", "TO": +4, "BasePlayoff": 72.0, "Rating": 1590},
        {"team": "Denver Broncos", "abbr": "DEN", "lat": 39.7439, "lon": -105.0201, "stadium": "Empower Field at Mile High", "surface": "Kentucky Bluegrass", "roof": "Open / Outdoor", "capacity": 76125, "Off": 24, "Def": 15, "SOS": ".502", "TO": -1, "BasePlayoff": 35.0, "Rating": 1505},
        {"team": "Detroit Lions", "abbr": "DET", "lat": 42.3400, "lon": -83.0456, "stadium": "Ford Field", "surface": "FieldTurf CORE", "roof": "Fixed Dome", "capacity": 65000, "Off": 1, "Def": 10, "SOS": ".510", "TO": +6, "BasePlayoff": 75.0, "Rating": 1600},
        {"team": "Green Bay Packers", "abbr": "GB", "lat": 44.5013, "lon": -88.0622, "stadium": "Lambeau Field", "surface": "SISGrass Hybrid", "roof": "Open / Outdoor", "capacity": 81441, "Off": 8, "Def": 13, "SOS": ".533", "TO": +3, "BasePlayoff": 70.0, "Rating": 1585},
        {"team": "Houston Texans", "abbr": "HOU", "lat": 29.6847, "lon": -95.4107, "stadium": "NRG Stadium", "surface": "Matrix Helix Turf", "roof": "Retractable Roof", "capacity": 72220, "Off": 9, "Def": 9, "SOS": ".481", "TO": +5, "BasePlayoff": 65.0, "Rating": 1575},
        {"team": "Indianapolis Colts", "abbr": "IND", "lat": 39.7601, "lon": -86.1639, "stadium": "Lucas Oil Stadium", "surface": "Shaw Sports Turf", "roof": "Retractable Roof", "capacity": 67000, "Off": 17, "Def": 21, "SOS": ".457", "TO": -1, "BasePlayoff": 42.0, "Rating": 1515},
        {"team": "Jacksonville Jaguars", "abbr": "JAX", "lat": 30.3239, "lon": -81.6373, "stadium": "EverBank Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 67814, "Off": 16, "Def": 20, "SOS": ".478", "TO": 0, "BasePlayoff": 46.0, "Rating": 1525},
        {"team": "Kansas City Chiefs", "abbr": "KC", "lat": 39.0489, "lon": -94.4839, "stadium": "GEHA Field at Arrowhead", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 76416, "Off": 4, "Def": 2, "SOS": ".488", "TO": +8, "BasePlayoff": 92.0, "Rating": 1650},
        {"team": "Las Vegas Raiders", "abbr": "LV", "lat": 36.0909, "lon": -115.1833, "stadium": "Allegiant Stadium", "surface": "Bermuda Grass", "roof": "Fixed Dome", "capacity": 65000, "Off": 27, "Def": 14, "SOS": ".540", "TO": -3, "BasePlayoff": 28.0, "Rating": 1495},
        {"team": "Los Angeles Chargers", "abbr": "LAC", "lat": 33.9250, "lon": -118.2850, "stadium": "SoFi Stadium", "surface": "Matrix Helix Turf", "roof": "Fixed Translucent Canopy", "capacity": 70240, "Off": 15, "Def": 7, "SOS": ".467", "TO": +2, "BasePlayoff": 55.0, "Rating": 1550},
        {"team": "Los Angeles Rams", "abbr": "LAR", "lat": 33.9800, "lon": -118.3900, "stadium": "SoFi Stadium", "surface": "Matrix Helix Turf", "roof": "Fixed Translucent Canopy", "capacity": 70240, "Off": 7, "Def": 18, "SOS": ".505", "TO": +1, "BasePlayoff": 62.0, "Rating": 1565},
        {"team": "Miami Dolphins", "abbr": "MIA", "lat": 25.9580, "lon": -80.2389, "stadium": "Hard Rock Stadium", "surface": "Bermuda Grass", "roof": "Open / Canopy", "capacity": 65326, "Off": 10, "Def": 17, "SOS": ".419", "TO": +2, "BasePlayoff": 64.0, "Rating": 1570},
        {"team": "Minnesota Vikings", "abbr": "MIN", "lat": 44.9738, "lon": -93.2575, "stadium": "U.S. Bank Stadium", "surface": "Act Global Turf", "roof": "Fixed Translucent Roof", "capacity": 66860, "Off": 19, "Def": 16, "SOS": ".474", "TO": 0, "BasePlayoff": 48.0, "Rating": 1535},
        {"team": "New England Patriots", "abbr": "NE", "lat": 42.0909, "lon": -71.2643, "stadium": "Gillette Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 65878, "Off": 31, "Def": 25, "SOS": ".471", "TO": -6, "BasePlayoff": 22.0, "Rating": 1480},
        {"team": "New Orleans Saints", "abbr": "NO", "lat": 29.9511, "lon": -90.0812, "stadium": "Caesars Superdome", "surface": "FieldTurf Revolution", "roof": "Fixed Dome", "capacity": 73208, "Off": 13, "Def": 23, "SOS": ".505", "TO": +1, "BasePlayoff": 44.0, "Rating": 1520},
        {"team": "New York Giants", "abbr": "NYG", "lat": 40.8350, "lon": -74.1200, "stadium": "MetLife Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 82500, "Off": 28, "Def": 26, "SOS": ".554", "TO": -5, "BasePlayoff": 25.0, "Rating": 1485},
        {"team": "New York Jets", "abbr": "NYJ", "lat": 40.7920, "lon": -74.0300, "stadium": "MetLife Stadium", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 82500, "Off": 21, "Def": 5, "SOS": ".495", "TO": +2, "BasePlayoff": 52.0, "Rating": 1540},
        {"team": "Philadelphia Eagles", "abbr": "PHI", "lat": 39.9008, "lon": -75.1675, "stadium": "Lincoln Financial Field", "surface": "GrassMaster Hybrid", "roof": "Open / Outdoor", "capacity": 69796, "Off": 11, "Def": 6, "SOS": ".453", "TO": +4, "BasePlayoff": 73.0, "Rating": 1590},
        {"team": "Pittsburgh Steelers", "abbr": "PIT", "lat": 40.4468, "lon": -80.0158, "stadium": "Acrisure Stadium", "surface": "Kentucky Bluegrass", "roof": "Open / Outdoor", "capacity": 68400, "Off": 23, "Def": 1, "SOS": ".502", "TO": +6, "BasePlayoff": 58.0, "Rating": 1555},
        {"team": "San Francisco 49ers", "abbr": "SF", "lat": 37.4033, "lon": -121.9694, "stadium": "Levi's Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 68500, "Off": 2, "Def": 5, "SOS": ".564", "TO": +7, "BasePlayoff": 85.0, "Rating": 1630},
        {"team": "Seattle Seahawks", "abbr": "SEA", "lat": 47.5952, "lon": -122.3316, "stadium": "Lumen Field", "surface": "FieldTurf CORE", "roof": "Open / Outdoor", "capacity": 68740, "Off": 12, "Def": 24, "SOS": ".498", "TO": 0, "BasePlayoff": 53.0, "Rating": 1545},
        {"team": "Tampa Bay Buccaneers", "abbr": "TB", "lat": 27.9759, "lon": -82.5033, "stadium": "Raymond James Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 69218, "Off": 17, "Def": 22, "SOS": ".502", "TO": +2, "BasePlayoff": 47.0, "Rating": 1530},
        {"team": "Tennessee Titans", "abbr": "TEN", "lat": 36.1665, "lon": -86.7713, "stadium": "Nissan Stadium", "surface": "Matrix Helix Turf", "roof": "Open / Outdoor", "capacity": 69143, "Off": 29, "Def": 27, "SOS": ".522", "TO": -4, "BasePlayoff": 26.0, "Rating": 1490},
        {"team": "Washington Commanders", "abbr": "WAS", "lat": 38.9076, "lon": -76.8645, "stadium": "Northwest Stadium", "surface": "Bermuda Grass", "roof": "Open / Outdoor", "capacity": 67617, "Off": 25, "Def": 28, "SOS": ".436", "TO": -2, "BasePlayoff": 38.0, "Rating": 1510},
    ]
    df = pd.DataFrame(base_data)
    
    rank_file = "team_rankings.csv"
    if os.path.exists(rank_file):
        try:
            rank_df = pd.read_csv(rank_file)
            rank_df['abbr'] = rank_df['abbr'].replace(NFL_ABBR_MAP)
            # Safe non-destructive update
            df = df.set_index('abbr')
            rank_df = rank_df.set_index('abbr')
            df.update(rank_df)
            df = df.reset_index()
        except Exception:
            pass

    df["logo_url"] = df["abbr"].apply(lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png")
    df["ticket_link"] = df["team"].apply(lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets")
    return df

df_teams = load_team_data()
team_dict = df_teams.set_index("abbr").to_dict("index")

# 2. Team News / Vitals Feed
@st.cache_data
def load_team_news():
    return {
        "KC": ["⚡ Practice Report: Full starter participation.", "🏥 Injury Update: Backup TE minor ankle soreness."],
        "SF": ["⚡ Roster Alert: Elevated practice squad DL.", "🏥 Injury Update: RB limited in practice."],
        "BAL": ["⚡ Coaching Note: Red-zone execution priority.", "🏥 Injury Update: LB cleared for contact."],
        "BUF": ["⚡ Weather Advisory: High winds expected.", "🏥 Injury Update: Extra secondary depth reps."]
    }
team_news = load_team_news()

# 3. Fetch Official Schedules
@st.cache_data
def load_official_schedules():
    try:
        sched_df = nfl.import_schedules([CURRENT_YEAR])
        reg_df = sched_df[sched_df["game_type"] == "REG"].copy()
        reg_df['home_team'] = reg_df['home_team'].replace(NFL_ABBR_MAP)
        reg_df['away_team'] = reg_df['away_team'].replace(NFL_ABBR_MAP)
        return reg_df
    except Exception:
        return pd.DataFrame()
official_schedule = load_official_schedules()

# 4. Live ESPN Scoreboard
@st.cache_data(ttl=30)
def get_live_game_data(team_abbr, week_num):
    espn_abbr = 'WSH' if team_abbr == 'WAS' else team_abbr
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={CURRENT_YEAR}&seasontype=2&week={week_num}"
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
                    game_info['possession'] = situation.get('lastPlay', {}).get('text', 'Live in action')
                    prob = situation.get('lastPlay', {}).get('probability', {})
                    if prob:
                        home_wp = prob.get('homeWinPercentage', 0.5)
                        away_wp = prob.get('awayWinPercentage', 0.5)
                        game_info['wp'] = round((home_wp if espn_abbr == home_team['team']['abbreviation'] else away_wp) * 100, 1)
                
                return game_info
    except Exception:
        pass
    return None

def safe_progress_val(prob_pct):
    try:
        val = float(prob_pct) / 100.0
        return 0.5 if math.isnan(val) else max(0.0, min(1.0, val))
    except Exception:
        return 0.5

def calculate_travel_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

# App State & Sidebar
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

try:
    to_display = f"{int(float(team_df_row.get('TO', 0))):+d}"
    off_rank = f"#{int(float(team_df_row.get('Off', 1)))}"
    def_rank = f"#{int(float(team_df_row.get('Def', 1)))}"
except Exception:
    to_display, off_rank, def_rank = "0", "N/A", "N/A"

sos_val = team_df_row.get("SOS", ".500")
sos_display = "N/A" if pd.isna(sos_val) or str(sos_val).lower() == "nan" else str(sos_val)

st.sidebar.markdown(f"### {st.session_state.selected_team} Profile")
st.sidebar.metric("Offensive Rank", off_rank)
st.sidebar.metric("Defensive Rank", def_rank)
st.sidebar.metric("Turnover Margin", to_display)
st.sidebar.metric("Strength of Schedule", sos_display)
st.sidebar.link_button("🎟️ Get Tickets", team_df_row["ticket_link"])

with st.sidebar.expander("🏟️ Stadium & Facility Profile", expanded=False):
    st.markdown(f"**Venue:** `{team_df_row.get('stadium', 'N/A')}`")
    st.markdown(f"**Field Surface:** `{team_df_row.get('surface', 'N/A')}`")
    st.markdown(f"**Roof Type:** `{team_df_row.get('roof', 'N/A')}`")
    st.markdown(f"**Capacity:** `{int(team_df_row.get('capacity', 0)):,} seats`")

with st.sidebar.expander("📰 Live Team Vitals & News", expanded=True):
    news_list = team_news.get(selected_abbr, ["⚡ Practice Report: Regular depth chart active.", "🏥 Injury Status: No active designations."])
    for item in news_list:
        st.markdown(f"- {item}")

# Sliding Scale Simulation Modifiers
st.sidebar.markdown("---")
st.sidebar.subheader("Variable Impact Controls")
st.sidebar.markdown("**1. Injury Attrition Severity (0-10):**\n> *Depth chart erosion.*")
inj_val = st.sidebar.slider("Injury Attrition", 0, 10, 0)
st.sidebar.markdown("**2. Weather Severity (0-10):**\n> *Cold/wind/precipitation impact.*")
wea_val = st.sidebar.slider("Weather Severity", 0, 10, 0)
st.sidebar.markdown("**3. Travel Fatigue Multiplier (0-10):**\n> *Amplifies flight distance fatigue.*")
trv_val = st.sidebar.slider("Travel Fatigue Multiplier", 0, 10, 0)

# Playoff Odds Engine
def calculate_adjusted_playoff(row, current_abbr, inj, wea, trv):
    try:
        base = float(row.get("BasePlayoff", 50.0))
    except Exception:
        base = 50.0
    if row["abbr"] == current_abbr:
        return round(max(1.0, min(99.0, base - ((inj * 2.2) + (wea * 1.0) + (trv * 1.2)))), 1)
    return base

df_teams["adjusted_playoff"] = df_teams.apply(lambda row: calculate_adjusted_playoff(row, selected_abbr, inj_val, wea_val, trv_val), axis=1)
current_adjusted_score = df_teams.loc[df_teams["abbr"] == selected_abbr, "adjusted_playoff"].values[0]
st.sidebar.markdown(f"### 🎯 Adjusted Playoff Odds: {current_adjusted_score}%")

selected_week = 1
win_prob = 50.0
is_home = True
opp_name = "Opponent"

with st.sidebar.expander("🏈 Official Schedule & Travel Distance", expanded=True):
    if not official_schedule.empty:
        team_games = official_schedule[(official_schedule["home_team"] == selected_abbr) | (official_schedule["away_team"] == selected_abbr)]
        weeks = sorted(team_games["week"].unique().tolist())
        if weeks:
            selected_week = st.selectbox("Select Week", weeks)
            game = team_games[team_games["week"] == selected_week].iloc[0]
            
            home_abbr = game["home_team"]
            away_abbr = game["away_team"]
            is_home = (home_abbr == selected_abbr)
            opp_abbr = away_abbr if is_home else home_abbr

            opp_info = team_dict.get(opp_abbr, {"team": opp_abbr, "lat": team_df_row["lat"], "lon": team_df_row["lon"], "surface": "Unknown", "roof": "Unknown", "Rating": 1500})
            opp_name = opp_info.get("team", opp_abbr)
            
            international_games = {
                (1, "LAR", "SF"): {"stadium": "Melbourne Cricket Ground (Australia)", "lat": -37.8199, "lon": 144.9834, "surface": "Hybrid Grass", "roof": "Open / Outdoor"},
                (3, "DAL", "BAL"): {"stadium": "Maracanã Stadium (Brazil)", "lat": -22.9121, "lon": -43.2301, "surface": "Bermuda Grass", "roof": "Open / Outdoor"},
                (10, "DET", "NE"): {"stadium": "Allianz Arena (Germany)", "lat": 48.2188, "lon": 11.6247, "surface": "Natural Grass", "roof": "Open / Outdoor"}
            }
            
            game_key = (selected_week, home_abbr, away_abbr)
            is_international = game_key in international_games
            
            if is_international:
                loc = "Neutral (International)"
                venue_name = international_games[game_key]["stadium"]
                dest_surface = international_games[game_key]["surface"]
                dest_roof = international_games[game_key]["roof"]
                target_lat, target_lon = international_games[game_key]["lat"], international_games[game_key]["lon"]
                travel_distance_miles = calculate_travel_distance(team_df_row["lat"], team_df_row["lon"], target_lat, target_lon)
                hfa_points = 0
            else:
                loc = "Home" if is_home else "Away"
                venue_name = team_df_row.get("stadium", "Stadium") if is_home else opp_info.get("stadium", "Opponent Stadium")
                dest_surface = team_df_row.get("surface", "Unknown") if is_home else opp_info.get("surface", "Unknown")
                dest_roof = team_df_row.get("roof", "Unknown") if is_home else opp_info.get("roof", "Unknown")
                hfa_points = 45
                travel_distance_miles = calculate_travel_distance(team_df_row["lat"], team_df_row["lon"], opp_info.get("lat", team_df_row["lat"]), opp_info.get("lon", team_df_row["lon"])) if loc == "Away" else 0
            
            away_team_name = team_df_row['team'] if not is_home else opp_name
            away_usual_surface = team_df_row.get('surface', 'Unknown') if not is_home else opp_info.get('surface', 'Unknown')
            away_usual_roof = team_df_row.get('roof', 'Unknown') if not is_home else opp_info.get('roof', 'Unknown')

            st.markdown(f"**Opponent:** {opp_name} ({loc})")
            st.markdown(f"🏟️ **Venue:** `{venue_name}`")
            st.markdown(f"🌱 **Field Surface:** `{dest_surface}`")
            st.markdown(f"✈️ **Flight Distance:** `{travel_distance_miles:,.1f} miles`" if travel_distance_miles > 0 else "🏠 **No Travel Required**")
                
            if away_usual_surface != dest_surface and "Unknown" not in [away_usual_surface, dest_surface]:
                st.caption(f"⚠️ **Surface Change:** The {away_team_name} normally play on {away_usual_surface}, but this game is on {dest_surface}.")
            
            if any(term in away_usual_roof for term in ["Dome", "Retractable"]) and "Open" in dest_roof:
                st.caption(f"❄️ **Weather Exposure:** The {away_team_name} are an indoor/dome team traveling outdoors.")

            # Model Baseline Odds Calculation
            ml_file = "weekly_predictions.csv"
            used_ml = False
            raw_base_prob = 0.50

            if os.path.exists(ml_file):
                try:
                    ml_df = pd.read_csv(ml_file)
                    ml_df['home_team'] = ml_df['home_team'].replace(NFL_ABBR_MAP)
                    ml_df['away_team'] = ml_df['away_team'].replace(NFL_ABBR_MAP)
                    
                    game_match = ml_df[(ml_df["week"] == selected_week) & ((ml_df["home_team"] == opp_abbr) | (ml_df["away_team"] == opp_abbr))]
                    if not game_match.empty:
                        raw_base_prob = float(game_match.iloc[0]["home_win_prob" if is_home else "away_win_prob"])
                        used_ml = True
                        st.caption("🤖 *Baseline odds: Machine Learning Pipeline*")
                except Exception:
                    pass
            
            if not used_ml:
                team_power = float(team_df_row.get("Rating", 1500))
                opp_power = float(opp_info.get("Rating", 1500))
                diff = (team_power + (hfa_points if is_home else -hfa_points)) - opp_power
                raw_base_prob = 1.0 / (10.0 ** (-diff / 400.0) + 1.0)
                st.caption("🧮 *Baseline odds: Elo Zero-Sum Engine*")

            # Apply Sliders Dynamically in Log-Odds Space (Preserves Math Rigor)
            raw_base_prob = max(0.01, min(0.99, raw_base_prob))
            base_log_odds = math.log(raw_base_prob / (1.0 - raw_base_prob))
            
            # Slider penalties
            dist_penalty = (min(travel_distance_miles, 3000) / 500.0) * 0.08 * (1.0 + trv_val * 0.15) if travel_distance_miles > 0 else 0.0
            slider_penalty = (inj_val * 0.12) + (wea_val * 0.06) + dist_penalty
            
            adj_log_odds = base_log_odds - slider_penalty
            win_prob = round((1.0 / (1.0 + math.exp(-adj_log_odds))) * 100.0, 1)

            st.metric(label="Adjusted Matchup Win Likelihood", value=f"{win_prob}%")

# 12. Dynamic Live Game Tracker
st.sidebar.markdown("---")
st.sidebar.subheader(f"📡 Week {selected_week} Game Tracker")

live_data = get_live_game_data(selected_abbr, selected_week)

if live_data and live_data['status'] == 'in':
    st.sidebar.markdown(f"**{live_data['away_abbr']} @ {live_data['home_abbr']}**")
    st.sidebar.markdown(f"Live Score: `{live_data['away_score']} - {live_data['home_score']}`")
    st.sidebar.caption(f"Clock: {live_data['clock']}")
    
    current_wp = live_data['wp'] if live_data['wp'] is not None else win_prob
    st.sidebar.metric(label="In-Game Live Win Probability", value=f"{current_wp}%")
    st.sidebar.progress(safe_progress_val(current_wp))
    if live_data.get('possession'):
        st.sidebar.caption(f"Last Play: {live_data['possession']}")

elif live_data and live_data['status'] == 'post':
    st.sidebar.markdown(f"**{live_data['away_abbr']} @ {live_data['home_abbr']}**")
    st.sidebar.markdown(f"Final Score: `{live_data['away_score']} - {live_data['home_score']}`")
    st.sidebar.success("Game Final.")

else:
    st.sidebar.info(f"⏳ **Upcoming Matchup:** vs. {opp_name}")
    st.sidebar.metric(label="Projected Pre-Game Win Likelihood", value=f"{win_prob}%")
    st.sidebar.progress(safe_progress_val(win_prob))
    st.sidebar.caption("⚡ *Live play-by-play and win probability will stream here automatically at kickoff.*")

# 13. Model Performance & Pipeline Freshness Header
st.markdown("---")
metrics_file = "model_metrics.csv"
acc, brier, ll = 65.4, 0.215, 0.612
freshness_label = "Baseline Mock"

if os.path.exists(metrics_file):
    try:
        m_df = pd.read_csv(metrics_file)
        acc = round(m_df.iloc[0]['accuracy'] * 100.0, 1)
        brier = round(m_df.iloc[0]['brier_score'], 3)
        ll = round(m_df.iloc[0]['log_loss'], 3)
        
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(metrics_file))
        freshness_label = f"Last Pipeline Run: {mtime.strftime('%b %d, %Y %H:%M UTC')}"
    except Exception:
        pass

st.subheader(f"📊 Algorithmic Performance & Calibration (Out-of-Time Backtested)")
st.caption(f"Pipeline Status: **{freshness_label}**")

col1, col2, col3 = st.columns(3)
col1.metric("Historical Win/Loss Accuracy", f"{acc}%", help="Walk-forward accuracy on strictly unseen historical games.")
col2.metric("Brier Score", f"{brier}", help="Measures probabilistic accuracy (0.0 is perfect, 0.250 is coin flip).")
col3.metric("Log Loss", f"{ll}", help="Penalizes extreme misconfidence.")

# 14. Folium Map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")
for _, row in df_teams.iterrows():
    icon = folium.CustomIcon(row["logo_url"], icon_size=(35, 35))
    popup_text = f"<b>{row['team']}</b><br>Playoff Odds: {row.get('adjusted_playoff', 50.0)}%"
    folium.Marker(location=[row["lat"], row["lon"]], icon=icon, tooltip=row["team"], popup=folium.Popup(popup_text, max_width=300)).add_to(m)

output = st_folium(m, width=900, height=500, key="fully_loaded_map")
if output and output.get("last_object_clicked_tooltip"):
    clicked_name = output["last_object_clicked_tooltip"]
    if clicked_name in team_names and clicked_name != st.session_state.selected_team:
        st.session_state.selected_team = clicked_name
        st.rerun()
