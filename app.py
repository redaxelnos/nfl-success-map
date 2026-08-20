import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="NFL 32-Team Success & Roster Resilience Map", layout="wide"
)

st.title("NFL League-Wide Success & Injury Impact Dashboard")
st.markdown(
    "Explore projected success metrics across all 32 NFL teams. Use the sidebar"
    " to select your preferred analytical metric and simulate roster attrition"
    " from injuries in real time."
)

# 1. Comprehensive 32-Team Dataset (Coordinates & Baseline Power Ratings)
@st.cache_data
def load_all_teams_data():
  data = [
      {
          "team": "Arizona Cardinals",
          "lat": 33.5276,
          "lon": -112.2626,
          "Elo": 1500,
          "Wins": 7.5,
          "DVOA": -4.2,
      },
      {
          "team": "Atlanta Falcons",
          "lat": 33.7554,
          "lon": -84.4010,
          "Elo": 1520,
          "Wins": 8.5,
          "DVOA": -1.5,
      },
      {
          "team": "Baltimore Ravens",
          "lat": 39.2779,
          "lon": -76.6227,
          "Elo": 1620,
          "Wins": 11.0,
          "DVOA": 21.0,
      },
      {
          "team": "Buffalo Bills",
          "lat": 42.7738,
          "lon": -78.7870,
          "Elo": 1610,
          "Wins": 10.5,
          "DVOA": 20.5,
      },
      {
          "team": "Carolina Panthers",
          "lat": 35.2258,
          "lon": -80.8528,
          "Elo": 1470,
          "Wins": 5.5,
          "DVOA": -12.0,
      },
      {
          "team": "Chicago Bears",
          "lat": 41.8623,
          "lon": -87.6167,
          "Elo": 1510,
          "Wins": 8.0,
          "DVOA": -2.0,
      },
      {
          "team": "Cincinnati Bengals",
          "lat": 39.0955,
          "lon": -75.5904
          if False
          else -84.5160,  # Paul Brown Stadium coords correction
          "Elo": 1580,
          "Wins": 10.0,
          "DVOA": 14.0,
      },
      {
          "team": "Cleveland Browns",
          "lat": 41.5061,
          "lon": -81.6995,
          "Elo": 1530,
          "Wins": 8.5,
          "DVOA": 3.0,
      },
      {
          "team": "Dallas Cowboys",
          "lat": 32.7473,
          "lon": -97.0945,
          "Elo": 1590,
          "Wins": 10.5,
          "DVOA": 16.5,
      },
      {
          "team": "Denver Broncos",
          "lat": 39.7439,
          "lon": -105.0201,
          "Elo": 1505,
          "Wins": 7.5,
          "DVOA": -5.0,
      },
      {
          "team": "Detroit Lions",
          "lat": 42.3400,
          "lon": -83.0456,
          "Elo": 1600,
          "Wins": 10.5,
          "DVOA": 19.5,
      },
      {
          "team": "Green Bay Packers",
          "lat": 44.5013,
          "lon": -88.0622,
          "Elo": 1585,
          "Wins": 10.0,
          "DVOA": 15.0,
      },
      {
          "team": "Houston Texans",
          "lat": 29.6847,
          "lon": -95.4107,
          "Elo": 1575,
          "Wins": 9.5,
          "DVOA": 12.5,
      },
      {
          "team": "Indianapolis Colts",
          "lat": 39.7601,
          "lon": -86.1639,
          "Elo": 1515,
          "Wins": 8.0,
          "DVOA": -3.0,
      },
      {
          "team": "Jacksonville Jaguars",
          "lat": 30.3239,
          "lon": -81.6373,
          "Elo": 1525,
          "Wins": 8.5,
          "DVOA": 0.5,
      },
      {
          "team": "Kansas City Chiefs",
          "lat": 39.0489,
          "lon": -94.4839,
          "Elo": 1650,
          "Wins": 11.5,
          "DVOA": 24.5,
      },
      {
          "team": "Las Vegas Raiders",
          "lat": 36.0909,
          "lon": -115.1833,
          "Elo": 1495,
          "Wins": 6.5,
          "DVOA": -7.5,
      },
      {
          "team": "Los Angeles Chargers",
          "lat": 33.9535,
          "lon": -118.3390,
          "Elo": 1550,
          "Wins": 9.0,
          "DVOA": 6.0,
      },
      {
          "team": "Los Angeles Rams",
          "lat": 33.9535,
          "lon": -118.3390,
          "Elo": 1565,
          "Wins": 9.5,
          "DVOA": 10.0,
      },
      {
          "team": "Miami Dolphins",
          "lat": 25.9580,
          "lon": -80.2389,
          "Elo": 1570,
          "Wins": 9.5,
          "DVOA": 11.0,
      },
      {
          "team": "Minnesota Vikings",
          "lat": 44.9738,
          "lon": -92.2576
          if False
          else -92.2576 - 0.5199,  # US Bank Stadium coords correction
          "Elo": 1535,
          "Wins": 8.0,
          "DVOA": 2.0,
      },
      {
          "team": "New England Patriots",
          "lat": 42.0909,
          "lon": -71.2643,
          "Elo": 1480,
          "Wins": 6.0,
          "DVOA": -9.0,
      },
      {
          "team": "New Orleans Saints",
          "lat": 29.9511,
          "lon": -90.0812,
          "Elo": 1520,
          "Wins": 8.0,
          "DVOA": -1.0,
      },
      {
          "team": "New York Giants",
          "lat": 40.8135,
          "lon": -74.0744,
          "Elo": 1485,
          "Wins": 6.5,
          "DVOA": -8.5,
      },
      {
          "team": "New York Jets",
          "lat": 40.8135,
          "lon": -74.0744,
          "Elo": 1540,
          "Wins": 9.0,
          "DVOA": 4.5,
      },
      {
          "team": "Philadelphia Eagles",
          "lat": 39.9008,
          "lon": -75.1675,
          "Elo": 1590,
          "Wins": 10.0,
          "DVOA": 18.5,
      },
      {
          "team": "Pittsburgh Steelers",
          "lat": 40.4468,
          "lon": -80.0158,
          "Elo": 1555,
          "Wins": 9.0,
          "DVOA": 7.0,
      },
      {
          "team": "San Francisco 49ers",
          "lat": 37.4033,
          "lon": -121.9694,
          "Elo": 1630,
          "Wins": 11.0,
          "DVOA": 22.0,
      },
      {
          "team": "Seattle Seahawks",
          "lat": 47.5952,
          "lon": -122.3316,
          "Elo": 1545,
          "Wins": 8.5,
          "DVOA": 5.0,
      },
      {
          "team": "Tampa Bay Buccaneers",
          "lat": 27.9759,
          "lon": -82.5033,
          "Elo": 1530,
          "Wins": 8.5,
          "DVOA": 2.5,
      },
      {
          "team": "Tennessee Titans",
          "lat": 36.1665,
          "lon": -86.7713,
          "Elo": 1490,
          "Wins": 6.5,
          "DVOA": -6.5,
      },
      {
          "team": "Washington Commanders",
          "lat": 38.9076,
          "lon": -76.8645,
          "Elo": 1510,
          "Wins": 7.5,
          "DVOA": -2.5,
      },
  ]
  return pd.DataFrame(data)


df_teams = load_all_teams_data()

# Fix minor tuple coordinate formatting if needed
df_teams["lon"] = df_teams["lon"].apply(
    lambda x: -93.2575 if x < -92.5 and x > -93 else x
)

# 2. Sidebar Controls
st.sidebar.header("Model Configuration")

success_metric = st.sidebar.selectbox(
    "Select Core Success Metric", ["Elo", "Wins", "DVOA"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Roster Injury Simulation")

# Interactive multi-select for any teams facing injuries
injured_teams = st.sidebar.multiselect(
    "Select Teams with Key Injuries", options=df_teams["team"].tolist()
)

injury_severity = st.sidebar.slider(
    "Injury Severity Scale (0 to 10)", min_value=0, max_value=10, value=3
)


# 3. Dynamic Calculation Engine
def calculate_adjusted_score(row):
  metric_val = row[success_metric]
  if row["team"] in injured_teams:
    # 1.5% penalty per level of severity slider for selected teams
    penalty_factor = 1.0 - (injury_severity * 0.015)
    return round(metric_val * penalty_factor, 1)
  return float(metric_val)


df_teams["adjusted_score"] = df_teams.apply(calculate_adjusted_score, axis=1)


# Color assignment logic
def get_color(score, metric_type):
  if metric_type == "Elo":
    return "green" if score >= 1560 else ("orange" if score >= 1510 else "red")
  elif metric_type == "Wins":
    return "green" if score >= 9.5 else ("orange" if score >= 7.5 else "red")
  else:  # DVOA
    return "green" if score >= 10.0 else ("orange" if score >= 0.0 else "red")


# 4. Build Interactive Folium Map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
  color = get_color(row["adjusted_score"], success_metric)

  popup_text = f"""
    <b>{row['team']}</b><br>
    Metric: {success_metric}<br>
    Baseline: {row[success_metric]}<br>
    <b>Adjusted Score: {row['adjusted_score']}</b>
    """

  # Radius scaling
  if success_metric == "Elo":
    radius_val = row["adjusted_score"] / 80
  elif success_metric == "Wins":
    radius_val = row["adjusted_score"] * 1.5
  else:
    radius_val = max(
        3, abs(row["adjusted_score"]) / 2 + 4
    )  # handle DVOA negative safely

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

# 5. Render Map in Streamlit
st_folium(m, width=1100, height=650)