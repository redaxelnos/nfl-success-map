import folium
import nfl_data_py as nfl
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="NFL Granular Player Injury & Postseason Map", layout="wide"
)

st.title("NFL Granular Player Injury & Postseason Simulator")
st.markdown(
    "Select any team in the sidebar to adjust individual star player injury"
    " sliders (0 to 10). Player skill-set **'Deadliness' weights** ensure elite"
    " playmakers (like Franchise QBs and Elite Pass Rushers) impact"
    " probabilities realistically."
)


# 1. Team Base Data & Logos
@st.cache_data
def load_team_data():
  data = [
      {
          "team": "Arizona Cardinals",
          "abbr": "ARI",
          "lat": 33.5276,
          "lon": -112.2626,
          "BasePlayoff": 32.0,
          "BaseSB": 1.5,
      },
      {
          "team": "Atlanta Falcons",
          "abbr": "ATL",
          "lat": 33.7554,
          "lon": -84.4010,
          "BasePlayoff": 45.0,
          "BaseSB": 2.5,
      },
      {
          "team": "Baltimore Ravens",
          "abbr": "BAL",
          "lat": 39.2779,
          "lon": -76.6227,
          "BasePlayoff": 82.0,
          "BaseSB": 12.0,
      },
      {
          "team": "Buffalo Bills",
          "abbr": "BUF",
          "lat": 42.7738,
          "lon": -78.7870,
          "BasePlayoff": 78.0,
          "BaseSB": 10.5,
      },
      {
          "team": "Carolina Panthers",
          "abbr": "CAR",
          "lat": 35.2258,
          "lon": -80.8528,
          "BasePlayoff": 18.0,
          "BaseSB": 0.5,
      },
      {
          "team": "Chicago Bears",
          "abbr": "CHI",
          "lat": 41.8623,
          "lon": -87.6167,
          "BasePlayoff": 40.0,
          "BaseSB": 2.0,
      },
      {
          "team": "Cincinnati Bengals",
          "abbr": "CIN",
          "lat": 39.0955,
          "lon": -84.5160,
          "BasePlayoff": 68.0,
          "BaseSB": 7.5,
      },
      {
          "team": "Cleveland Browns",
          "abbr": "CLE",
          "lat": 41.5061,
          "lon": -81.6995,
          "BasePlayoff": 48.0,
          "BaseSB": 3.0,
      },
      {
          "team": "Dallas Cowboys",
          "abbr": "DAL",
          "lat": 32.7473,
          "lon": -97.0945,
          "BasePlayoff": 72.0,
          "BaseSB": 8.5,
      },
      {
          "team": "Denver Broncos",
          "abbr": "DEN",
          "lat": 39.7439,
          "lon": -105.0201,
          "BasePlayoff": 35.0,
          "BaseSB": 1.5,
      },
      {
          "team": "Detroit Lions",
          "abbr": "DET",
          "lat": 42.3400,
          "lon": -83.0456,
          "BasePlayoff": 75.0,
          "BaseSB": 9.5,
      },
      {
          "team": "Green Bay Packers",
          "abbr": "GB",
          "lat": 44.5013,
          "lon": -88.0622,
          "BasePlayoff": 70.0,
          "BaseSB": 8.0,
      },
      {
          "team": "Houston Texans",
          "abbr": "HOU",
          "lat": 29.6847,
          "lon": -95.4107,
          "BasePlayoff": 65.0,
          "BaseSB": 6.5,
      },
      {
          "team": "Indianapolis Colts",
          "abbr": "IND",
          "lat": 39.7601,
          "lon": -86.1639,
          "BasePlayoff": 42.0,
          "BaseSB": 2.0,
      },
      {
          "team": "Jacksonville Jaguars",
          "abbr": "JAX",
          "lat": 30.3239,
          "lon": -81.6373,
          "BasePlayoff": 46.0,
          "BaseSB": 2.5,
      },
      {
          "team": "Kansas City Chiefs",
          "abbr": "KC",
          "lat": 39.0489,
          "lon": -94.4839,
          "BasePlayoff": 92.0,
          "BaseSB": 20.0,
      },
      {
          "team": "Las Vegas Raiders",
          "abbr": "LV",
          "lat": 36.0909,
          "lon": -115.1833,
          "BasePlayoff": 28.0,
          "BaseSB": 1.0,
      },
      {
          "team": "Los Angeles Chargers",
          "abbr": "LAC",
          "lat": 33.9535,
          "lon": -118.3390,
          "BasePlayoff": 55.0,
          "BaseSB": 4.5,
      },
      {
          "team": "Los Angeles Rams",
          "abbr": "LAR",
          "lat": 33.9535,
          "lon": -118.3390,
          "BasePlayoff": 62.0,
          "BaseSB": 5.5,
      },
      {
          "team": "Miami Dolphins",
          "abbr": "MIA",
          "lat": 25.9580,
          "lon": -80.2389,
          "BasePlayoff": 64.0,
          "BaseSB": 6.0,
      },
      {
          "team": "Minnesota Vikings",
          "abbr": "MIN",
          "lat": 44.9738,
          "lon": -93.2575,
          "BasePlayoff": 48.0,
          "BaseSB": 3.0,
      },
      {
          "team": "New England Patriots",
          "abbr": "NE",
          "lat": 42.0909,
          "lon": -71.2643,
          "BasePlayoff": 22.0,
          "BaseSB": 0.8,
      },
      {
          "team": "New Orleans Saints",
          "abbr": "NO",
          "lat": 29.9511,
          "lon": -90.0812,
          "BasePlayoff": 44.0,
          "BaseSB": 2.2,
      },
      {
          "team": "New York Giants",
          "abbr": "NYG",
          "lat": 40.8135,
          "lon": -74.0744,
          "BasePlayoff": 25.0,
          "BaseSB": 1.0,
      },
      {
          "team": "New York Jets",
          "abbr": "NYJ",
          "lat": 40.8135,
          "lon": -74.0744,
          "BasePlayoff": 52.0,
          "BaseSB": 4.0,
      },
      {
          "team": "Philadelphia Eagles",
          "abbr": "PHI",
          "lat": 39.9008,
          "lon": -75.1675,
          "BasePlayoff": 73.0,
          "BaseSB": 9.0,
      },
      {
          "team": "Pittsburgh Steelers",
          "abbr": "PIT",
          "lat": 40.4468,
          "lon": -80.0158,
          "BasePlayoff": 58.0,
          "BaseSB": 5.0,
      },
      {
          "team": "San Francisco 49ers",
          "abbr": "SF",
          "lat": 37.4033,
          "lon": -121.9694,
          "BasePlayoff": 85.0,
          "BaseSB": 14.0,
      },
      {
          "team": "Seattle Seahawks",
          "abbr": "SEA",
          "lat": 47.5952,
          "lon": -122.3316,
          "BasePlayoff": 53.0,
          "BaseSB": 4.0,
      },
      {
          "team": "Tampa Bay Buccaneers",
          "abbr": "TB",
          "lat": 27.9759,
          "lon": -82.5033,
          "BasePlayoff": 47.0,
          "BaseSB": 3.0,
      },
      {
          "team": "Tennessee Titans",
          "abbr": "TEN",
          "lat": 36.1665,
          "lon": -86.7713,
          "BasePlayoff": 26.0,
          "BaseSB": 1.0,
      },
      {
          "team": "Washington Commanders",
          "abbr": "WAS",
          "lat": 38.9076,
          "lon": -76.8645,
          "BasePlayoff": 38.0,
          "BaseSB": 1.8,
      },
  ]
  df = pd.DataFrame(data)
  df["logo_url"] = df["abbr"].apply(
      lambda x: f"https://a.espncdn.com/i/teamlogos/nfl/500/{x.lower()}.png"
  )
  return df


df_teams = load_team_data()

# 2. Curated Star Player Dictionary with Skill-Set "Deadliness" Weights
# (Weight factors: QB = 2.5x impact, Elite Playmakers/Pass Rushers = 1.5x, Standard Starters = 1.0x)
@st.cache_data
def get_star_players():
  return {
      "KC": [
          {"name": "Patrick Mahomes (QB)", "weight": 3.0},
          {"name": "Travis Kelce (TE)", "weight": 1.8},
          {"name": "Chris Jones (DT)", "weight": 1.6},
          {"name": "Creed Humphrey (C)", "weight": 1.2},
      ],
      "SF": [
          {"name": "Brock Purdy (QB)", "weight": 2.2},
          {"name": "Christian McCaffrey (RB)", "weight": 2.5},
          {"name": "Nick Bosa (DE)", "weight": 2.0},
          {"name": "Fred Warner (LB)", "weight": 1.8},
      ],
      "BAL": [
          {"name": "Lamar Jackson (QB)", "weight": 3.0},
          {"name": "Derrick Henry (RB)", "weight": 2.0},
          {"name": "Kyle Hamilton (S)", "weight": 1.5},
          {"name": "Roquan Smith (LB)", "weight": 1.6},
      ],
      "BUF": [
          {"name": "Josh Allen (QB)", "weight": 3.0},
          {"name": "James Cook (RB)", "weight": 1.4},
          {"name": "Matt Milano (LB)", "weight": 1.5},
          {"name": "Greg Rousseau (DE)", "weight": 1.3},
      ],
      "PHI": [
          {"name": "Jalen Hurts (QB)", "weight": 2.4},
          {"name": "Saquon Barkley (RB)", "weight": 2.2},
          {"name": "A.J. Brown (WR)", "weight": 1.8},
          {"name": "Lane Johnson (OT)", "weight": 1.9},
      ],
      "DET": [
          {"name": "Jared Goff (QB)", "weight": 2.1},
          {"name": "Amon-Ra St. Brown (WR)", "weight": 1.9},
          {"name": "Penei Sewell (OT)", "weight": 1.9},
          {"name": "Aidan Hutchinson (DE)", "weight": 2.2},
      ],
      # Default fallback list for remaining teams
      "DEFAULT": [
          {"name": "Franchise Quarterback (QB)", "weight": 2.5},
          {"name": "WR1 Playmaker (WR)", "weight": 1.5},
          {"name": "Lockdown Corner (CB)", "weight": 1.4},
          {"name": "Star Pass Rusher (DE)", "weight": 1.6},
          {"name": "Left Tackle (OT)", "weight": 1.5},
      ],
  }


star_rosters = get_star_players()

# 3. Sidebar Controls & Persistent State Initialization
st.sidebar.header("Granular Injury Simulator")
target_metric = st.sidebar.selectbox(
    "View Map Metric", ["Playoff Probability (%)", "Super Bowl Likelihood (%)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Team & Player Selection")

selected_team_name = st.sidebar.selectbox(
    "Choose Team to Inspect", df_teams["team"].tolist()
)
selected_abbr = df_teams.loc[
    df_teams["team"] == selected_team_name, "abbr"
].values[0]

# Initialize global injury tracker in session state
if "player_injuries" not in st.session_state:
  st.session_state.player_injuries = {}

st.sidebar.markdown(f"**Adjust Injury Severity (0 = Healthy, 10 = Out for Season)**")

# Retrieve players for selected team
team_players = star_rosters.get(selected_abbr, star_rosters["DEFAULT"])

# Render individual sliding scale for each player
team_injury_scores = {}
for player in team_players:
  p_name = player["name"]
  p_weight = player["weight"]

  # Unique key for session state per team/player
  slider_key = f"{selected_abbr}_{p_name}"
  current_val = st.session_state.player_injuries.get(slider_key, 0)

  slider_val = st.sidebar.slider(
      f"{p_name} (Deadliness: {p_weight}x)", 0, 10, current_val, key=slider_key
  )
  team_injury_scores[p_name] = {"severity": slider_val, "weight": p_weight}


# 4. Calculation Engine with Skill-Set Multipliers
def calculate_adjusted_odds(row):
  abbr = row["abbr"]
  base_playoff = row["BasePlayoff"]
  base_sb = row["BaseSB"]

  total_penalty = 0.0

  # Sum up injuries across all teams stored in session state
  for key, severity in st.session_state.player_injuries.items():
    if key.startswith(abbr + "_"):
      # Extract weight dynamically from player config
      p_name = key.replace(abbr + "_", "")
      # Find weight
      p_list = star_rosters.get(abbr, star_rosters["DEFAULT"])
      weight = next((item["weight"] for item in p_list if item["name"] == p_name), 1.5)

      # Penalty formula: Severity (0-10) * Skill Weight * scaling factor
      total_penalty += severity * weight

  # Apply penalties to probabilities
  adjusted_playoff = max(1.0, min(99.0, base_playoff - (total_penalty * 1.8)))
  adjusted_sb = max(0.1, min(50.0, base_sb - (total_penalty * 0.4)))

  if target_metric == "Playoff Probability (%)":
    return round(adjusted_playoff, 1)
  else:
    return round(adjusted_sb, 1)


df_teams["displayed_score"] = df_teams.apply(calculate_adjusted_odds, axis=1)


# 5. Build Interactive Folium Map with Logo Icons
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
  # Count active injuries for popup details
  abbr = row["abbr"]
  team_total_severity = sum(
      val for k, val in st.session_state.player_injuries.items() if k.startswith(abbr + "_")
  )

  popup_text = f"""
    <b>{row['team']} ({row['abbr']})</b><br>
    Metric: {target_metric}<br>
    <b>Current Odds: {row['displayed_score']}%</b><br>
    <i>Injury Severity Sum: {team_total_severity}</i>
    """

  icon_size_val = int(
      min(
          45,
          max(
              22,
              row["displayed_score"] / 2
              if target_metric == "Playoff Probability (%)"
              else row["displayed_score"] * 1.5,
          ),
      )
  )

  logo_icon = folium.CustomIcon(
      icon_image=row["logo_url"],
      icon_size=(icon_size_val, icon_size_val),
      icon_anchor=(icon_size_val // 2, icon_size_val // 2),
  )

  folium.Marker(
      location=[row["lat"], row["lon"]],
      icon=logo_icon,
      popup=folium.Popup(popup_text, max_width=300),
      tooltip=row["team"],
  ).add_to(m)

st_folium(m, width=1100, height=650)