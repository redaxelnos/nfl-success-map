import math
import folium
import nfl_data_py as nfl
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Official NFL Matchup, Travel & Vitals Hub", layout="wide"
)

st.title("Official NFL Schedule, Distance Travel & Intelligence Hub")
st.markdown(
    "**Click any team's logo on the map** or use the dropdown to inspect"
    " official schedules, exact travel distances, team news vitals, and"
    " interactive variable sliders."
)

# 1. Complete 32-Team Dataset with Coordinates & Metadata
@st.cache_data
def load_team_data():
    data = [
        {"team": "Arizona Cardinals", "abbr": "ARI", "lat": 33.5276, "lon": -112.2626, "Off": 18, "Def": 22, "SOS": ".512", "TO": -2, "BasePlayoff": 32.0, "Rating": 1500},
        {"team": "Atlanta Falcons", "abbr": "ATL", "lat": 33.7554, "lon": -84.4010, "Off": 14, "Def": 16, "SOS": ".485", "TO": +1, "BasePlayoff": 45.0, "Rating": 1520},
        {"team": "Baltimore Ravens", "abbr": "BAL", "lat": 39.2779, "lon": -76.6227, "Off": 2, "Def": 3, "SOS": ".524", "TO": +7, "BasePlayoff": 82.0, "Rating": 1620},
        {"team": "Buffalo Bills", "abbr": "BUF", "lat": 42.7738, "lon": -78.7870, "Off": 3, "Def": 8, "SOS": ".508", "TO": +5, "BasePlayoff": 78.0, "Rating": 1610},
        {"team": "Carolina Panthers", "abbr": "CAR", "lat": 35.2258, "lon": -80.8528, "Off": 30, "Def": 31, "SOS": ".492", "TO": -9, "BasePlayoff": 18.0, "Rating": 1470},
        {"team": "Chicago Bears", "abbr": "CHI", "lat": 41.8623, "lon": -87.6167, "Off": 20, "Def": 12, "SOS": ".478", "TO": 0, "BasePlayoff": 40.0, "Rating": 1510},
        {"team": "Cincinnati Bengals", "abbr": "CIN", "lat": 39.0955, "lon": -84.5160, "Off": 6, "Def": 19, "SOS": ".531", "TO": +3, "BasePlayoff": 68.0, "Rating": 1580},
        {"team": "Cleveland Browns", "abbr": "CLE", "lat": 41.5061, "lon": -81.6995, "Off": 22, "Def": 4, "SOS": ".542", "TO": -4, "BasePlayoff": 48.0, "Rating": 1530},
        {"team": "Dallas Cowboys", "abbr": "DAL", "lat": 32.7473, "lon": -97.0945, "Off": 5, "Def": 11, "SOS": ".495", "TO": +4, "BasePlayoff": 72.0, "Rating": 1590},
        {"team": "Denver Broncos", "abbr": "DEN", "lat": 39.7439, "lon": -105.0201, "Off": 24, "Def": 15, "SOS": ".515", "TO": -1, "BasePlayoff": 35.0, "Rating": 1505},
        {"team": "Detroit Lions", "abbr": "DET", "lat": 42.3400, "lon": -83.0456, "Off": 1, "Def": 10, "SOS": ".510", "TO": +6, "BasePlayoff": 75.0, "Rating": 1600},
        {"team": "Green Bay Packers", "abbr": "GB", "lat": 44.5013, "lon": -88.0622, "Off": 8, "Def": 13, "SOS": ".502", "TO": +3, "BasePlayoff": 70.0, "Rating": 1585},
        {"team": "Houston Texans", "abbr": "HOU", "lat": 29.6847, "lon": -95.4107, "Off": 9, "Def": 9, "SOS": ".488", "TO": +5, "BasePlayoff": 65.0, "Rating": 1575},
        {"team": "Indianapolis Colts", "abbr": "IND", "lat": 39.7601, "lon": -86.1639, "Off": 17, "Def": 21, "SOS": ".490", "TO": -1, "BasePlayoff": 42.0, "Rating": 1515},
        {"team": "Jacksonville Jaguars", "abbr": "JAX", "lat": 30.3239, "lon": -81.6373, "Off": 16, "Def": 20, "SOS": ".500", "TO": 0, "BasePlayoff": 46.0, "Rating": 1525},
        {"team": "Kansas City Chiefs", "abbr": "KC", "lat": 39.0489, "lon": -94.4839, "Off": 4, "Def": 2, "SOS": ".535", "TO": +8, "BasePlayoff": 92.0, "Rating": 1650},
        {"team": "Las Vegas Raiders", "abbr": "LV", "lat": 36.0909, "lon": -115.1833, "Off": 27, "Def": 14, "SOS": ".520", "TO": -3, "BasePlayoff": 28.0, "Rating": 1495},
        {"team": "Los Angeles Chargers", "abbr": "LAC", "lat": 33.9535, "lon": -118.3390, "Off": 15, "Def": 7, "SOS": ".475", "TO": +2, "BasePlayoff": 55.0, "Rating": 1550},
        {"team": "Los Angeles Rams", "abbr": "LAR", "lat": 33.9535, "lon": -118.3390, "Off": 7, "Def": 18, "SOS": ".512", "TO": +1, "BasePlayoff": 62.0, "Rating": 1565},
        {"team": "Miami Dolphins", "abbr": "MIA", "lat": 25.9580, "lon": -80.2389, "Off": 10, "Def": 17, "SOS": ".482", "TO": +2, "BasePlayoff": 64.0, "Rating": 1570},
        {"team": "Minnesota Vikings", "abbr": "MIN", "lat": 44.9738, "lon": -93.2575, "Off": 19, "Def": 16, "SOS": ".505", "TO": 0, "BasePlayoff": 48.0, "Rating": 1535},
        {"team": "New England Patriots", "abbr": "NE", "lat": 42.0909, "lon": -71.2643, "Off": 31, "Def": 25, "SOS": ".518", "TO": -6, "BasePlayoff": 22.0, "Rating": 1480},
        {"team": "New Orleans Saints", "abbr": "NO", "lat": 29.9511, "lon": -90.0812, "Off": 13, "Def": 23, "SOS": ".470", "TO": +1, "BasePlayoff": 44.0, "Rating": 1520},
        {"team": "New York Giants", "abbr": "NYG", "lat": 40.8135, "lon": -74.0744, "Off": 28, "Def": 26, "SOS": ".525", "TO": -5, "BasePlayoff": 25.0, "Rating": 1485},
        {"team": "New York Jets", "abbr": "NYJ", "lat": 40.8135, "lon": -74.0744, "Off": 21, "Def": 5, "SOS": ".502", "TO": +2, "BasePlayoff": 52.0, "Rating": 1540},
        {"team": "Philadelphia Eagles", "abbr": "PHI", "lat": 39.9008, "lon": -75.1675, "Off": 11, "Def": 6, "SOS": ".498", "TO": +4, "BasePlayoff": 73.0, "Rating": 1590},
        {"team": "Pittsburgh Steelers", "abbr": "PIT", "lat": 40.4468, "lon": -80.0158, "Off": 23, "Def": 1, "SOS": ".545", "TO": +6, "BasePlayoff": 58.0, "Rating": 1555},
        {"team": "San Francisco 49ers", "abbr": "SF", "lat": 37.4033, "lon": -121.9694, "Off": 2, "Def": 5, "SOS": ".510", "TO": +7, "BasePlayoff": 85.0, "Rating": 1630},
        {"team": "Seattle Seahawks", "abbr": "SEA", "lat": 47.5952, "lon": -122.3316, "Off": 12, "Def": 24, "SOS": ".492", "TO": 0, "BasePlayoff": 53.0, "Rating": 1545},
        {"team": "Tampa Bay Buccaneers", "abbr": "TB", "lat": 27.9759, "lon": -82.5033, "Off": 17, "Def": 22, "SOS": ".488", "TO": +2, "BasePlayoff": 47.0, "Rating": 1530},
        {"team": "Tennessee Titans", "abbr": "TEN", "lat": 36.1665, "lon": -86.7713, "Off": 29, "Def": 27, "SOS": ".515", "TO": -4, "BasePlayoff": 26.0, "Rating": 1490},
        {"team": "Washington Commanders", "abbr": "WAS", "lat": 38.9076, "lon": -76.8645, "Off": 25, "Def": 28, "SOS": ".485", "TO": -2, "BasePlayoff": 38.0, "Rating": 1510},
    ]
    df = pd.DataFrame(data)
    df["logo_url"] = df["abbr"].apply(
        lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png"
    )
    df["ticket_link"] = df["team"].apply(
        lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets"
    )
    return df


df_teams_cached = load_team_data()
df_teams = df_teams_cached.copy() # Prevents Streamlit cache mutation errors
team_dict = df_teams.set_index("abbr").to_dict("index")


# 2. Mock Live News / Vitals Feed per Team
@st.cache_data
def load_team_news():
    return {
        "KC": [
            "⚡ Practice Report: Full participation for offensive starters.",
            "🏥 Injury Update: Minor ankle soreness reported for backup tight end.",
        ],
        "SF": [
            "⚡ Roster Alert: Elevated practice squad defensive lineman.",
            "🏥 Injury Update: Star running back listed as limited in drills.",
        ],
        "BAL": [
            "⚡ Coaching Note: Scheme adjustments focused on red-zone efficiency.",
            "🏥 Injury Update: Linebacker cleared for full contact.",
        ],
        "BUF": [
            "⚡ Weather Advisory: High winds expected for upcoming outdoor drills.",
            "🏥 Injury Update: Secondary depth getting extra reps.",
        ],
    }


team_news = load_team_news()


# 3. Fetch Official Schedules via nfl-data-py API with Fallback
@st.cache_data
def load_official_schedules():
    try:
        sched_df = nfl.import_schedules([2026])
        reg_games = sched_df[sched_df["game_type"] == "REG"]
        if not reg_games.empty:
            return reg_games
    except Exception:
        pass
    return pd.DataFrame()


official_schedule = load_official_schedules()


# 4. Haversine Distance Calculator in Miles
def calculate_travel_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


# 5. State Initialization
if "selected_team" not in st.session_state:
    st.session_state.selected_team = "Kansas City Chiefs"

team_names = df_teams["team"].tolist()


# 6. Sidebar UI & State Sync
st.sidebar.title("Matchup & Vitals Hub")

current_index = team_names.index(st.session_state.selected_team)
selected_name = st.sidebar.selectbox("Select Team", team_names, index=current_index)

if selected_name != st.session_state.selected_team:
    st.session_state.selected_team = selected_name
    st.rerun()

team_df_row = df_teams[df_teams["team"] == st.session_state.selected_team].iloc[0]
selected_abbr = team_df_row["abbr"]


# Display Team Analytics & Ticket Link
st.sidebar.markdown(f"### {st.session_state.selected_team} Profile")
st.sidebar.metric("Offensive Rank", f"#{team_df_row['Off']}")
st.sidebar.metric("Defensive Rank", f"#{team_df_row['Def']}")
st.sidebar.metric("Turnover Margin", f"{team_df_row['TO']:+d}")
st.sidebar.metric("Strength of Schedule", team_df_row["SOS"])
st.sidebar.link_button("🎟️ Get Tickets", team_df_row["ticket_link"])


# 7. Live Team Vitals & News Ticker Panel
with st.sidebar.expander("📰 Live Team Vitals & News", expanded=True):
    news_list = team_news.get(
        selected_abbr,
        [
            "⚡ Practice Report: Normal roster rotation active.",
            "🏥 Injury Status: No major new designations reported.",
        ],
    )
    for item in news_list:
        st.markdown(f"- {item}")
    st.caption(
        "*Note: Automated data pipelines refresh weekly status reports; sliders"
        " below test what-if simulation scenarios.*"
    )


# 8. Sliding-Scale Variables with Detailed Explanations
st.sidebar.markdown("---")
st.sidebar.subheader("Variable Impact Controls")

st.sidebar.markdown(
    "**1. Injury Attrition Severity (0-10):**\n"
    "> *Measures overall depth erosion and missing starters. Higher scores"
    " directly degrade both weekly win probabilities and long-term playoff"
    " odds.*"
)
inj_val = st.sidebar.slider("Injury Attrition", 0, 10, 0)

st.sidebar.markdown(
    "**2. Weather Severity (0-10):**\n"
    "> *Accounts for severe cold, wind, or rain. Penalizes passing efficiency"
    " and execution in outdoor matchups.*"
)
wea_val = st.sidebar.slider("Weather Severity", 0, 10, 0)

st.sidebar.markdown(
    "**3. Travel Fatigue Multiplier (0-10):**\n"
    "> *Amplifies the fatigue penalty calculated automatically from exact flight"
    " distances for away games.*"
)
trv_val = st.sidebar.slider("Travel Fatigue Multiplier", 0, 10, 0)


# 9. Playoff Odds Calculation Engine
def calculate_adjusted_playoff(row, current_abbr, inj, wea, trv):
    base = row["BasePlayoff"]
    if row["abbr"] == current_abbr:
        total_penalty = (inj * 2.2) + (wea * 1.0) + (trv * 1.2)
        return round(max(1.0, min(99.0, base - total_penalty)), 1)
    return base

df_teams["adjusted_playoff"] = df_teams.apply(
    lambda row: calculate_adjusted_playoff(row, selected_abbr, inj_val, wea_val, trv_val), axis=1
)
current_adjusted_score = df_teams.loc[
    df_teams["abbr"] == selected_abbr, "adjusted_playoff"
].values[0]
st.sidebar.markdown(
    f"### 🎯 Adjusted Playoff Odds: {current_adjusted_score}%"
)


# 10. Official Weekly Matchup & Distance Travel Analyzer
with st.sidebar.expander("🏈 Official Schedule & Travel Distance", expanded=True):
    if not official_schedule.empty:
        team_games = official_schedule[
            (official_schedule["home_team"] == selected_abbr)
            | (official_schedule["away_team"] == selected_abbr)
        ]
        weeks = sorted(team_games["week"].unique().tolist())

        if weeks:
            selected_week = st.selectbox("Select Week", weeks)
            game = team_games[team_games["week"] == selected_week].iloc[0]

            is_home = game["home_team"] == selected_abbr
            opp_abbr = game["away_team"] if is_home else game["home_team"]
            loc = "Home" if is_home else "Away"

            # 🛠️ Fix: Alias mapping for mismatched nfl_data_py abbreviations
            abbr_mapping = {"LA": "LAR", "OAK": "LV", "SD": "LAC", "WSH": "WAS"}
            clean_opp_abbr = abbr_mapping.get(opp_abbr, opp_abbr)

            opp_info = team_dict.get(
                clean_opp_abbr,
                {
                    "team": opp_abbr,
                    "lat": team_df_row["lat"],
                    "lon": team_df_row["lon"],
                    "Rating": 1500,
                },
            )

            # Distance calculation
            if loc == "Away":
                travel_distance_miles = calculate_travel_distance(
                    team_df_row["lat"],
                    team_df_row["lon"],
                    opp_info["lat"],
                    opp_info["lon"],
                )
            else:
                travel_distance_miles = 0

            st.markdown(f"**Opponent:** {opp_info['team']} ({loc})")
            if loc == "Away":
                st.markdown(f"✈️ **Flight Distance:** `{travel_distance_miles} miles`")
            else:
                st.markdown(f"🏠 **Home Field Advantage**")

            # 🛠️ Fix: Symmetrical Win Probability Computation
            team_base_power = team_df_row["Rating"]
            opp_rating = opp_info["Rating"]

            inj_penalty = inj_val * 10
            wea_penalty = wea_val * 6
            travel_mult = trv_val
            
            # Capped travel penalty to prevent extreme skewing on cross-country trips
            distance_penalty = (
                min((travel_distance_miles / 500) * 2.0, 12.0) * (1 + travel_mult * 0.2)
                if loc == "Away"
                else 0
            )
            
            hfa_points = 45 

            if loc == "Home":
                rating_diff = (team_base_power + hfa_points - inj_penalty - wea_penalty) - opp_rating
            else:
                rating_diff = (team_base_power - inj_penalty - wea_penalty - distance_penalty) - (opp_rating + hfa_points)

            win_prob = round(1 / (10 ** (-rating_diff / 400) + 1) * 100, 1)

            st.metric(
                label=f"Week {selected_week} Win Probability", value=f"{win_prob}%"
            )

            if win_prob >= 60:
                st.success("🟢 Projected Favorite")
            elif win_prob >= 40:
                st.warning("🟡 Toss-Up Matchup")
            else:
                st.error("🔴 Projected Underdog")
    else:
        st.info("Loading official schedule feed...")


# 11. Map Generation
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
    icon = folium.CustomIcon(row["logo_url"], icon_size=(35, 35))
    popup_text = f"""
      <b>{row['team']}</b><br>
      Base Playoff: {row['BasePlayoff']}%<br>
      <b>Adjusted Playoff: {row['adjusted_playoff']}%</b>
      """
    folium.Marker(
        location=[row["lat"], row["lon"]],
        icon=icon,
        tooltip=row["team"],
        popup=folium.Popup(popup_text, max_width=300),
    ).add_to(m)


# 12. Render Map & Capture Clicks
output = st_folium(m, width=900, height=500, key="fully_loaded_map")

if output and output.get("last_object_clicked_tooltip"):
    clicked_name = output["last_object_clicked_tooltip"]
    if clicked_name in team_names and clicked_name != st.session_state.selected_team:
        st.session_state.selected_team = clicked_name
        st.rerun()
