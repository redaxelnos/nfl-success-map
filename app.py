import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Interactive Clickable NFL Postseason Map", layout="wide"
)

st.title("Interactive Clickable NFL Postseason & Analytics Simulator")
st.markdown(
    "**Click any team's logo on the map** (or use the sidebar dropdown) to"
    " inspect their advanced profile, adjust global risk, and fine-tune"
    " individual player injury sliders in real time."
)


# 1. Team Base Data, Logos & Advanced Analytics Profiles
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
          "OffRank": 18,
          "DefRank": 22,
          "SOS": ".512",
          "TurnoverMargin": -2,
      },
      {
          "team": "Atlanta Falcons",
          "abbr": "ATL",
          "lat": 33.7554,
          "lon": -84.4010,
          "BasePlayoff": 45.0,
          "BaseSB": 2.5,
          "OffRank": 14,
          "DefRank": 16,
          "SOS": ".485",
          "TurnoverMargin": +1,
      },
      {
          "team": "Baltimore Ravens",
          "abbr": "BAL",
          "lat": 39.2779,
          "lon": -76.6227,
          "BasePlayoff": 82.0,
          "BaseSB": 12.0,
          "OffRank": 2,
          "DefRank": 3,
          "SOS": ".524",
          "TurnoverMargin": +7,
      },
      {
          "team": "Buffalo Bills",
          "abbr": "BUF",
          "lat": 42.7738,
          "lon": -78.7870,
          "BasePlayoff": 78.0,
          "BaseSB": 10.5,
          "OffRank": 3,
          "DefRank": 8,
          "SOS": ".508",
          "TurnoverMargin": +5,
      },
      {
          "team": "Carolina Panthers",
          "abbr": "CAR",
          "lat": 35.2258,
          "lon": -80.8528,
          "BasePlayoff": 18.0,
          "BaseSB": 0.5,
          "OffRank": 30,
          "DefRank": 31,
          "SOS": ".492",
          "TurnoverMargin": -9,
      },
      {
          "team": "Chicago Bears",
          "abbr": "CHI",
          "lat": 41.8623,
          "lon": -87.6167,
          "BasePlayoff": 40.0,
          "BaseSB": 2.0,
          "OffRank": 20,
          "DefRank": 12,
          "SOS": ".478",
          "TurnoverMargin": 0,
      },
      {
          "team": "Cincinnati Bengals",
          "abbr": "CIN",
          "lat": 39.0955,
          "lon": -84.5160,
          "BasePlayoff": 68.0,
          "BaseSB": 7.5,
          "OffRank": 6,
          "DefRank": 19,
          "SOS": ".531",
          "TurnoverMargin": +3,
      },
      {
          "team": "Cleveland Browns",
          "abbr": "CLE",
          "lat": 41.5061,
          "lon": -81.6995,
          "BasePlayoff": 48.0,
          "BaseSB": 3.0,
          "OffRank": 22,
          "DefRank": 4,
          "SOS": ".542",
          "TurnoverMargin": -4,
      },
      {
          "team": "Dallas Cowboys",
          "abbr": "DAL",
          "lat": 32.7473,
          "lon": -97.0945,
          "BasePlayoff": 72.0,
          "BaseSB": 8.5,
          "OffRank": 5,
          "DefRank": 11,
          "SOS": ".495",
          "TurnoverMargin": +4,
      },
      {
          "team": "Denver Broncos",
          "abbr": "DEN",
          "lat": 39.7439,
          "lon": -105.0201,
          "BasePlayoff": 35.0,
          "BaseSB": 1.5,
          "OffRank": 24,
          "DefRank": 15,
          "SOS": ".515",
          "TurnoverMargin": -1,
      },
      {
          "team": "Detroit Lions",
          "abbr": "DET",
          "lat": 42.3400,
          "lon": -83.0456,
          "BasePlayoff": 75.0,
          "BaseSB": 9.5,
          "OffRank": 1,
          "DefRank": 10,
          "SOS": ".510",
          "TurnoverMargin": +6,
      },
      {
          "team": "Green Bay Packers",
          "abbr": "GB",
          "lat": 44.5013,
          "lon": -88.0622,
          "BasePlayoff": 70.0,
          "BaseSB": 8.0,
          "OffRank": 8,
          "DefRank": 13,
          "SOS": ".502",
          "TurnoverMargin": +3,
      },
      {
          "team": "Houston Texans",
          "abbr": "HOU",
          "lat": 29.6847,
          "lon": -95.4107,
          "BasePlayoff": 65.0,
          "BaseSB": 6.5,
          "OffRank": 9,
          "DefRank": 9,
          "SOS": ".488",
          "TurnoverMargin": +5,
      },
      {
          "team": "Indianapolis Colts",
          "abbr": "IND",
          "lat": 39.7601,
          "lon": -86.1639,
          "BasePlayoff": 42.0,
          "BaseSB": 2.0,
          "OffRank": 17,
          "DefRank": 21,
          "SOS": ".490",
          "TurnoverMargin": -1,
      },
      {
          "team": "Jacksonville Jaguars",
          "abbr": "JAX",
          "lat": 30.3239,
          "lon": -81.6373,
          "BasePlayoff": 46.0,
          "BaseSB": 2.5,
          "OffRank": 16,
          "DefRank": 20,
          "SOS": ".500",
          "TurnoverMargin": 0,
      },
      {
          "team": "Kansas City Chiefs",
          "abbr": "KC",
          "lat": 39.0489,
          "lon": -94.4839,
          "BasePlayoff": 92.0,
          "BaseSB": 20.0,
          "OffRank": 4,
          "DefRank": 2,
          "SOS": ".535",
          "TurnoverMargin": +8,
      },
      {
          "team": "Las Vegas Raiders",
          "abbr": "LV",
          "lat": 36.0909,
          "lon": -115.1833,
          "BasePlayoff": 28.0,
          "BaseSB": 1.0,
          "OffRank": 27,
          "DefRank": 14,
          "SOS": ".520",
          "TurnoverMargin": -3,
      },
      {
          "team": "Los Angeles Chargers",
          "abbr": "LAC",
          "lat": 33.9535,
          "lon": -118.3390,
          "BasePlayoff": 55.0,
          "BaseSB": 4.5,
          "OffRank": 15,
          "DefRank": 7,
          "SOS": ".475",
          "TurnoverMargin": +2,
      },
      {
          "team": "Los Angeles Rams",
          "abbr": "LAR",
          "lat": 33.9535,
          "lon": -118.3390,
          "BasePlayoff": 62.0,
          "BaseSB": 5.5,
          "OffRank": 7,
          "DefRank": 18,
          "SOS": ".512",
          "TurnoverMargin": +1,
      },
      {
          "team": "Miami Dolphins",
          "abbr": "MIA",
          "lat": 25.9580,
          "lon": -80.2389,
          "BasePlayoff": 64.0,
          "BaseSB": 6.0,
          "OffRank": 10,
          "DefRank": 17,
          "SOS": ".482",
          "TurnoverMargin": +2,
      },
      {
          "team": "Minnesota Vikings",
          "abbr": "MIN",
          "lat": 44.9738,
          "lon": -93.2575,
          "BasePlayoff": 48.0,
          "BaseSB": 3.0,
          "OffRank": 19,
          "DefRank": 16,
          "SOS": ".505",
          "TurnoverMargin": 0,
      },
      {
          "team": "New England Patriots",
          "abbr": "NE",
          "lat": 42.0909,
          "lon": -71.2643,
          "BasePlayoff": 22.0,
          "BaseSB": 0.8,
          "OffRank": 31,
          "DefRank": 25,
          "SOS": ".518",
          "TurnoverMargin": -6,
      },
      {
          "team": "New Orleans Saints",
          "abbr": "NO",
          "lat": 29.9511,
          "lon": -90.0812,
          "BasePlayoff": 44.0,
          "BaseSB": 2.2,
          "OffRank": 13,
          "DefRank": 23,
          "SOS": ".470",
          "TurnoverMargin": +1,
      },
      {
          "team": "New York Giants",
          "abbr": "NYG",
          "lat": 40.8135,
          "lon": -74.0744,
          "BasePlayoff": 25.0,
          "BaseSB": 1.0,
          "OffRank": 28,
          "DefRank": 26,
          "SOS": ".525",
          "TurnoverMargin": -5,
      },
      {
          "team": "New York Jets",
          "abbr": "NYJ",
          "lat": 40.8135,
          "lon": -74.0744,
          "BasePlayoff": 52.0,
          "BaseSB": 4.0,
          "OffRank": 21,
          "DefRank": 5,
          "SOS": ".502",
          "TurnoverMargin": +2,
      },
      {
          "team": "Philadelphia Eagles",
          "abbr": "PHI",
          "lat": 39.9008,
          "lon": -75.1675,
          "BasePlayoff": 73.0,
          "BaseSB": 9.0,
          "OffRank": 11,
          "DefRank": 6,
          "SOS": ".498",
          "TurnoverMargin": +4,
      },
      {
          "team": "Pittsburgh Steelers",
          "abbr": "PIT",
          "lat": 40.4468,
          "lon": -80.0158,
          "BasePlayoff": 58.0,
          "BaseSB": 5.0,
          "OffRank": 23,
          "DefRank": 1,
          "SOS": ".545",
          "TurnoverMargin": +6,
      },
      {
          "team": "San Francisco 49ers",
          "abbr": "SF",
          "lat": 37.4033,
          "lon": -121.9694,
          "BasePlayoff": 85.0,
          "BaseSB": 14.0,
          "OffRank": 2,
          "DefRank": 5,
          "SOS": ".510",
          "TurnoverMargin": +7,
      },
      {
          "team": "Seattle Seahawks",
          "abbr": "SEA",
          "lat": 47.5952,
          "lon": -122.3316,
          "BasePlayoff": 53.0,
          "BaseSB": 4.0,
          "OffRank": 12,
          "DefRank": 24,
          "SOS": ".492",
          "TurnoverMargin": 0,
      },
      {
          "team": "Tampa Bay Buccaneers",
          "abbr": "TB",
          "lat": 27.9759,
          "lon": -82.5033,
          "BasePlayoff": 47.0,
          "BaseSB": 3.0,
          "OffRank": 17,
          "DefRank": 22,
          "SOS": ".488",
          "TurnoverMargin": +2,
      },
      {
          "team": "Tennessee Titans",
          "abbr": "TEN",
          "lat": 36.1665,
          "lon": -86.7713,
          "BasePlayoff": 26.0,
          "BaseSB": 1.0,
          "OffRank": 29,
          "DefRank": 27,
          "SOS": ".515",
          "TurnoverMargin": -4,
      },
      {
          "team": "Washington Commanders",
          "abbr": "WAS",
          "lat": 38.9076,
          "lon": -76.8645,
          "BasePlayoff": 38.0,
          "BaseSB": 1.8,
          "OffRank": 25,
          "DefRank": 28,
          "SOS": ".485",
          "TurnoverMargin": -2,
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
def load_star_players():
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


star_rosters = load_star_players()

# 3. Initialize Session State for Selected Team Synchronization
if "selected_team" not in st.session_state:
  st.session_state.selected_team = "Kansas City Chiefs"

team_names = df_teams["team"].tolist()
current_index = team_names.index(st.session_state.selected_team)

# Sidebar Controls
st.sidebar.header("Postseason Simulation & Intelligence")
target_metric = st.sidebar.selectbox(
    "View Map Metric", ["Playoff Probability (%)", "Super Bowl Likelihood (%)"]
)

st.sidebar.markdown("---")


# Selectbox linked directly to session state
def update_team_selection():
  st.session_state.selected_team = st.session_state.team_dropdown


selected_team_name = st.sidebar.selectbox(
    "Select Team to Inspect",
    team_names,
    index=current_index,
    key="team_dropdown",
    on_change=update_team_selection,
)

selected_abbr = df_teams.loc[
    df_teams["team"] == st.session_state.selected_team, "abbr"
].values[0]
team_row = df_teams[df_teams["abbr"] == selected_abbr].iloc[0]

# Slide Drawer / Expander for Advanced Team Details
with st.sidebar.expander(
    f"Advanced Analytics: {st.session_state.selected_team}", expanded=True
):
  st.markdown(f"**Offensive Rank:** #{team_row['OffRank']}")
  st.markdown(f"**Defensive Rank:** #{team_row['DefRank']}")
  st.markdown(f"**Strength of Schedule (SOS):** {team_row['SOS']}")
  st.markdown(f"**Turnover Margin:** {team_row['TurnoverMargin']:+d}")

# Global Team Injury Risk & Individual Player Sliders
st.sidebar.markdown("---")
st.sidebar.subheader("Injury Risk Controls")

global_risk_key = f"global_risk_{selected_abbr}"
if global_risk_key not in st.session_state:
  st.session_state[global_risk_key] = 0
global_risk_factor = st.sidebar.slider(
    "Global Team Injury Risk / Attrition", 0, 10, key=global_risk_key
)

st.sidebar.markdown("---")
st.sidebar.text("Individual Key Player Injuries (0-10)")
team_players = star_rosters.get(selected_abbr, star_rosters["DEFAULT"])

for p_name in team_players:
  slider_key = f"inj_{selected_abbr}_{p_name}"
  if slider_key not in st.session_state:
    st.session_state[slider_key] = 0
  st.sidebar.slider(p_name, 0, 10, key=slider_key)


# 4. Calculation Engine linking Global Risk and Player Sliders to Postseason Odds
def calculate_adjusted_odds(row):
  abbr = row["abbr"]
  base_playoff = row["BasePlayoff"]
  base_sb = row["BaseSB"]

  total_injury_points = 0
  team_keys = star_rosters.get(abbr, star_rosters["DEFAULT"])
  for p_name in team_keys:
    key = f"inj_{abbr}_{p_name}"
    total_injury_points += st.session_state.get(key, 0)

  global_risk = st.session_state.get(f"global_risk_{abbr}", 0)
  combined_penalty = total_injury_points + (global_risk * 1.5)

  adjusted_playoff = max(1.0, min(99.0, base_playoff - (combined_penalty * 2.2)))
  adjusted_sb = max(0.1, min(50.0, base_sb - (combined_penalty * 0.45)))

  if target_metric == "Playoff Probability (%)":
    return round(adjusted_playoff, 1)
  else:
    return round(adjusted_sb, 1)


df_teams["displayed_score"] = df_teams.apply(calculate_adjusted_odds, axis=1)

# 5. Build Interactive Map with Clickable Logo Icons
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

for _, row in df_teams.iterrows():
  abbr = row["abbr"]
  popup_text = f"""
    <b>{row['team']} ({row['abbr']})</b><br>
    Metric: {target_metric}<br>
    <b>Current Odds: {row['displayed_score']}%</b><br>
    Offense Rank: #{row['OffRank']} | Defense Rank: #{row['DefRank']}
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
      tooltip=row["team"],  # Tooltip enables click tracking via streamlit-folium
  ).add_to(m)

# Render map and capture clicks
map_data = st_folium(m, width=1100, height=650, key="nfl_interactive_map")

# Synchronize map clicks with sidebar state
if map_data and map_data.get("last_object_clicked"):
  clicked_team = map_data["last_object_clicked"].get("tooltip")
  if clicked_team in team_names and clicked_team != st.session_state.selected_team:
    st.session_state.selected_team = clicked_team
    st.rerun()