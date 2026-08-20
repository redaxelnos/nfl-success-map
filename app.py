import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="NFL Player Injury & Postseason Map", layout="wide"
)

st.title("NFL Player Injury & Postseason Simulator")
st.markdown(
    "Select any team in the sidebar to adjust individual player injury"
    " sliders (0 to 10). Watch the team logos update their size and"
    " probabilities instantly in real time."
)


# 1. Team Base Data & Official Logo URLs
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

# 2. Key Player Roster Names per Team
@st.cache_data
def get_star_players():
  return {
      "KC": [
          "Patrick Mahomes (QB)",
          "Travis Kelce (TE)",
          "Chris Jones (DT)",
          "Creed Humphrey (C)",
      ],
      "SF": [
          "Brock Purdy (QB)",
          "Christian McCaffrey (RB)",
          "Nick Bosa (DE)",
          "Fred Warner (LB)",
      ],
      "BAL": [
          "Lamar Jackson (QB)",
          "Derrick Henry (RB)",
          "Kyle Hamilton (S)",
          "Roquan Smith (LB)",
      ],
      "BUF": [
          "Josh Allen (QB)",
          "James Cook (RB)",
          "Matt Milano (LB)",
          "Greg Rousseau (DE)",
      ],
      "PHI": [
          "Jalen Hurts (QB)",
          "Saquon Barkley (RB)",
          "A.J. Brown (WR)",
          "Lane Johnson (OT)",
      ],
      "DET": [
          "Jared Goff (QB)",
          "Amon-Ra St. Brown (WR)",
          "Penei Sewell (OT)",
          "Aidan Hutchinson (DE)",
      ],
      "DEFAULT": [
          "Franchise Quarterback (QB)",
          "WR1 Playmaker (WR)",
          "Lockdown Corner (CB)",
          "Star Pass Rusher (DE)",
          "Left Tackle (OT)",
      ],
  }


star_rosters = get_star_players()

# 3. Sidebar Controls
st.sidebar.header("Postseason Simulation")
target_metric = st.sidebar.selectbox(
    "View Map Metric", ["Playoff Probability (%)", "Super Bowl Likelihood (%)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Player Injury Sliders (0 - 10)")

selected_team_name = st.sidebar.selectbox(
    "Choose Team to Modify", df_teams["team"].tolist()
)
selected_abbr = df_teams.loc[
    df_teams["team"] == selected_team_name, "abbr"
].values[0]

team_players = star_rosters.get(selected_abbr, star_rosters["DEFAULT"])

# Generate persistent injury sliders for the selected team
for p_name in team_players:
  slider_key = f"inj_{selected_abbr}_{p_name}"
  if slider_key not in st.session_state:
    st.session_state[slider_key] = 0
  st.sidebar.slider(p_name, 0, 10, key=slider_key)


# 4. Direct Calculation Engine linking Sliders to Postseason Odds
def calculate_adjusted_odds(row):
  abbr = row["abbr"]
  base_playoff = row["BasePlayoff"]
  base_sb = row["BaseSB"]

  total_injury_points = 0
  team_keys = star_rosters.get(abbr, star_rosters["DEFAULT"])
  for p_name in team_keys:
    key = f"inj_{abbr}_{p_name}"
    total_injury_points += st.session_state.get(key, 0)

  # Direct penalty deduction based on slider values
  adjusted_playoff = max(1.0, min(99.0, base_playoff - (total_injury_points * 2.5)))
  adjusted_sb = max(0.1, min(50.0, base_sb - (total_injury_points * 0.5)))

  if target_metric == "Playoff Probability (%)":
    return round(adjusted_playoff, 1)
  else:
    return round(adjusted_sb, 1)


df_teams["displayed_score"] = df_teams.apply(calculate_adjusted_odds, axis=1)

# 5. Build Interactive Map with Logo Icons
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
  abbr = row["abbr"]
  team_injury_sum = sum(
      st.session_state.get(f"inj_{abbr}_{p}", 0)
      for p in star_rosters.get(abbr, star_rosters["DEFAULT"])
  )

  popup_text = f"""
    <b>{row['team']} ({row['abbr']})</b><br>
    Metric: {target_metric}<br>
    <b>Current Odds: {row['displayed_score']}%</b><br>
    <i>Total Injury Points: {team_injury_sum}</i>
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