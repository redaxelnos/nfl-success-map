import os
import math
import json
import datetime
import requests
import folium
import nfl_data_py as nfl
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from fantasy_pipeline import fetch_complete_fantasy_state

# =====================================================================
# SECURE CLOUD AUTHENTICATION REBUILD
# =====================================================================
if not os.path.exists("oauth2.json"):
    if "yahoo" in st.secrets:
        with open("oauth2.json", "w") as f:
            json.dump(dict(st.secrets["yahoo"]), f)
    elif "YAHOO_KEYS" in st.secrets:
        with open("oauth2.json", "w") as f:
            f.write(st.secrets["YAHOO_KEYS"])

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
            if "abbr" in rank_df.columns:
                rank_df["abbr"] = rank_df["abbr"].replace(NFL_ABBR_MAP)
                update_cols = [c for c in ["Off", "Def", "TO", "SOS", "Rating", "BasePlayoff"] if c in rank_df.columns]
                merged = pd.merge(df, rank_df[["abbr"] + update_cols], on="abbr", how="left", suffixes=("", "_new"))
                for col in update_cols:
                    new_col = f"{col}_new"
                    if new_col in merged.columns:
                        merged[col] = merged[new_col].combine_first(merged[col])
                        merged.drop(columns=[new_col], inplace=True)
                df = merged
        except Exception:
            pass

    df["logo_url"] = df["abbr"].apply(lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png")
    df["ticket_link"] = df["team"].apply(lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets")
    return df

df_teams = load_team_data()
team_dict = df_teams.set_index("abbr").to_dict("index")

@st.cache_data(ttl=3600)
def load_team_news(team_abbr, year):
    results = {'injuries': [], 'news': []}
    try:
        injuries = nfl.import_injuries([year])
        if 'team' in injuries.columns: injuries['team'] = injuries['team'].replace(NFL_ABBR_MAP)
        team_injuries = injuries[injuries['team'] == team_abbr]
        if not team_injuries.empty:
            latest_week = team_injuries['week'].max()
            current_inj = team_injuries[team_injuries['week'] == latest_week].copy()
            def status_rank(row):
                stat = str(row.get('report_status', '')).upper()
                prac = str(row.get('practice_status', '')).upper()
                if 'OUT' in stat or 'IR' in stat: return 1
                if 'DOUBTFUL' in stat: return 2
                if 'QUESTIONABLE' in stat: return 3
                if 'DNP' in prac or 'DID NOT PARTICIPATE' in prac: return 4
                if 'LP' in prac or 'LIMITED' in prac: return 5
                return 6
            current_inj['rank'] = current_inj.apply(status_rank, axis=1)
            current_inj = current_inj.sort_values('rank')
            for _, row in current_inj.iterrows():
                player = row.get('full_name', 'Unknown')
                position = row.get('position', '')
                r_stat = row.get('report_status')
                p_stat = row.get('practice_status')
                if pd.notna(r_stat) and str(r_stat).strip() != "": status = str(r_stat).title()
                elif pd.notna(p_stat) and str(p_stat).strip() != "": status = f"Practice: {str(p_stat)}"
                else: status = "Injured Reserve / Out"
                injury = row.get('report_primary_injury')
                if pd.isna(injury) or str(injury).strip() == "": injury = row.get('practice_primary_injury', 'Undisclosed')
                if 'Full' not in status and 'FP' not in status:
                    results['injuries'].append(f"**{position} {player}:** {status} ({injury})")
    except Exception: pass
    if not results['injuries']: results['injuries'].append("✅ No active impact injuries reported.")
        
    try:
        espn_abbr = 'WSH' if team_abbr == 'WAS' else team_abbr
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{espn_abbr}/news"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        articles = data.get('articles', [])
        for art in articles[:6]: 
            headline = art.get('headline', '')
            link = art.get('links', {}).get('web', {}).get('href', '#')
            results['news'].append(f"📰 [{headline}]({link})")
    except Exception: pass
    if not results['news']: results['news'].append("No breaking team headlines right now.")
    return results

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=900)
def get_live_stadium_weather(lat, lon, roof_type):
    if "Dome" in str(roof_type) or "Retractable" in str(roof_type): return {"temp": 72.0, "wind": 0.0, "precip": 0.0, "condition": "Controlled (Indoor)", "penalty": 0.0}
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,precipitation&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
        resp = requests.get(url, timeout=5)
        data = resp.json().get('current', {})
        temp = data.get('temperature_2m', 70.0)
        wind = data.get('wind_speed_10m', 0.0)
        precip = data.get('precipitation', 0.0)
        penalty = 0.0
        if temp < 32: penalty += 3.0
        elif temp < 40: penalty += 1.0
        if wind > 20: penalty += 4.0
        elif wind > 15: penalty += 2.0
        if precip > 0.05: penalty += 3.0
        condition = "Clear / Fair"
        if precip > 0.05: condition = "Active Precipitation"
        elif wind > 15: condition = "High Winds"
        elif temp < 32: condition = "Freezing Conditions"
        return {"temp": temp, "wind": wind, "precip": precip, "condition": condition, "penalty": min(10.0, penalty)}
    except Exception: return {"temp": 70.0, "wind": 0.0, "precip": 0.0, "condition": "Data Unavailable", "penalty": 0.0}

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
    except Exception: pass
    return None

def safe_progress_val(prob_pct):
    try:
        val = float(prob_pct) / 100.0
        return 0.5 if math.isnan(val) else max(0.0, min(1.0, val))
    except Exception: return 0.5

def calculate_travel_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

@st.cache_data(ttl=600)  
def load_live_rosters_and_meta():
    try:
        return fetch_complete_fantasy_state("oauth2.json")
    except Exception as e:
        return pd.DataFrame(), {}

# Sidebar Setup
if "selected_team" not in st.session_state: st.session_state.selected_team = "Kansas City Chiefs"
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

with st.sidebar.expander("📰 Live Team Vitals & News", expanded=False):
    news_dict = load_team_news(selected_abbr, CURRENT_YEAR)
    t1, t2 = st.tabs(["🏥 Injuries", "📰 Headlines"])
    with t1:
        with st.container(height=220):
            for item in news_dict['injuries']: st.markdown(f"- {item}")
    with t2:
        with st.container(height=220):
            for item in news_dict['news']: st.markdown(f"- {item}")

st.sidebar.markdown("---")
st.sidebar.subheader("Manual Forecast Controls")
inj_val = st.sidebar.slider("Injury Attrition", 0, 10, 0)
wea_val = st.sidebar.slider("Weather Severity", 0, 10, 0)
trv_val = st.sidebar.slider("Travel Fatigue Multiplier", 0, 10, 0)

def calculate_adjusted_playoff(row, current_abbr, inj, wea, trv):
    try: base = float(row.get("BasePlayoff", 50.0))
    except Exception: base = 50.0
    if row["abbr"] == current_abbr: return round(max(1.0, min(99.0, base - ((inj * 2.2) + (wea * 1.0) + (trv * 1.2)))), 1)
    return base

df_teams["adjusted_playoff"] = df_teams.apply(lambda row: calculate_adjusted_playoff(row, selected_abbr, inj_val, wea_val, trv_val), axis=1)
current_adjusted_score = df_teams.loc[df_teams["abbr"] == selected_abbr, "adjusted_playoff"].values[0]
st.sidebar.markdown(f"### 🎯 Adjusted Playoff Odds: {current_adjusted_score}%")

selected_week = 3  # Updated statically or via user input loop for live week
win_prob = 50.0
is_home = True
opp_name = "Opponent"

with st.sidebar.expander("🏈 Official Schedule & Travel Distance", expanded=True):
    if not official_schedule.empty:
        team_games = official_schedule[(official_schedule["home_team"] == selected_abbr) | (official_schedule["away_team"] == selected_abbr)]
        weeks = sorted(team_games["week"].unique().tolist())
        if weeks:
            selected_week = st.selectbox("Select Week", weeks, index=weeks.index(3) if 3 in weeks else 0)
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
                target_lat_weather = international_games[game_key]["lat"]
                target_lon_weather = international_games[game_key]["lon"]
                travel_distance_miles = calculate_travel_distance(team_df_row["lat"], team_df_row["lon"], target_lat_weather, target_lon_weather)
                hfa_points = 0
            else:
                loc = "Home" if is_home else "Away"
                venue_name = team_df_row.get("stadium", "Stadium") if is_home else opp_info.get("stadium", "Opponent Stadium")
                dest_surface = team_df_row.get("surface", "Unknown") if is_home else opp_info.get("surface", "Unknown")
                dest_roof = team_df_row.get("roof", "Unknown") if is_home else opp_info.get("roof", "Unknown")
                hfa_points = 45
                target_lat_weather = team_df_row["lat"] if is_home else opp_info.get("lat", team_df_row["lat"])
                target_lon_weather = team_df_row["lon"] if is_home else opp_info.get("lon", team_df_row["lon"])
                travel_distance_miles = calculate_travel_distance(team_df_row["lat"], team_df_row["lon"], target_lat_weather, target_lon_weather) if loc == "Away" else 0
            
            away_team_name = team_df_row['team'] if not is_home else opp_name
            away_usual_surface = team_df_row.get('surface', 'Unknown') if not is_home else opp_info.get('surface', 'Unknown')
            away_usual_roof = team_df_row.get('roof', 'Unknown') if not is_home else opp_info.get('roof', 'Unknown')

            st.markdown(f"**Opponent:** {opp_name} ({loc})")
            st.markdown(f"🏟️ **Venue:** `{venue_name}`")
            st.markdown(f"🌱 **Field Surface:** `{dest_surface}`")
            st.markdown(f"✈️ **Flight Distance:** `{travel_distance_miles:,.1f} miles`" if travel_distance_miles > 0 else "🏠 **No Travel Required**")
            
            live_weather = get_live_stadium_weather(target_lat_weather, target_lon_weather, dest_roof)
            st.markdown(f"🌤️ **Live Stadium Weather:** `{live_weather['temp']}°F | {live_weather['wind']} mph wind | {live_weather['condition']}`")
                
            if away_usual_surface != dest_surface and "Unknown" not in [away_usual_surface, dest_surface]:
                st.caption(f"⚠️ **Surface Change:** The {away_team_name} normally play on {away_usual_surface}, but this game is on {dest_surface}.")
            if any(term in away_usual_roof for term in ["Dome", "Retractable"]) and "Open" in dest_roof:
                st.caption(f"❄️ **Weather Exposure:** The {away_team_name} are an indoor/dome team traveling outdoors.")

            apply_live_weather = st.checkbox("Inject live weather penalty into odds", value=False)

            ml_file = "weekly_predictions.csv"
            used_ml = False
            raw_home_prob = 0.50
            game_match = pd.DataFrame()

            if os.path.exists(ml_file):
                try:
                    ml_df = pd.read_csv(ml_file)
                    ml_df['home_team'] = ml_df['home_team'].replace(NFL_ABBR_MAP)
                    ml_df['away_team'] = ml_df['away_team'].replace(NFL_ABBR_MAP)
                    game_match = ml_df[(ml_df["week"] == selected_week) & (ml_df["home_team"] == home_abbr) & (ml_df["away_team"] == away_abbr)]
                    if not game_match.empty:
                        raw_home_prob = float(game_match.iloc[0]["home_win_prob"])
                        used_ml = True
                        st.caption("🤖 *Baseline odds: Machine Learning Pipeline*")
                except Exception: pass
            
            if not used_ml:
                home_power = float(team_dict.get(home_abbr, {}).get("Rating", 1500))
                away_power = float(team_dict.get(away_abbr, {}).get("Rating", 1500))
                diff = (home_power + hfa_points) - away_power
                raw_home_prob = 1.0 / (10.0 ** (-diff / 400.0) + 1.0)
                st.caption("🧮 *Baseline odds: Elo Zero-Sum Engine*")

            raw_home_prob = max(0.01, min(0.99, raw_home_prob))
            home_log_odds = math.log(raw_home_prob / (1.0 - raw_home_prob))
            
            active_wea_val = live_weather['penalty'] if apply_live_weather else wea_val
            away_lat = team_dict.get(away_abbr, {}).get("lat", target_lat_weather)
            away_lon = team_dict.get(away_abbr, {}).get("lon", target_lon_weather)
            actual_away_flight = calculate_travel_distance(away_lat, away_lon, target_lat_weather, target_lon_weather) if not is_international else 0.0
            
            dist_penalty = (min(actual_away_flight, 3000) / 500.0) * 0.08 * (1.0 + trv_val * 0.15) if actual_away_flight > 0 else 0.0
            inj_shift = (inj_val * 0.08) if not is_home else -(inj_val * 0.08)
            wea_shift = (active_wea_val * 0.03) if (any(term in away_usual_roof for term in ["Dome", "Retractable"]) and "Open" in dest_roof) else 0.0
            
            net_home_advantage_shift = dist_penalty + inj_shift + wea_shift
            adj_home_log_odds = home_log_odds + net_home_advantage_shift
            adj_home_prob = round((1.0 / (1.0 + math.exp(-adj_home_log_odds))) * 100.0, 1)
            adj_away_prob = round(100.0 - adj_home_prob, 1)

            win_prob = adj_home_prob if is_home else adj_away_prob
            st.metric(label="Adjusted Matchup Win Likelihood", value=f"{win_prob}%")

            if used_ml and not game_match.empty and 'model_margin' in game_match.columns:
                m_row = game_match.iloc[0]
                model_margin = m_row.get('model_margin', None)
                match_sched = official_schedule[official_schedule['game_id'] == m_row['game_id']]
                market_margin = None
                if not match_sched.empty:
                    raw_spread = match_sched.iloc[0]['spread_line']
                    if pd.notna(raw_spread): market_margin = float(raw_spread if m_row['home_team'] == selected_abbr else -raw_spread)
                
                if pd.notna(model_margin):
                    with st.expander("💰 Market Discrepancy & Spread Edge", expanded=True):
                        team_model_margin = float(model_margin if is_home else -model_margin)
                        team_market_margin = market_margin if pd.notna(market_margin) else 0.0
                        team_edge = team_model_margin - team_market_margin
                        team_market_spread = -team_market_margin
                        team_model_spread = -team_model_margin

                        def format_spread(val): return "PK" if round(val, 1) == 0.0 else f"{val:+.1f}"

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Market Spread", format_spread(team_market_spread) if pd.notna(market_margin) else "N/A", help="Consensus Vegas spread.")
                        c2.metric("Model Spread", format_spread(team_model_spread), help="Where the model thinks the spread should be.")
                        edge_val = abs(team_edge)
                        c3.metric("Hidden Value", f"{edge_val:.1f} pts" if pd.notna(market_margin) else "N/A", delta=f"{team_edge:+.1f} for {st.session_state.selected_team}" if pd.notna(market_margin) else None)

                        st.markdown("**Spread Comparison Indicator**")
                        comp_df = pd.DataFrame({"Points": [team_market_spread, team_model_spread]}, index=["Vegas Spread", "Model Spread"])
                        st.bar_chart(comp_df, height=150, color="#1f77b4")

                        favored_team = st.session_state.selected_team if team_edge > 0 else opp_name
                        st.markdown("---")
                        
                        if pd.notna(market_margin):
                            if round(edge_val, 1) == 0.0: st.caption("⚖️ **Perfect Agreement:** The model and the sportsbooks project the exact same margin.")
                            else:
                                if team_edge > 0:
                                    if team_market_spread > 0 and team_model_spread <= 0: logic_text = f"Vegas expects the {st.session_state.selected_team} to be underdogs (+{team_market_spread:.1f}), but the model expects an outright **UPSET victory** (winning by {abs(team_model_spread):.1f})."
                                    elif team_market_spread > 0 and team_model_spread > 0: logic_text = f"Vegas expects the {st.session_state.selected_team} to lose by {team_market_spread:.1f}, but the model thinks it will be a much closer game (losing by only {team_model_spread:.1f})."
                                    elif team_market_spread <= 0 and team_model_spread < 0: logic_text = f"Vegas expects the {st.session_state.selected_team} to win by {abs(team_market_spread):.1f}, but the model expects them to win by an even larger blowout ({abs(team_model_spread):.1f})."
                                else: 
                                    if team_market_spread <= 0 and team_model_spread > 0: logic_text = f"Vegas expects the {st.session_state.selected_team} to be favorites (-{abs(team_market_spread):.1f}), but the model expects an outright **UPSET loss** (losing by {team_model_spread:.1f})."
                                    elif team_market_spread <= 0 and team_model_spread <= 0: logic_text = f"Vegas expects the {st.session_state.selected_team} to win by {abs(team_market_spread):.1f}, but the model thinks it will be a much closer game (winning by only {abs(team_model_spread):.1f})."
                                    elif team_market_spread > 0 and team_model_spread > 0: logic_text = f"Vegas expects the {st.session_state.selected_team} to lose by {team_market_spread:.1f}, but the model expects them to get beat even worse (losing by {team_model_spread:.1f})."
                                icon = "🔥" if edge_val >= 2.0 else "💡"
                                bold_alert = "**Actionable Edge:** " if edge_val >= 2.0 else "**How to read this:** "
                                st.caption(f"{icon} {bold_alert}{logic_text} Therefore, the model identifies **{edge_val:.1f} points of betting value** on the **{favored_team}**.")

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
    if live_data.get('possession'): st.sidebar.caption(f"Last Play: {live_data['possession']}")
elif live_data and live_data['status'] == 'post':
    st.sidebar.markdown(f"**{live_data['away_abbr']} @ {live_data['home_abbr']}**")
    st.sidebar.markdown(f"Final Score: `{live_data['away_score']} - {live_data['home_score']}`")
    st.sidebar.success("Game Final.")
else:
    st.sidebar.info(f"⏳ **Upcoming Matchup:** vs. {opp_name}")
    st.sidebar.metric(label="Projected Pre-Game Win Likelihood", value=f"{win_prob}%")
    st.sidebar.progress(safe_progress_val(win_prob))

st.markdown("---")
metrics_file = "model_metrics.csv"
acc, brier, ll = 65.4, 0.215, 0.612
freshness_label = "Baseline Mock"
if os.path.exists(metrics_file):
    try:
        m_df = pd.read_csv(metrics_file)
        latest_m = m_df.iloc[-1]
        acc = round(latest_m['accuracy'] * 100.0, 1)
        brier = round(latest_m['brier_score'], 3)
        ll = round(latest_m['log_loss'], 3)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(metrics_file))
        freshness_label = f"Last Pipeline Run: {mtime.strftime('%b %d, %Y %H:%M UTC')}"
    except Exception: pass

st.subheader(f"📊 Algorithmic Performance (Out-of-Time Backtested)")
st.caption(f"Pipeline Status: **{freshness_label}**")

col1, col2, col3 = st.columns(3)
col1.metric("Historical Win/Loss Accuracy", f"{acc}%", help="Walk-forward accuracy on strictly unseen historical games.")
col2.metric("Brier Score", f"{brier}", help="Measures probabilistic accuracy (0.0 is perfect, 0.250 is coin flip).")
col3.metric("Log Loss", f"{ll}", help="Penalizes extreme misconfidence.")

if 'm_df' in locals() and 'date' in m_df.columns and len(m_df) > 1:
    tab1, tab2 = st.tabs(["📉 Calibration Over Time (Log Loss & Brier)", "🎯 Accuracy Over Time"])
    with tab1: st.line_chart(m_df.set_index('date')[['log_loss', 'brier_score']])
    with tab2:
        m_df['Accuracy %'] = m_df['accuracy'] * 100.0
        st.line_chart(m_df.set_index('date')[['Accuracy %']])

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

# =====================================================================
# ZERO-SUM FANTASY COMMAND CENTER & MANAGERIAL AUDIT
# =====================================================================
st.markdown("---")
st.header("⚡ Live Fantasy Intelligence & Prescriptive Managerial Audit")

col_head, col_sync = st.columns([3, 1])
with col_sync:
    if st.button("🔄 Force Real-Time Sync"):
        st.cache_data.clear()
        st.rerun()

# ---------------------------------------------------------------------
# FORWARD-LOOKING MATCHUP ENGINE & TIME-LOCK PROTOCOL
# ---------------------------------------------------------------------
def clean_player_name(name):
    if not isinstance(name, str): return name
    for suffix in [" Sr.", " Jr.", " III", " II"]:
        name = name.replace(suffix, "")
    return name.strip()

@st.cache_data(ttl=60)
def get_locked_nfl_teams(year, week):
    """Pings ESPN live scoreboard to flag teams whose games have already started/finished."""
    locked = set()
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={year}&seasontype=2&week={week}"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        for event in data.get('events', []):
            state = event['status']['type']['state']
            if state in ['in', 'post']:
                for comp in event['competitions'][0]['competitors']:
                    team_abbr = comp['team']['abbreviation'].upper()
                    locked.add(team_abbr)
                    # Normalize common variations
                    if team_abbr == 'WSH': locked.add('WAS')
                    elif team_abbr == 'LAR': locked.add('LA')
                    elif team_abbr == 'LV': locked.add('OAK')
    except Exception:
        pass
    return locked

@st.cache_data(ttl=3600)
def load_real_ppg_baselines():
    """Extracts actual real-world Fantasy PPG."""
    try:
        for year in [CURRENT_YEAR, CURRENT_YEAR - 1]:
            try:
                weekly_df = nfl.import_weekly_data([year])
                if not weekly_df.empty:
                    weekly_df['clean_name'] = weekly_df['player_display_name'].apply(clean_player_name)
                    counts = weekly_df.groupby('clean_name').size()
                    valid = counts[counts >= 3].index
                    filtered = weekly_df[weekly_df['clean_name'].isin(valid)]
                    ppg_dict = filtered.groupby('clean_name')['fantasy_points_ppr'].mean().to_dict()
                    if ppg_dict: return ppg_dict
            except Exception: continue
        return {}
    except Exception: return {}

def get_opponent_def_rank(team_abbr, week, sched_df, team_data_dict):
    """Determines how elite the opposing defense is this specific week."""
    try:
        game = sched_df[((sched_df['home_team'] == team_abbr) | (sched_df['away_team'] == team_abbr)) & (sched_df['week'] == week)]
        if game.empty: return 16
        row = game.iloc[0]
        opp = row['away_team'] if row['home_team'] == team_abbr else row['home_team']
        return float(team_data_dict.get(opp, {}).get("Def", 16))
    except Exception: return 16.0

def get_algorithmic_projection(player, nfl_team, pos, status, ppg_dict, week, sched_df, team_data_dict):
    cleaned_player = clean_player_name(player)
    
    if cleaned_player in ppg_dict:
        val = ppg_dict[cleaned_player]
    else:
        pos_base = {"QB": 14.0, "RB": 7.0, "WR": 7.0, "TE": 5.0, "K": 7.0, "DEF": 6.0}
        val = pos_base.get(pos, 6.0)
        elites = ["Joe Burrow", "Christian McCaffrey", "Breece Hall", "Derrick Henry", "Amon-Ra St. Brown", "CeeDee Lamb", "Justin Jefferson", "Aaron Jones", "DeVonta Smith", "Tee Higgins", "Trevor Lawrence", "Garrett Wilson"]
        if cleaned_player in elites: val += 7.0
            
    # Forward-Looking Matchup Variance
    opp_def_rank = get_opponent_def_rank(nfl_team.upper(), week, sched_df, team_data_dict)
    matchup_shift = (opp_def_rank - 16) * 0.15 
    val += matchup_shift

    # Zero out strictly inactive tags. We no longer slash the "Q" tag.
    if status in ["O", "IR", "D", "IR-R", "PUP", "SUSP"]:
        val = 0.0
        
    return max(0.0, round(val, 1))

real_ppg_data = load_real_ppg_baselines()
live_roster_df, league_metadata = load_live_rosters_and_meta()

if not live_roster_df.empty:
    available_leagues = live_roster_df["League"].unique().tolist()
    
    col_sel, _ = st.columns([1, 2])
    with col_sel:
        selected_league = st.selectbox("Select Active Fantasy League:", available_leagues)
    
    league_roster = live_roster_df[live_roster_df["League"] == selected_league].copy()
    
    # 1. Fetch live lock statuses to protect Thursday/Played players
    locked_nfl_teams = get_locked_nfl_teams(CURRENT_YEAR, selected_week)
    
    # 2. Inject Matchup-adjusted algorithm projections
    league_roster["Matchup_Proj"] = league_roster.apply(lambda r: get_algorithmic_projection(
        r["Player"], r["NFL_Team"], r["Real_Pos"], r["Health_Status"], 
        real_ppg_data, selected_week, official_schedule, team_dict
    ), axis=1)

    current_meta = league_metadata.get(selected_league, {})
    league_limits = current_meta.get("settings", {"IR": 1, "BN": 6})
    waiver_pool = current_meta.get("waivers", {})
    
    tab_starters, tab_bench, tab_manager_audit = st.tabs(["🔥 Active Starters", "🛋️ Bench & Reserves", "⚖️ Prescriptive Action Directives"])
    
    with tab_starters:
        starters = league_roster[~league_roster["Fantasy_Slot"].isin(["BN", "IR"])]
        st.dataframe(
            starters[["Fantasy_Slot", "Player", "Real_Pos", "NFL_Team", "Matchup_Proj", "Health_Status"]],
            use_container_width=True, hide_index=True
        )

    with tab_bench:
        bench = league_roster[league_roster["Fantasy_Slot"].isin(["BN", "IR"])]
        st.dataframe(
            bench[["Fantasy_Slot", "Player", "Real_Pos", "NFL_Team", "Matchup_Proj", "Health_Status"]],
            use_container_width=True, hide_index=True
        )

    with tab_manager_audit:
        st.subheader("Algorithmic Decision Matrix & Directives")
        directives_issued = False

        # --- RULE IDENTIFICATION & IR SCAN ---
        max_ir = league_limits.get("IR", 1)
        ir_occupied_players = league_roster[league_roster["Fantasy_Slot"].isin(["IR", "IR-R"])]["Player"].tolist()
        ir_occupied_count = len(ir_occupied_players)
        ir_eligible_on_bench = bench[(bench["Health_Status"].isin(["IR", "IR-R", "O"])) & (bench["Fantasy_Slot"] == "BN")]

        if not ir_eligible_on_bench.empty:
            directives_issued = True
            for _, ir_p in ir_eligible_on_bench.iterrows():
                if ir_occupied_count >= max_ir:
                    st.error(
                        f"⛔ **STRUCTURAL BOTTLENECK: IR Overflow**  \n"
                        f"• **Asset:** **{ir_p['Player']}** carries an active **{ir_p['Health_Status']}** designation but is burning a regular bench spot (`BN`).  \n"
                        f"• **Cause:** Dynamic league capacity is maxed at **{max_ir} IR slot(s)** (Occupied by: {', '.join(ir_occupied_players)}).  \n"
                        f"• **Action Required:** Monitor active IR players. Unblock this slot as soon as a player clears protocol to generate a free waiver acquisition."
                    )
                else:
                    st.info(
                        f"💡 **OPTIMIZATION: Open IR Slot Available**  \n"
                        f"• **Action:** Shift **{ir_p['Player']}** to your vacant IR slot immediately.  \n"
                        f"• **Result:** Unlocks 1 free roster spot for a speculative skill-position stash prior to kickoff."
                    )

        # --- LINEUP OPTIMIZATION (START/SIT) WITH TIME-LOCK ENFORCEMENT ---
        benched_skill = bench[(bench["Real_Pos"].isin(["QB", "RB", "WR", "TE", "K", "DEF"])) & (bench["Matchup_Proj"] > 0)]
        starters_skill = starters[starters["Real_Pos"].isin(["QB", "RB", "WR", "TE", "K", "DEF"])]
        
        start_sit_moves = []
        for _, bench_p in benched_skill.iterrows():
            # If the bench player has already played/locked, ignore them entirely
            if bench_p["NFL_Team"] in locked_nfl_teams:
                continue
                
            b_val = bench_p["Matchup_Proj"]
            
            if bench_p["Real_Pos"] == "QB": valid_slots = ["QB", "S-FLEX"]
            elif bench_p["Real_Pos"] == "RB": valid_slots = ["RB", "W/R/T", "W/R", "FLEX"]
            elif bench_p["Real_Pos"] == "WR": valid_slots = ["WR", "W/R/T", "W/R", "FLEX"]
            elif bench_p["Real_Pos"] == "TE": valid_slots = ["TE", "W/R/T", "FLEX"]
            elif bench_p["Real_Pos"] == "K": valid_slots = ["K"]
            elif bench_p["Real_Pos"] == "DEF": valid_slots = ["DEF"]
            else: valid_slots = []
            
            # Evaluate against active starters whose games have NOT started yet
            eligible_starters = starters_skill[
                (starters_skill["Fantasy_Slot"].isin(valid_slots)) & 
                (~starters_skill["NFL_Team"].isin(locked_nfl_teams))
            ]
            
            if not eligible_starters.empty:
                weakest_starter = eligible_starters.loc[eligible_starters["Matchup_Proj"].idxmin()]
                
                if b_val > weakest_starter["Matchup_Proj"] + 1.5:
                    start_sit_moves.append({
                        "Bench_Player": bench_p["Player"],
                        "Bench_Val": b_val,
                        "Starter_Player": weakest_starter["Player"],
                        "Starter_Val": weakest_starter["Matchup_Proj"],
                        "Slot": weakest_starter["Fantasy_Slot"]
                    })

        if start_sit_moves:
            directives_issued = True
            start_sit_moves = sorted(start_sit_moves, key=lambda x: x["Bench_Val"] - x["Starter_Val"], reverse=True)
            seen_starters = set()
            
            for move in start_sit_moves:
                if move["Starter_Player"] not in seen_starters:
                    st.error(
                        f"🚨 **SUBOPTIMAL DEPLOYMENT: Matchup/Sit Error Detected**  \n"
                        f"• **Benched Asset:** **{move['Bench_Player']}** (Matchup Proj: {move['Bench_Val']} pts) is trapped on your bench.  \n"
                        f"• **Active Vulnerability:** **{move['Starter_Player']}** (Matchup Proj: {move['Starter_Val']} pts) is currently starting in the **{move['Slot']}** slot.  \n"
                        f"• **Directive:** Based on defensive matchup variances, bench {move['Starter_Player']} and activate {move['Bench_Player']} immediately to recover **{round(move['Bench_Val'] - move['Starter_Val'], 1)}** projected points."
                    )
                    seen_starters.add(move["Starter_Player"])

        # --- INJURY CONTINGENCY DIRECTIVES ---
        injured_starters = starters[starters["Health_Status"].isin(["Q", "D", "O"])]
        if not injured_starters.empty:
            directives_issued = True
            for _, s in injured_starters.iterrows():
                # Skip locked players (their status won't matter anymore)
                if s["NFL_Team"] in locked_nfl_teams: continue
                
                pos = s["Real_Pos"]
                pos_bench = bench[bench["Real_Pos"] == pos]
                
                pool = waiver_pool.get(pos, [])
                waiver_recommendations = [f"**{p['Player']}** ({p['NFL_Team']})" for p in pool[:2]] if pool else ["Top Projected Waiver Option"]

                if pos_bench.empty:
                    st.warning(
                        f"🚨 **ACTION REQUIRED: Critical {pos} Fragility**  \n"
                        f"• **Exposure:** Starter **{s['Player']} ({s['NFL_Team']})** is listed as **{s['Health_Status']}** with **0 backup {pos}s** rostered.  \n"
                        f"• **Directive Claim:** Add waiver target {', '.join(waiver_recommendations)} to prevent an automatic zero if scratched Sunday morning."
                    )
                else:
                    healthy_backup = pos_bench[pos_bench["Health_Status"] == "Healthy"]
                    backup_name = healthy_backup.iloc[0]["Player"] if not healthy_backup.empty else pos_bench.iloc[0]["Player"]
                    st.info(
                        f"⚠️ **LINEUP ALERT: Pre-Game Contingency Swap**  \n"
                        f"• **Starter:** **{s['Player']} ({s['NFL_Team']})** is **{s['Health_Status']}**.  \n"
                        f"• **In-House Protocol:** Roster holds redundancy via **{backup_name}**. Prepare to swap into starting lineup if game-time scratch occurs."
                    )

        # --- BENCH LIQUIDITY PURGE ---
        kickers_on_bench = bench[bench["Real_Pos"] == "K"]
        defs_on_bench = bench[bench["Real_Pos"] == "DEF"]
        
        if not kickers_on_bench.empty:
            directives_issued = True
            for _, k in kickers_on_bench.iterrows():
                st.warning(f"📉 **PURGE DIRECTIVE:** Drop backup kicker **{k['Player']} ({k['NFL_Team']})**. Zero marginal variance; backup kickers hold negative opportunity cost.")
                
        if not defs_on_bench.empty:
            directives_issued = True
            for _, d in defs_on_bench.iterrows():
                st.warning(f"📉 **PURGE DIRECTIVE:** Drop backup defense **{d['Player']} ({d['NFL_Team']})**. Defensive streaming assets are redundant roster holds.")

        if not directives_issued:
            st.success("✅ **Zero-Sum Validation:** Roster is mathematically calibrated. Zero structural inefficiencies, unhedged starting liabilities, or Start/Sit errors detected.")

    st.markdown("<br><small>[Fantasy data provided by Yahoo Fantasy](https://football.fantasysports.yahoo.com/)</small>", unsafe_allow_html=True)
else:
    st.info("Live Yahoo Fantasy Data currently unavailable. Ensure `oauth2.json` or Streamlit Secrets are active.")
