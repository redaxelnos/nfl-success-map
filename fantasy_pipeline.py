import json
import os
import pandas as pd
from yahoo_oauth import OAuth2

def fetch_and_parse_rosters(oauth_file='oauth2.json'):
    """
    Connects live to Yahoo API using stored OAuth tokens,
    retrieves the latest roster data, and returns a clean DataFrame.
    """
    if not os.path.exists(oauth_file):
        raise FileNotFoundError(f"Missing {oauth_file}. Please ensure your authentication file is uploaded.")
        
    # Authenticate silently using the saved permanent token
    oauth = OAuth2(None, None, from_file=oauth_file)
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    # The API endpoint that isolates your specific managed teams
    url = "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nfl/teams/roster?format=json"
    response = oauth.session.get(url)
    
    if response.status_code != 200:
        raise ConnectionError(f"Yahoo API Error {response.status_code}: {response.text}")
        
    data = response.json()
    teams_data = data['fantasy_content']['users']['0']['user'][1]['games']['0']['game'][1]['teams']
    roster_rows = []

    # Parse the nested JSON dynamically to avoid Yahoo's null insertions
    for team_idx in range(teams_data['count']):
        team = teams_data[str(team_idx)]['team']
        
        team_key = team[0][0]['team_key']
        league_id = team_key.split('.l.')[1].split('.t.')[0]
        team_name = next((item['name'] for item in team[0] if isinstance(item, dict) and 'name' in item), "Unknown")

        # Isolate only your competitive leagues
        if league_id == "859017":
            league_name = "KP league"
        elif league_id == "341689":
            league_name = "League ICT 2.0"
        else:
            continue  

        roster_container = next((item for item in team if isinstance(item, dict) and 'roster' in item), None)
        if not roster_container:
            continue
            
        roster_data = roster_container['roster']['0']['players']
        for p_idx in range(roster_data['count']):
            player = roster_data[str(p_idx)]['player']
            details = player[0]

            # Extract player vitals
            p_name = next((item['name']['full'] for item in details if isinstance(item, dict) and 'name' in item), "Unknown")
            p_id = next((item['player_id'] for item in details if isinstance(item, dict) and 'player_id' in item), "Unknown")
            nfl_team = next((item['editorial_team_abbr'] for item in details if isinstance(item, dict) and 'editorial_team_abbr' in item), "UNK")
            real_pos = next((item['primary_position'] for item in details if isinstance(item, dict) and 'primary_position' in item), "UNK")
            status = next((item['status'] for item in details if isinstance(item, dict) and 'status' in item), "Healthy")

            # Extract active fantasy deployment slot
            pos_data = next((item for item in player if isinstance(item, dict) and 'selected_position' in item), None)
            fantasy_slot = next((sp['position'] for sp in pos_data['selected_position'] if 'position' in sp), "BN") if pos_data else "BN"

            roster_rows.append({
                "League": league_name,
                "Fantasy_Team": team_name,
                "Player": p_name,
                "NFL_Team": nfl_team.upper(),
                "Real_Pos": real_pos,
                "Fantasy_Slot": fantasy_slot,
                "Health_Status": status,
                "Player_ID": p_id
            })

    return pd.DataFrame(roster_rows)

if __name__ == "__main__":
    df = fetch_and_parse_rosters()
    print(df.to_string(index=False))
