import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="NFL Advanced Schedule & Variable Simulator", layout="wide"
)

st.title("NFL Matchup, Schedule & Variable Impact Simulator")
st.markdown(
    "**Click any team's logo on the map** or use the sidebar dropdown to inspect"
    " their schedule, view travel/location context, and adjust sliding-scale"
    " variables (**Injuries, Weather, Travel Fatigue**) to see real-time shifts"
    " in postseason odds."
)


# 1. Complete 32-Team Dataset with Stats, Ticket Links, and Sample Schedule Context
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

# Sample schedule context generator per team for previewing travel & location impact
@st.cache_data
def load_sample_schedules():
  return {
      "KC": [
          {"Week": 1, "Opponent": "vs BAL", "Location": "Home", "Travel": "None"},
          {
              "Week": 2,
              "Opponent": "@ LAC",
              "Location": "Away",
              "Travel": "West Coast (Long)",
          },
          {
              "Week": 3,
              "Opponent": "@ ATL",
              "Location": "Away",
              "Travel": "East Coast (Medium)",
          },
          {"Week": 4, "Opponent": "vs LAC", "Location": "Home", "Travel": "None"},
      ],
      "SF": [
          {"Week": 1, "Opponent": "vs NYJ", "Location": "Home", "Travel": "None"},
          {
              "Week": 2,
              "Opponent": "@ MIN",
              "Location": "Away",
              "Travel": "Midwest (Long)",
          },
          {
              "Week": 3,
              "Opponent": "@ LAR",
              "Location": "Away",
              "Travel": "Division (Short)",
          },
          {"Week": 4, "Opponent": "vs NE", "Location": "Home", "Travel": "None"},
      ],
      "BAL": [
          {"Week": 1, "Opponent": "@ KC", "Location": "Away", "Travel": "Midwest"},
          {
              "Week": 2,
              "Opponent": "vs LV",
              "Location": "Home",
              "Travel": "None",
          },
          {
              "Week": 3,
              "Opponent": "@ DAL",
              "Location": "Away",
              "Travel": "South",
          },
          {
              "Week": 4,
              "Opponent": "vs BUF",
              "Location": "Home",
              "Travel": "None",
          },
      ],
  }


team_schedules = load_sample_schedules()

# 2. State Initialization
if "selected_team" not in st.session_state:
  st.session_state.selected_team = "Kansas City Chiefs"

team_names = df_teams["team"].tolist()

# 3. Sidebar UI & State Sync
st.sidebar.title("Matchup & Variable Hub")

current_index = team_names.index(st.session_state.selected_team)
selected_name = st.sidebar.selectbox("Select Team", team_names, index=current_index)

if selected_name != st.session_state.selected_team:
  st.session_state.selected_team = selected_name
  st.rerun()

team_row = df_teams[df_teams["team"] == st.session_state.selected_team].iloc[0]
selected_abbr = team_row["abbr"]

# Display Analytics & Ticket Links
st.sidebar.markdown(f"### {team_row['team']} Profile")
st.sidebar.metric("Offensive Rank", f"#{team_row['Off']}")
st.sidebar.metric("Defensive Rank", f"#{team_row['Def']}")
st.sidebar.metric("Turnover Margin", f"{team_row['TO']:+d}")
st.sidebar.metric("Strength of Schedule", team_row["SOS"])
st.sidebar.link_button("🎟️ Get Tickets", team_row["ticket_link"])

# 4. Sliding-Scale Variables for Injuries, Weather, and Travel
st.sidebar.markdown("---")
st.sidebar.subheader("Variable Impact Controls")

injury_slider = st.sidebar.slider(
    "Injury Attrition Severity", 0, 10, 0, key=f"inj_{selected_abbr}"
)
weather_slider = st.sidebar.slider(
    "Weather Severity (Cold/Wind/Rain)", 0, 10, 0, key=f"wea_{selected_abbr}"
)
travel_slider = st.sidebar.slider(
    "Travel Fatigue / Short Rest", 0, 10, 0, key=f"trv_{selected_abbr}"
)

# 5. Dynamic Calculation Engine combining Variables
def calculate_adjusted_playoff(row):
  base = row["BasePlayoff"]
  abbr = row["abbr"]

  # Retrieve current slider values for this team
  inj = st.session_state.get(f"inj_{abbr}", 0)
  wea = st.session_state.get(f"wea_{abbr}", 0)
  trv = st.session_state.get(f"trv_{abbr}", 0)

  # Combined penalty deduction formula
  total_penalty = (inj * 2.5) + (wea * 1.0) + (trv * 1.2)
  return round(max(1.0, min(99.0, base - total_penalty)), 1)


df_teams["adjusted_playoff"] = df_teams.apply(
    calculate_adjusted_playoff, axis=1
)

# Current selected team's calculated score for display
current_adjusted_score = df_teams.loc[
    df_teams["abbr"] == selected_abbr, "adjusted_playoff"
].values[0]
st.sidebar.markdown(f"**Adjusted Playoff Odds: {current_adjusted_score}%**")

# 6. Display Team Schedule & Travel Context in Sidebar Expander
with st.sidebar.expander("📅 Team Schedule & Travel Context", expanded=True):
  sched = team_schedules.get(
      selected_abbr,
      [
          {"Week": 1, "Opponent": "Upcoming Game", "Location": "Home", "Travel": "None"},
          {"Week": 2, "Opponent": "Away Fixture", "Location": "Away", "Travel": "Cross-Country"},
      ],
  )
  for game in sched:
    st.markdown(
        f"**Wk {game['Week']}**: {game['Opponent']} | *{game['Location']}* |"
        f" Travel: {game['Travel']}"
    )

# 7. Map Generation
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

# 8. Render Map & Capture Reliable Clicks
output = st_folium(m, width=900, height=500, key="variable_map")

if output and output.get("last_object_clicked_tooltip"):
  clicked_name = output["last_object_clicked_tooltip"]
  if clicked_name in team_names and clicked_name != st.session_state.selected_team:
    st.session_state.selected_team = clicked_name
    st.rerun()