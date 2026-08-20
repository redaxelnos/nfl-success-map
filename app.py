import nfl_data_py as nfl
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Live Automated NFL Success & Injury Map", layout="wide"
)

st.title("Live NFL Success & Automated Roster Resilience Dashboard")
st.markdown(
    "Powered by live `nflverse` data pipelines. This map automatically tracks"
    " official weekly injury designations and applies positional value weighting"
    " to dynamically re-calculate team success metrics."
)


# 1. Fetch Live Data with Streamlit Caching
@st.cache_data(ttl=3600)  # Refreshes automatically every hour
def load_live_data():
  current_year = 2026
  # Pull official injury reports
  injuries_df = nfl.import_injuries([current_year])
  return injuries_df


try:
  live_injuries = load_live_data()
except Exception:
  live_injuries = pd.DataFrame()  # Fallback if offline

# 2. Comprehensive 32-Team Baseline Dataset
@st.cache_data
def load_team_baselines():
  data = [
      {
          "team": "Arizona Cardinals",
          "abbr": "ARI",
          "lat": 33.5276,
          "lon": -112.2626,
          "Elo": 1500,
          "Wins": 7.5,
      },
      {
          "team": "Atlanta Falcons",
          "abbr": "ATL",
          "lat": 33.7554,
          "lon": -84.4010,
          "Elo": 1520,
          "Wins": 8.5,
      },
      {
          "team": "Baltimore Ravens",
          "abbr": "BAL",
          "lat": 39.2779,
          "lon": -76.6227,
          "Elo": 1620,
          "Wins": 11.0,
      },
      {
          "team": "Buffalo Bills",
          "abbr": "BUF",
          "lat": 42.7738,
          "lon": -78.7870,
          "Elo": 1610,
          "Wins": 10.5,
      },
      {
          "team": "Carolina Panthers",
          "abbr": "CAR",
          "lat": 35.2258,
          "lon": -80.8528,
          "Elo": 1470,
          "Wins": 5.5,
      },
      {
          "team": "Chicago Bears",
          "abbr": "CHI",
          "lat": 41.8623,
          "lon": -87.6167,
          "Elo": 1510,
          "Wins": 8.0,
      },
      {
          "team": "Cincinnati Bengals",
          "abbr": "CIN",
          "lat": 39.0955,
          "lon": -84.5160,
          "Elo": 1580,
          "Wins": 10.0,
      },
      {
          "team": "Cleveland Browns",
          "abbr": "CLE",
          "lat": 41.5061,
          "lon": -81.6995,
          "Elo": 1530,
          "Wins": 8.5,
      },
      {
          "team": "Dallas Cowboys",
          "abbr": "DAL",
          "lat": 32.7473,
          "lon": -97.0945,
          "Elo": 1590,
          "Wins": 10.5,
      },
      {
          "team": "Denver Broncos",
          "abbr": "DEN",
          "lat": 39.7439,
          "lon": -105.0201,
          "Elo": 1505,
          "Wins": 7.5,
      },
      {
          "team": "Detroit Lions",
          "abbr": "DET",
          "lat": 42.3400,
          "lon": -83.0456,
          "Elo": 1600,
          "Wins": 10.5,
      },
      {
          "team": "Green Bay Packers",
          "abbr": "GB",
          "lat": 44.5013,
          "lon": -88.0622,
          "Elo": 1585,
          "Wins": 10.0,
      },
      {
          "team": "Houston Texans",
          "abbr": "HOU",
          "lat": 29.6847,
          "lon": -95.4107,
          "Elo": 1575,
          "Wins": 9.5,
      },
      {
          "team": "Indianapolis Colts",
          "abbr": "IND",
          "lat": 39.7601,
          "lon": -86.1639,
          "Elo": 1515,
          "Wins": 8.0,
      },
      {
          "team": "Jacksonville Jaguars",
          "abbr": "JAX",
          "lat": 30.3239,
          "lon": -81.6373,
          "Elo": 1525,
          "Wins": 8.5,
      },
      {
          "team": "Kansas City Chiefs",
          "abbr": "KC",
          "lat": 39.0489,
          "lon": -94.4839,
          "Elo": 1650,
          "Wins": 11.5,
      },
      {
          "team": "Las Vegas Raiders",
          "abbr": "LV",
          "lat": 36.0909,
          "lon": -115.1833,
          "Elo": 1495,
          "Wins": 6.5,
      },
      {
          "team": "Los Angeles Chargers",
          "abbr": "LAC",
          "lat": 33.9535,
          "lon": -118.3390,
          "Elo": 1550,
          "Wins": 9.0,
      },
      {
          "team": "Los Angeles Rams",
          "abbr": "LAR",
          "lat": 33.9535,
          "lon": -118.3390,
          "Elo": 1565,
          "Wins": 9.5,
      },
      {
          "team": "Miami Dolphins",
          "abbr": "MIA",
          "lat": 25.9580,
          "lon": -80.2389,
          "Elo": 1570,
          "Wins": 9.5,
      },
      {
          "team": "Minnesota Vikings",
          "abbr": "MIN",
          "lat": 44.9738,
          "lon": -93.2575,
          "Elo": 1535,
          "Wins": 8.0,
      },
      {
          "team": "New England Patriots",
          "abbr": "NE",
          "lat": 42.0909,
          "lon": -71.2643,
          "Elo": 1480,
          "Wins": 6.0,
      },
      {
          "team": "New Orleans Saints",
          "abbr": "NO",
          "lat": 29.9511,
          "lon": -90.0812,
          "Elo": 1520,
          "Wins": 8.0,
      },
      {
          "team": "New York Giants",
          "abbr": "NYG",
          "lat": 40.8135,
          "lon": -74.0744,
          "Elo": 1485,
          "Wins": 6.5,
      },
      {
          "team": "New York Jets",
          "abbr": "NYJ",
          "lat": 40.8135,
          "lon": -74.0744,
          "Elo": 1540,
          "Wins": 9.0,
      },
      {
          "team": "Philadelphia Eagles",
          "abbr": "PHI",
          "lat": 39.9008,
          "lon": -75.1675,
          "Elo": 1590,
          "Wins": 10.0,
      },
      {
          "team": "Pittsburgh Steelers",
          "abbr": "PIT",
          "lat": 40.4468,
          "lon": -80.0158,
          "Elo": 1555,
          "Wins": 9.0,
      },
      {
          "team": "San Francisco 49ers",
          "abbr": "SF",
          "lat": 37.4033,
          "lon": -121.9694,
          "Elo": 1630,
          "Wins": 11.0,
      },
      {
          "team": "Seattle Seahawks",
          "abbr": "SEA",
          "lat": 47.5952,
          "lon": -122.3316,
          "Elo": 1545,
          "Wins": 8.5,
      },
      {
          "team": "Tampa Bay Buccaneers",
          "abbr": "TB",
          "lat": 27.9759,
          "lon": -82.5033,
          "Elo": 1530,
          "Wins": 8.5,
      },
      {
          "team": "Tennessee Titans",
          "abbr": "TEN",
          "lat": 36.1665,
          "lon": -86.7713,
          "Elo": 1490,
          "Wins": 6.5,
      },
      {
          "team": "Washington Commanders",
          "abbr": "WAS",
          "lat": 38.9076,
          "lon": -76.8645,
          "Elo": 1510,
          "Wins": 7.5,
      },
  ]
  return pd.DataFrame(data)


df_teams = load_team_baselines()

# 3. Sidebar Configuration
st.sidebar.header("Live Control Center")
success_metric = st.sidebar.selectbox("Success Metric", ["Elo", "Wins"])

# Granular Positional Weighting Multipliers
st.sidebar.markdown("---")
st.sidebar.subheader("Positional Injury Penalties")
qb_penalty = st.sidebar.slider("QB1 Injury Penalty Value", 0.0, 30.0, 15.0)
star_penalty = st.sidebar.slider(
    "Key Starter (WR/Edge/OT) Penalty", 0.0, 15.0, 5.0
)

# 4. Process Live Injuries & Calculate Attrition
def calculate_live_score(row):
  base_val = row[success_metric]
  team_abbr = row["abbr"]

  penalty_total = 0.0
  if not live_injuries.empty and "team" in live_injuries.columns:
    # Filter live injury report for players listed as 'Out' or 'Doubtful' on this team
    team_injuries = live_injuries[
        (live_injuries["team"] == team_abbr)
        & (
            live_injuries["report_status"].isin(["Out", "Doubtful", "IR"])
            if "report_status" in live_injuries.columns
            else False
        )
    ]
    for _, inj in team_injuries.iterrows():
      pos = (
          inj.get("position", "")
          if "position" in team_injuries.columns
          else ""
      )
      if pos == "QB":
        penalty_total += qb_penalty
      elif pos in ["WR", "T", "DE", "CB"]:
        penalty_total += star_penalty
      else:
        penalty_total += 1.5

  adjusted = max(0, base_val - penalty_total)
  return round(adjusted, 1)


df_teams["adjusted_score"] = df_teams.apply(calculate_live_score, axis=1)


# Color mapping logic
def get_color(score, metric_type):
  if metric_type == "Elo":
    return "green" if score >= 1560 else ("orange" if score >= 1510 else "red")
  else:
    return "green" if score >= 9.5 else ("orange" if score >= 7.5 else "red")


# 5. Build Interactive Map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
  color = get_color(row["adjusted_score"], success_metric)
  popup_text = f"""
    <b>{row['team']} ({row['abbr']})</b><br>
    Baseline {success_metric}: {row[success_metric]}<br>
    <b>Adjusted Score: {row['adjusted_score']}</b>
    """

  radius_val = (
      row["adjusted_score"] / 80
      if success_metric == "Elo"
      else row["adjusted_score"] * 1.5
  )

  folium.CircleMarker(
      location=[row["lat"], row["lon"]],
      radius=radius_val,
      color=color,
      fill=True,
      fill_color=color,
      fill_opacity=0.7,
      popup=folium.Popup(popup_text, max_width=300),
      tooltip=row["team"],
  ).add_to(m)

st_folium(m, width=1100, height=650)