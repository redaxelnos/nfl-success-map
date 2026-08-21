import os
import datetime
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.linear_model import LogisticRegression

def main():
    current_year = datetime.datetime.now().year
    print(f"Starting automated model run for {current_year} season...")
    
    # 1. Pull Schedule Data
    try:
        sched = nfl.import_schedules([current_year])
    except Exception as e:
        print(f"Could not pull schedule: {e}")
        return

    completed_games = sched.dropna(subset=['result']).copy()
    
    # 2. Pull Play-by-Play Data for Advanced Metrics (EPA)
    team_epa_dict = {}
    if not completed_games.empty:
        try:
            print("Pulling play-by-play data for advanced EPA metrics...")
            pbp = nfl.import_pbp_data([current_year])
            pbp_rp = pbp[(pbp['pass'] == 1) | (pbp['rush'] == 1)].copy()
            if not pbp_rp.empty:
                epa_off = pbp_rp.groupby('posteam')['epa'].mean().to_dict()
                epa_def = pbp_rp.groupby('defteam')['epa'].mean().to_dict()
                for team in set(list(epa_off.keys()) + list(epa_def.keys())):
                    team_epa_dict[team] = {
                        'off_epa': epa_off.get(team, 0.0),
                        'def_epa': epa_def.get(team, 0.0)
                    }
        except Exception as e:
            print(f"PBP ingestion notice (using fallback features): {e}")

    # 3. Calculate Dynamic Ranks & Ratings from Live Data
    all_teams = pd.unique(sched[['home_team', 'away_team']].values.ravel('K'))
    ranking_rows = []
    
    for t in all_teams:
        off_val = team_epa_dict.get(t, {}).get('off_epa', 0.0)
        def_val = team_epa_dict.get(t, {}).get('def_epa', 0.0)
        
        ranking_rows.append({
            'abbr': t,
            'raw_off': off_val,
            'raw_def': def_val,
        })
        
    rank_df = pd.DataFrame(ranking_rows)
    if not rank_df.empty:
        # Rank 1 = highest offensive EPA
        rank_df['Off'] = rank_df['raw_off'].rank(ascending=False, method='min').astype(int)
        # Rank 1 = lowest defensive EPA allowed
        rank_df['Def'] = rank_df['raw_def'].rank(ascending=True, method='min').astype(int)
        rank_df['SOS'] = ".500"
        rank_df['Rating'] = 1500 + (rank_df['raw_off'] * 100) - (rank_df['raw_def'] * 100)
        rank_df['BasePlayoff'] = 50.0
        
        team_rank_output = rank_df[['abbr', 'Off', 'Def', 'SOS', 'Rating', 'BasePlayoff']]
        team_rank_output.to_csv("team_rankings.csv", index=False)
        print("Team rankings and stats successfully updated.")

    # 4. Feature Engineering & Training
    completed_games['home_win'] = (completed_games['result'] > 0).astype(int)
    completed_games['home_off_epa'] = completed_games['home_team'].map(lambda x: team_epa_dict.get(x, {}).get('off_epa', 0.0))
    completed_games['home_def_epa'] = completed_games['home_team'].map(lambda x: team_epa_dict.get(x, {}).get('def_epa', 0.0))
    completed_games['away_off_epa'] = completed_games['away_team'].map(lambda x: team_epa_dict.get(x, {}).get('off_epa', 0.0))
    completed_games['away_def_epa'] = completed_games['away_team'].map(lambda x: team_epa_dict.get(x, {}).get('def_epa', 0.0))

    features = ['spread_line', 'total_line', 'home_off_epa', 'home_def_epa', 'away_off_epa', 'away_def_epa']
    X_train = completed_games[features].fillna(0)
    y_train = completed_games['home_win']

    if len(X_train) < 5:
        features = ['spread_line', 'total_line']
        X_train = completed_games[features].fillna(0)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    # 5. Predict Upcoming Week's Odds
    upcoming_games = sched[sched['result'].isna()].copy()
    if not upcoming_games.empty:
        upcoming_games['home_off_epa'] = upcoming_games['home_team'].map(lambda x: team_epa_dict.get(x, {}).get('off_epa', 0.0))
        upcoming_games['home_def_epa'] = upcoming_games['home_team'].map(lambda x: team_epa_dict.get(x, {}).get('def_epa', 0.0))
        upcoming_games['away_off_epa'] = upcoming_games['away_team'].map(lambda x: team_epa_dict.get(x, {}).get('off_epa', 0.0))
        upcoming_games['away_def_epa'] = upcoming_games['away_team'].map(lambda x: team_epa_dict.get(x, {}).get('def_epa', 0.0))
        
        X_predict = upcoming_games[features].fillna(0)
        probabilities = model.predict_proba(X_predict)
        
        upcoming_games['home_win_prob'] = probabilities[:, 1]
        upcoming_games['away_win_prob'] = probabilities[:, 0]
        
        output = upcoming_games[['game_id', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob']]
        output.to_csv("weekly_predictions.csv", index=False)
        print("Weekly predictions successfully updated.")
    else:
        print("No upcoming games found to predict.")

if __name__ == "__main__":
    main()
