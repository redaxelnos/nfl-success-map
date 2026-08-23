import os
import datetime
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.linear_model import LogisticRegression

def main():
    current_year = datetime.datetime.now().year
    print(f"Starting comprehensive data update for {current_year} season...")
    
    # 1. Pull Current & Historical Schedule Data for Machine Learning Training
    try:
        # Load historical seasons + current season to ensure robust training data
        sched_history = nfl.import_schedules([current_year - 2, current_year - 1])
        sched_current = nfl.import_schedules([current_year])
        sched = pd.concat([sched_history, sched_current], ignore_index=True)
    except Exception as e:
        print(f"Could not pull schedule data: {e}")
        return

    current_sched = sched_current[sched_current['game_type'] == 'REG'].copy()
    if current_sched.empty:
        current_sched = sched_current.copy()

    all_teams = pd.unique(current_sched[['home_team', 'away_team']].values.ravel('K'))
    completed_games_current = current_sched.dropna(subset=['result']).copy()
    
    # 2. Ingest Play-by-Play for Live EPA and Turnovers (Current Season)
    team_pbp_metrics = {t: {'off_epa': 0.0, 'def_epa': 0.0, 'to_diff': 0} for t in all_teams}
    
    if not completed_games_current.empty:
        try:
            print("Calculating live EPA and turnover metrics from play-by-play...")
            pbp = nfl.import_pbp_data([current_year])
            pbp_rp = pbp[(pbp['pass'] == 1) | (pbp['rush'] == 1)].copy()
            
            if not pbp_rp.empty:
                epa_off = pbp_rp.groupby('posteam')['epa'].mean().to_dict()
                epa_def = pbp_rp.groupby('defteam')['epa'].mean().to_dict()
                
                # Turnover calculation (Interceptions + Fumbles Lost)
                to_off = pbp.groupby('posteam')['interception'].sum() + pbp.groupby('posteam')['fumble_lost'].sum()
                to_def = pbp.groupby('defteam')['interception'].sum() + pbp.groupby('defteam')['fumble_lost'].sum()
                to_margin = (to_def.fillna(0) - to_off.fillna(0)).to_dict()
                
                for t in all_teams:
                    team_pbp_metrics[t] = {
                        'off_epa': epa_off.get(t, 0.0),
                        'def_epa': epa_def.get(t, 0.0),
                        'to_diff': int(to_margin.get(t, 0))
                    }
        except Exception as e:
            print(f"PBP processing notice: {e}")

    # 3. Dynamic Standings & Opponent Strength of Schedule (SOS)
    team_records = {t: {'wins': 0, 'losses': 0, 'ties': 0} for t in all_teams}
    
    for _, g in completed_games_current.iterrows():
        h, a, res = g['home_team'], g['away_team'], g['result']
        if res > 0:
            team_records[h]['wins'] += 1
            team_records[a]['losses'] += 1
        elif res < 0:
            team_records[a]['wins'] += 1
            team_records[h]['losses'] += 1
        else:
            team_records[h]['ties'] += 1
            team_records[a]['ties'] += 1

    team_sos = {}
    for t in all_teams:
        team_schedule = current_sched[(current_sched['home_team'] == t) | (current_sched['away_team'] == t)]
        opponents = [
            row['away_team'] if row['home_team'] == t else row['home_team']
            for _, row in team_schedule.iterrows()
        ]
        
        opp_wins = sum([team_records[opp]['wins'] + (0.5 * team_records[opp]['ties']) for opp in opponents if opp in team_records])
        opp_games = sum([team_records[opp]['wins'] + team_records[opp]['losses'] + team_records[opp]['ties'] for opp in opponents if opp in team_records])
        
        if opp_games > 0:
            sos_val = opp_wins / opp_games
            team_sos[t] = f".{int(round(sos_val * 1000)):03d}"
        else:
            team_sos[t] = ".500"

    # 4. Generate Dynamic Power Rankings & Playoff Odds
    ranking_rows = []
    for t in all_teams:
        off_val = team_pbp_metrics[t]['off_epa']
        def_val = team_pbp_metrics[t]['def_epa']
        to_val = team_pbp_metrics[t]['to_diff']
        sos_str = team_sos[t]
        
        rating = 1500 + (off_val * 120) - (def_val * 120) + (to_val * 5)
        
        wins = team_records[t]['wins']
        losses = team_records[t]['losses']
        total_g = max(1, wins + losses)
        current_win_pct = wins / total_g if (wins + losses) > 0 else 0.5
        
        playoff_prob = round(1 / (1 + np.exp(-((rating - 1500) / 50 + (current_win_pct - 0.5) * 6))) * 100, 1)
        
        ranking_rows.append({
            'abbr': t,
            'raw_off': off_val,
            'raw_def': def_val,
            'TO': to_val,
            'SOS': sos_str,
            'Rating': round(rating, 1),
            'BasePlayoff': max(1.0, min(99.0, playoff_prob))
        })
        
    rank_df = pd.DataFrame(ranking_rows)
    if not rank_df.empty:
        rank_df['Off'] = rank_df['raw_off'].rank(ascending=False, method='min').astype(int)
        rank_df['Def'] = rank_df['raw_def'].rank(ascending=True, method='min').astype(int)
        
        team_rank_output = rank_df[['abbr', 'Off', 'Def', 'TO', 'SOS', 'Rating', 'BasePlayoff']]
        team_rank_output.to_csv("team_rankings.csv", index=False)
        print("Dynamic rankings and team metrics saved to team_rankings.csv.")

    # 5. Train Machine Learning Model (Using historical + completed matchups)
    all_completed = sched.dropna(subset=['result', 'spread_line', 'total_line']).copy()
    all_completed['home_win'] = (all_completed['result'] > 0).astype(int)

    all_completed['home_off_epa'] = all_completed['home_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('off_epa', 0.0))
    all_completed['home_def_epa'] = all_completed['home_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('def_epa', 0.0))
    all_completed['away_off_epa'] = all_completed['away_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('off_epa', 0.0))
    all_completed['away_def_epa'] = all_completed['away_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('def_epa', 0.0))

    features = ['spread_line', 'total_line', 'home_off_epa', 'home_def_epa', 'away_off_epa', 'away_def_epa']
    X_train = all_completed[features].fillna(0)
    y_train = all_completed['home_win']

    print(f"Training Logistic Regression model on {len(X_train)} historical matchups...")
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # 6. Predict Upcoming Current Season Matchups
    upcoming_games = current_sched[current_sched['result'].isna()].copy()
    if not upcoming_games.empty:
        upcoming_games['home_off_epa'] = upcoming_games['home_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('off_epa', 0.0))
        upcoming_games['home_def_epa'] = upcoming_games['home_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('def_epa', 0.0))
        upcoming_games['away_off_epa'] = upcoming_games['away_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('off_epa', 0.0))
        upcoming_games['away_def_epa'] = upcoming_games['away_team'].map(lambda x: team_pbp_metrics.get(x, {}).get('def_epa', 0.0))
        
        X_predict = upcoming_games[features].fillna(0)
        probabilities = model.predict_proba(X_predict)
        
        upcoming_games['home_win_prob'] = probabilities[:, 1]
        upcoming_games['away_win_prob'] = probabilities[:, 0]
        
        output = upcoming_games[['game_id', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob']]
        output.to_csv("weekly_predictions.csv", index=False)
        print("Weekly matchup probabilities successfully saved to weekly_predictions.csv.")
    else:
        print("No upcoming games found to predict.")

if __name__ == "__main__":
    main()
