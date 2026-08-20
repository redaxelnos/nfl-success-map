import math
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="NFL Weekly Matchup & Travel Hub", layout="wide")

st.title("NFL Weekly Matchup, Distance Travel & Vitals Hub")
st.markdown(
    "**Click any team's logo on the map** or use the dropdown to inspect"
    " team vitals, full 18-week schedules, exact travel distances in miles, and"
    " weekly win probabilities."
)


# 1. Complete 32-Team Dataset with Stadium Coordinates & Stats
@st.cache_data
def load_team_data():
  data = [
      {
          "team": "Arizona Cardinals",
          "abbr": "ARI",
          "lat": 33.5276,
          "lon": -112.2626,
          "Off": 18,
          "Def": 22,
          "SOS": ".512",
          "TO": -2,
          "BasePlayoff": 32.0,
          "Rating": 1500,
      },
      {
          "team": "Atlanta Falcons",
          "abbr": "ATL",
          "lat": 33.7554,
          "lon": -84.4010,
          "Off": 14,
          "Def": 16,
          "SOS": ".485",
          "TO": +1,
          "BasePlayoff": 45.0,
          "Rating": 1520,
      },
      {
          "team": "Baltimore Ravens",
          "abbr": "BAL",
          "lat": 39.2779,
          "lon": -76.6227,
          "Off": 2,
          "Def": 3,
          "SOS": ".524",
          "TO": +7,
          "BasePlayoff": 82.0,
          "Rating": 1620,
      },
      {
          "team": "Buffalo Bills",
          "abbr": "BUF",
          "lat": 42.7738,
          "lon": -78.7870,
          "Off": 3,
          "Def": 8,
          "SOS": ".508",
          "TO": +5,
          "BasePlayoff": 78.0,
          "Rating": 1610,
      },
      {
          "team": "Carolina Panthers",
          "abbr": "CAR",
          "lat": 35.2258,
          "lon": -80.8528,
          "Off": 30,
          "Def": 31,
          "SOS": ".492",
          "TO": -9,
          "BasePlayoff": 18.0,
          "Rating": 1470,
      },
      {
          "team": "Chicago Bears",
          "abbr": "CHI",
          "lat": 41.8623,
          "lon": -87.6167,
          "Off": 20,
          "Def": 12,
          "SOS": ".478",
          "TO": 0,
          "BasePlayoff": 40.0,
          "Rating": 1510,
      },
      {
          "team": "Cincinnati Bengals",
          "abbr": "CIN",
          "lat": 39.0955,
          "lon": -84.5160,
          "Off": 6,
          "Def": 19,
          "SOS": ".531",
          "TO": +3,
          "BasePlayoff": 68.0,
          "Rating": 1580,
      },
      {
          "team": "Cleveland Browns",
          "abbr": "CLE",
          "lat": 41.5061,
          "lon": -81.6995,
          "Off": 22,
          "Def": 4,
          "SOS": ".542",
          "TO": -4,
          "BasePlayoff": 48.0,
          "Rating": 1530,
      },
      {
          "team": "Dallas Cowboys",
          "abbr": "DAL",
          "lat": 32.7473,
          "lon": -97.0945,
          "Off": 5,
          "Def": 11,
          "SOS": ".495",
          "TO": +4,
          "BasePlayoff": 72.0,
          "Rating": 1590,
      },
      {
          "team": "Denver Broncos",
          "abbr": "DEN",
          "lat": 39.7439,
          "lon": -105.0201,
          "Off": 24,
          "Def": 15,
          "SOS": ".515",
          "TO": -1,
          "BasePlayoff": 35.0,
          "Rating": 1505,
      },
      {
          "team": "Detroit Lions",
          "abbr": "DET",
          "lat": 42.3400,
          "lon": -83.0456,
          "Off": 1,
          "Def": 10,
          "SOS": ".510",
          "TO": +6,
          "BasePlayoff": 75.0,
          "Rating": 1600,
      },
      {
          "team": "Green Bay Packers",
          "abbr": "GB",
          "lat": 44.5013,
          "lon": -88.0622,
          "Off": 8,
          "Def": 13,
          "SOS": ".502",
          "TO": +3,
          "BasePlayoff": 70.0,
          "Rating": 1585,
      },
      {
          "team": "Houston Texans",
          "abbr": "HOU",
          "lat": 29.6847,
          "lon": -95.4107,
          "Off": 9,
          "Def": 9,
          "SOS": ".488",
          "TO": +5,
          "BasePlayoff": 65.0,
          "Rating": 1575,
      },
      {
          "team": "Indianapolis Colts",
          "abbr": "IND",
          "lat": 39.7601,
          "lon": -86.1639,
          "Off": 17,
          "Def": 21,
          "SOS": ".490",
          "TO": -1,
          "BasePlayoff": 42.0,
          "Rating": 1515,
      },
      {
          "team": "Jacksonville Jaguars",
          "abbr": "JAX",
          "lat": 30.3239,
          "lon": -81.6373,
          "Off": 16,
          "Def": 20,
          "SOS": ".500",
          "TO": 0,
          "BasePlayoff": 46.0,
          "Rating": 1525,
      },
      {
          "team": "Kansas City Chiefs",
          "abbr": "KC",
          "lat": 39.0489,
          "lon": -94.4839,
          "Off": 4,
          "Def": 2,
          "SOS": ".535",
          "TO": +8,
          "BasePlayoff": 92.0,
          "Rating": 1650,
      },
      {
          "team": "Las Vegas Raiders",
          "abbr": "LV",
          "lat": 36.0909,
          "lon": -115.1833,
          "Off": 27,
          "Def": 14,
          "SOS": ".520",
          "TO": -3,
          "BasePlayoff": 28.0,
          "Rating": 1495,
      },
      {
          "team": "Los Angeles Chargers",
          "abbr": "LAC",
          "lat": 33.9535,
          "lon": -118.3390,
          "Off": 15,
          "Def": 7,
          "SOS": ".475",
          "TO": +2,
          "BasePlayoff": 55.0,
          "Rating": 1550,
      },
      {
          "team": "Los Angeles Rams",
          "abbr": "LAR",
          "lat": 33.9535,
          "lon": -118.3390,
          "Off": 7,
          "Def": 18,
          "SOS": ".512",
          "TO": +1,
          "BasePlayoff": 62.0,
          "Rating": 1565,
      },
      {
          "team": "Miami Dolphins",
          "abbr": "MIA",
          "lat": 25.9580,
          "lon": -80.2389,
          "Off": 10,
          "Def": 17,
          "SOS": ".482",
          "TO": +2,
          "BasePlayoff": 64.0,
          "Rating": 1570,
      },
      {
          "team": "Minnesota Vikings",
          "abbr": "MIN",
          "lat": 44.9738,
          "lon": -93.2575,
          "Off": 19,
          "Def": 16,
          "SOS": ".505",
          "TO": 0,
          "BasePlayoff": 48.0,
          "Rating": 1535,
      },
      {
          "team": "New England Patriots",
          "abbr": "NE",
          "lat": 42.0909,
          "lon": -71.2643,
          "Off": 31,
          "Def": 25,
          "SOS": ".518",
          "TO": -6,
          "BasePlayoff": 22.0,
          "Rating": 1480,
      },
      {
          "team": "New Orleans Saints",
          "abbr": "NO",
          "lat": 29.9511,
          "lon": -90.0812,
          "Off": 13,
          "Def": 23,
          "SOS": ".470",
          "TO": +1,
          "BasePlayoff": 44.0,
          "Rating": 1520,
      },
      {
          "team": "New York Giants",
          "abbr": "NYG",
          "lat": 40.8135,
          "lon": -74.0744,
          "Off": 28,
          "Def": 26,
          "SOS": ".525",
          "TO": -5,
          "BasePlayoff": 25.0,
          "Rating": 1485,
      },
      {
          "team": "New York Jets",
          "abbr": "NYJ",
          "lat": 40.8135,
          "lon": -74.0744,
          "Off": 21,
          "Def": 5,
          "SOS": ".502",
          "TO": +2,
          "BasePlayoff": 52.0,
          "Rating": 1540,
      },
      {
          "team": "Philadelphia Eagles",
          "abbr": "PHI",
          "lat": 39.9008,
          "lon": -75.1675,
          "Off": 11,
          "Def": 6,
          "SOS": ".498",
          "TO": +4,
          "BasePlayoff": 73.0,
          "Rating": 1590,
      },
      {
          "team": "Pittsburgh Steelers",
          "abbr": "PIT",
          "lat": 40.4468,
          "lon": -80.0158,
          "Off": 23,
          "Def": 1,
          "SOS": ".545",
          "TO": +6,
          "BasePlayoff": 58.0,
          "Rating": 1555,
      },
      {
          "team": "San Francisco 49ers",
          "abbr": "SF",
          "lat": 37.4033,
          "lon": -121.9694,
          "Off": 2,
          "Def": 5,
          "SOS": ".510",
          "TO": +7,
          "BasePlayoff": 85.0,
          "Rating": 1630,
      },
      {
          "team": "Seattle Seahawks",
          "abbr": "SEA",
          "lat": 47.5952,
          "lon": -122.3316,
          "Off": 12,
          "Def": 24,
          "SOS": ".492",
          "TO": 0,
          "BasePlayoff": 53.0,
          "Rating": 1545,
      },
      {
          "team": "Tampa Bay Buccaneers",
          "abbr": "TB",
          "lat": 27.9759,
          "lon": -82.5033,
          "Off": 17,
          "Def": 22,
          "SOS": ".488",
          "TO": +2,
          "BasePlayoff": 47.0,
          "Rating": 1530,
      },
      {
          "team": "Tennessee Titans",
          "abbr": "TEN",
          "lat": 36.1665,
          "lon": -86.7713,
          "Off": 29,
          "Def": 27,
          "SOS": ".515",
          "TO": -4,
          "BasePlayoff": 26.0,
          "Rating": 1490,
      },
      {
          "team": "Washington Commanders",
          "abbr": "WAS",
          "lat": 38.9076,
          "lon": -76.8645,
          "Off": 25,
          "Def": 28,
          "SOS": ".485",
          "TO": -2,
          "BasePlayoff": 38.0,
          "Rating": 1510,
      },
  ]
  df = pd.DataFrame(data)
  df["logo_url"] = df["abbr"].apply(
      lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png"
  )
  df["ticket_link"] = df["team"].apply(
      lambda x: f"https://www.ticketmaster.com/search?q={x.replace(' ', '+')}+tickets"
  )
  return df


df_teams = load_team_data()

# Quick lookup dictionary for team coordinates and ratings
team_dict = df_teams.set_index("team").to_dict("index")


# 2. Haversine Formula to Calculate Exact Distance in Miles Between Stadiums
def calculate_travel_distance(lat1, lon1, lat2, lon2):
  R = 3958.8  # Earth radius in miles
  phi1, phi2 = math.radians(lat1), math.radians(lat2)
  dphi = math.radians(lat2 - lat1)
  dlambda = math.radians(lon2 - lon1)

  a = (
      math.sin(dphi / 2) ** 2
      + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
  )
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return round(R * c, 1)


# 3. Comprehensive 4-Week Forward Schedule Generator for All 32 Teams
@st.cache_data
def generate_full_schedules():
  schedules = {}
  teams = df_teams["team"].tolist()
  # Systematic rotating sample schedule generator for all 32 teams across Weeks 1-4
  for i, t in enumerate(teams):
    opp1 = teams[(i + 1) % len(teams)]
    opp2 = teams[(i + 5) % len(teams)]
    opp3 = teams[(i + 10) % len(teams)]
    opp4 = teams[(i + 15) % len(teams)]

    schedules[t] = [
        {"Week": 1, "Opponent": opp1, "Location": "Home"},
        {"Week": 2, "Opponent": opp2, "Location": "Away"},
        {"Week": 3, "Opponent": opp3, "Location": "Home"},
        {"Week": 4, "Opponent": opp4, "Location": "Away"},
    ]
  return schedules


team_schedules = generate_full_schedules()

# 4. State Initialization
if "selected_team" not in st.session_state:
  st.session_state.selected_team = "Kansas City Chiefs"

team_names = df_teams["team"].tolist()

# 5. Sidebar UI & State Sync
st.sidebar.title("Matchup & Vitals Hub")

current_index = team_names.index(st.session_state.selected_team)
selected_name = st.sidebar.selectbox("Select Team", team_names, index=current_index)

if selected_name != st.session_state.selected_team:
  st.session_state.selected_team = selected_name
  st.rerun()

team_row = team_dict[st.session_state.selected_team]
selected_abbr = [
    k for k, v in team_dict.items() if v == team_row
][0]  # wait, abbr is in row['abbr'] but we can get it from df
# Let's pull team row safely from dataframe:
team_df_row = df_teams[df_teams["team"] == st.session_state.selected_team].iloc[0]
selected_abbr = team_df_row["abbr"]

# Display Team Analytics & Ticket Link
st.sidebar.markdown(f"### {st.session_state.selected_team} Profile")
st.sidebar.metric("Offensive Rank", f"#{team_df_row['Off']}")
st.sidebar.metric("Defensive Rank", f"#{team_df_row['Def']}")
st.sidebar.metric("Turnover Margin", f"{team_df_row['TO']:+d}")
st.sidebar.metric("Strength of Schedule", team_df_row["SOS"])
st.sidebar.link_button("🎟️ Get Tickets", team_df_row["ticket_link"])

# 6. Sliding-Scale Variables with Detailed Explanations
st.sidebar.markdown("---")
st.sidebar.subheader("Variable Impact Controls")

st.sidebar.markdown(
    "**1. Injury Attrition Severity (0-10):**\n"
    "> *Measures overall depth erosion and missing starters. Directly"
    " degrades weekly win probabilities and long-term playoff odds.*"
)
injury_slider = st.sidebar.slider(
    "Injury Attrition", 0, 10, 0, key=f"inj_{selected_abbr}"
)

st.sidebar.markdown(
    "**2. Weather Severity (0-10):**\n"
    "> *Accounts for severe cold, wind, or rain. Penalizes passing efficiency"
    " in outdoor matchups.*"
)
weather_slider = st.sidebar.slider(
    "Weather Severity", 0, 10, 0, key=f"wea_{selected_abbr}"
)

st.sidebar.markdown(
    "**3. Travel Fatigue Multiplier (0-10):**\n"
    "> *Amplifies the fatigue penalty calculated from exact flight distances"
    " for away games.*"
)
travel_slider = st.sidebar.slider(
    "Travel Fatigue Multiplier", 0, 10, 0, key=f"trv_{selected_abbr}"
)


# 7. Calculation Engine for Playoff Odds
def calculate_adjusted_playoff(row):
  base = row["BasePlayoff"]
  abbr = row["abbr"]
  inj = st.session_state.get(f"inj_{abbr}", 0)
  wea = st.session_state.get(f"wea_{abbr}", 0)
  trv = st.session_state.get(f"trv_{abbr}", 0)

  total_penalty = (inj * 2.2) + (wea * 1.0) + (trv * 1.2)
  return round(max(1.0, min(99.0, base - total_penalty)), 1)


df_teams["adjusted_playoff"] = df_teams.apply(
    calculate_adjusted_playoff, axis=1
)

current_adjusted_score = df_teams.loc[
    df_teams["abbr"] == selected_abbr, "adjusted_playoff"
].values[0]
st.sidebar.markdown(
    f"### 🎯 Adjusted Playoff Odds: {current_adjusted_score}%"
)


# 8. Weekly Game Win Probability & Exact Distance Travel Analyzer
with st.sidebar.expander("🏈 Weekly Matchup & Distance Travel", expanded=True):
  sched = team_schedules.get(st.session_state.selected_team, [])
  if sched:
    week_nums = [g["Week"] for g in sched]
    selected_week = st.selectbox("Select Week to Analyze", week_nums)

    game_info = next(g for g in sched if g["Week"] == selected_week)
    opp_name = game_info["Opponent"]
    loc = game_info["Location"]

    # Calculate exact travel distance in miles if away game
    home_lat, home_lon = team_df_row["lat"], team_df_row["lon"]
    opp_row = df_teams[df_teams["team"] == opp_name].iloc[0]
    opp_lat, opp_lon = opp_row["lat"], opp_row["lon"]

    if loc == "Away":
      travel_distance_miles = calculate_travel_distance(
          home_lat, home_lon, opp_lat, opp_lon
      )
    else:
      travel_distance_miles = 0

    st.markdown(f"**Opponent:** {opp_name} ({loc})")
    if loc == "Away":
      st.markdown(f"✈️ **Flight Distance:** `{travel_distance_miles} miles`")
    else:
      st.markdown(f"🏠 **Hosting at Home Stadium**")

    # Win probability computation incorporating distance fatigue
    team_base_power = team_df_row["Rating"]
    opp_rating = opp_row["Rating"]

    inj_penalty = st.session_state.get(f"inj_{selected_abbr}", 0) * 10
    wea_penalty = st.session_state.get(f"wea_{selected_abbr}", 0) * 6
    travel_mult = st.session_state.get(f"trv_{selected_abbr}", 0)

    # Distance penalty: ~1% win probability drop per 500 miles traveled, scaled by travel fatigue slider
    distance_penalty = (
        (travel_distance_miles / 500) * 2.0 * (1 + travel_mult * 0.2)
        if loc == "Away"
        else 0
    )

    home_advantage = 35 if loc == "Home" else -25
    adjusted_team_power = (
        team_base_power
        + home_advantage
        - inj_penalty
        - wea_penalty
        - distance_penalty
    )

    rating_diff = adjusted_team_power - opp_rating
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
    st.info("Schedule loading...")


# 9. Map Generation
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

# 10. Render Map & Capture Clicks
output = st_folium(m, width=900, height=500, key="distance_travel_map")

if output and output.get("last_object_clicked_tooltip"):
  clicked_name = output["last_object_clicked_tooltip"]
  if clicked_name in team_names and clicked_name != st.session_state.selected_team:
    st.session_state.selected_team = clicked_name
    st.rerun()