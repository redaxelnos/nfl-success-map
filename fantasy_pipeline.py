import json
import os
import pandas as pd
from yahoo_oauth import OAuth2

def get_authenticated_session(oauth_file='oauth2.json'):
    """Authenticates and refreshes the Yahoo OAuth session."""
    if not os.path.exists(oauth_file):
        raise FileNotFoundError(f"Missing {oauth_file}. Ensure authentication file is present.")
    oauth = OAuth2(None, None, from_file=oauth_file)
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    return oauth

def fetch_league_settings(oauth, league_key):
    """Dynamically queries roster slot constraints (e.g., exact IR and BN limits)."""
    url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/settings?format=json"
    try:
        res = oauth.session.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            roster_positions = data['fantasy_content']['league'][1]['settings'][0]['roster_positions']
            limits = {}
            for pos_obj in roster_positions:
                p_info = pos_obj.get('roster_position', {})
                pos = p_info.get('position')
                count = int(p_info.get('count', 0))
                limits[pos] = count
            return limits
    except Exception:
        pass
    return {"IR": 1, "BN": 6, "QB": 1, "RB": 2, "WR": 2, "TE": 1, "W/R/T": 1, "K": 1, "DEF": 1}

def fetch_top_available_players(oauth, league_key, position="QB", count=4):
    """Scans the waiver wire and free agent pool for top-ranked replacement assets."""
    url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players;status=A;position={position};sort=AR;count={count}?format=json"
    available = []
    try:
        res = oauth.session.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            players_dict = data['fantasy_content']['league'][1]['players']
            num_players = players_dict.get('count', 0)
            for idx in range(num_players):
                p_entry = players_dict[str(idx)]['player'][0]
                name = next((i['name']['full'] for i in p_entry if isinstance(i, dict) and 'name' in i), "Unknown")
                team = next((i['editorial_team_abbr'] for i in p_entry if isinstance(i, dict) and 'editorial_team_abbr' in i), "UNK").upper()
                pos = next((i['primary_position'] for i in p_entry if isinstance(i, dict) and 'primary_position' in i), position)
                status = next((i['status'] for i in p_entry if isinstance(i, dict) and 'status' in i), "Healthy")
                available.append({"Player": name, "NFL_Team": team, "Position": pos, "Status": status})
    except Exception:
        pass
    return available

def fetch_complete_fantasy_state(oauth_file='oauth2.json'):
    """
    Primary execution pipeline: Returns (rosters_df, league_metadata_dict)
    Now pulls exact live Yahoo projections to eliminate math proxies.
    """
    oauth = get_authenticated_session(oauth_file)
    
    # 1. Fetch User Teams
    url = "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nfl/teams?format=json"
    response = oauth.session.get(url, timeout=12)
    
    if response.status_code != 200:
        raise ConnectionError(f"Yahoo API Error {response.status_code}: {response.text}")
        
    data = response.json()
    teams_data = data['fantasy_content']['users']['0']['user'][1]['games']['0']['game'][1]['teams']
    
    roster_rows = []
    league_meta = {}

    for team_idx in range(teams_data['count']):
        team = teams_data[str(team_idx)]['team']
        team_key = team[0][0]['team_key']
        league_id = team_key.split('.l.')[1].split('.t.')[0]
        league_key = team_key.rsplit('.t.', 1)[0]
        team_name = next((item['name'] for item in team[0] if isinstance(item, dict) and 'name' in item), "Unknown")

        if league_id == "859017":
            league_name = "KP league"
        elif league_id == "341689":
            league_name = "League ICT 2.0"
        else:
            continue

        if league_name not in league_meta:
            settings = fetch_league_settings(oauth, league_key)
            waiver_qbs = fetch_top_available_players(oauth, league_key, position="QB", count=3)
            waiver_rbs = fetch_top_available_players(oauth, league_key, position="RB", count=3)
            waiver_wrs = fetch_top_available_players(oauth, league_key, position="WR", count=3)
            league_meta[league_name] = {
                "league_key": league_key,
                "settings": settings,
                "waivers": {"QB": waiver_qbs, "RB": waiver_rbs, "WR": waiver_wrs}
            }

        # 2. Fetch specific team roster paired with live projected stats
        proj_url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}/roster/players/stats;type=projected_week?format=json"
        proj_res = oauth.session.get(proj_url, timeout=10)
        
        if proj_res.status_code == 200:
            proj_data = proj_res.json()
            roster_data = proj_data['fantasy_content']['team'][1]['roster']['0']['players']
            
            for p_idx in range(roster_data['count']):
                player = roster_data[str(p_idx)]['player']
                details = player[0]

                p_name = next((i['name']['full'] for i in details if isinstance(i, dict) and 'name' in i), "Unknown")
                p_id = next((i['player_id'] for i in details if isinstance(i, dict) and 'player_id' in i), "Unknown")
                nfl_team = next((i['editorial_team_abbr'] for i in details if isinstance(i, dict) and 'editorial_team_abbr' in i), "UNK").upper()
                real_pos = next((i['primary_position'] for i in details if isinstance(i, dict) and 'primary_position' in i), "UNK")
                status = next((i['status'] for i in details if isinstance(i, dict) and 'status' in i), "Healthy")

                pos_data = next((i for i in player if isinstance(i, dict) and 'selected_position' in i), None)
                fantasy_slot = next((sp['position'] for sp in pos_data['selected_position'] if 'position' in sp), "BN") if pos_data else "BN"

                # Extract True Yahoo Live Projection
                proj_pts = 0.0
                pts_data = next((i for i in player if isinstance(i, dict) and 'player_projected_points' in i), None)
                if pts_data:
                    try:
                        proj_pts = float(pts_data['player_projected_points'].get('total', 0.0))
                    except ValueError:
                        proj_pts = 0.0

                roster_rows.append({
                    "League": league_name,
                    "Fantasy_Team": team_name,
                    "Player": p_name,
                    "NFL_Team": nfl_team,
                    "Real_Pos": real_pos,
                    "Fantasy_Slot": fantasy_slot,
                    "Health_Status": status,
                    "Player_ID": p_id,
                    "Proj_Pts": proj_pts
                })

    return pd.DataFrame(roster_rows), league_meta
