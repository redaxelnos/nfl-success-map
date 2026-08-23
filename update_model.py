import os
import datetime
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.linear_model import LogisticRegression

def main():
    current_year = datetime.datetime.now().year
    # Create a rolling 3-year window for model training
    years_to_pull = [current_year - 2, current_year - 1, current_year]
    print(f"Starting multi-year data update for {years_to_pull}...")
    
    # 1. Pull Multi-Year Schedule Data
    try:
        sched = nfl.import_schedules(years_to_pull)
    except Exception as e:
        print(f"Could not pull schedules: {e}")
        return

    # Isolate current year for standings and upcoming predictions
    current_sched = sched[sched['season'] == current_year]
    current_completed = current_sched.dropna(subset=['result']).copy()
    all_teams = pd.unique(current_sched[['home_team', 'away_team']].values.ravel('K'))
    
    # Determine the ranking year: Fall back to last year if preseason (0 games played)
    ranking_year = current_year if not current_completed.empty else current_year - 1
    print(f"Using {ranking_year} data for team power rankings and SOS baselines...")

    # 2. Pull Multi-Year Play-by-Play Data
    try:
        pbp = nfl.import_pbp_data(years_to_pull)
    except Exception as e:
        print(f"Could not pull PBP data: {e}")
        return

    # Filter PBP for the active ranking year (Current vs. Prior Season Baseline)
    pbp_ranking = pbp[pbp['season'] == ranking_year].copy()
    pbp_ranking_rp = pbp_ranking[(pbp_ranking['pass'] == 1) | (pbp_ranking['rush'] == 1)].copy()

    team_pbp_metrics = {t: {'off_epa': 0.0, 'def_epa': 0.0, 'to_diff': 0} for t in all_teams}
    
    if not pbp_ranking_rp.empty:
        try:
            epa_off = pbp_ranking_rp.groupby('posteam')['epa'].mean().to_dict()
            epa_def = pbp_ranking_rp.groupby('defteam')['epa'].mean().to_dict()
            
            to_off = pbp_ranking.groupby('posteam')['interception'].sum() + pbp_ranking.groupby('posteam')['fumble_lost'].sum()
            to_def = pbp_ranking.groupby('defteam')['interception'].sum() + pbp_ranking.groupby('defteam')['fumble_lost'].sum()
            to_margin = (to_def.fillna(0) - to_off.fillna(0)).to_dict()
            
            for t in all_teams:
                team_pbp_metrics[t] = {
                    'off_epa': epa_off.get(t, 0.0),
                    'def_epa': epa_def.get(t, 0.0),
                    'to_diff': int(to_margin.get(t, 0))
                }
        except Exception as e:
            print(f"PBP processing notice: {e}")

    # 3. Calculate Standings & Strength of Schedule (SOS) for Ranking Year
    ranking_completed_games = sched[(sched['season'] == ranking_year) & (sched['result'].notna())]
    team_records = {t: {'wins': 0, 'losses': 0, 'ties': 0} for t in all_teams}
    
    for _, g in ranking_completed_games.iterrows():
        h, a, res = g['home_team'], g['away_team'], g['result']
        if h in team_records and a in team_records:
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
    ranking_full_sched = sched[sched['season'] == ranking_year]
    for t in all_teams:
        team_schedule = ranking_full_sched[(ranking_full_sched['home_team'] == t) | (ranking_full_sched['away_team'] == t)]
        opponents = [
            row['away_team'] if row['home_team'] == t else row['home_team']
            for _, row in team_schedule.iterrows()
        ]
        
        opp_wins = sum([team_records.get(opp, {}).get('wins', 0) + (0.5 * team_records.get(opp, {}).get('ties', 0)) for opp in opponents if opp in team_records])
        opp_games = sum([team_records.get(opp, {}).get('wins', 0) + team_records.get(opp, {}).get('losses', 0) + team_records.get(opp, {}).get('ties', 0) for opp in opponents if opp in team_records])
        
        if opp_games > 0:
            sos_val = opp_wins / opp_games
            team_sos[t] = f".{int(round(sos_val * 1000)):03d}"
        else:
            team_sos[t] = ".500"

    # 4. Generate Dynamic Rankings & Base Playoff Odds
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
        print(f"Dynamic rankings and live SOS saved based on {ranking_year} season.")

    # 5. Machine Learning Training on 3-Year Historical Data
    pbp_rp = pbp[(pbp['pass'] == 1) | (pbp['rush'] == 1)].copy()
    historical_off_epa = pbp_rp.groupby('posteam')['epa'].mean().to_dict()
    historical_def_epa = pbp_rp.groupby('defteam')['epa'].mean().to_dict()

    all_completed_games = sched.dropna(subset=['result']).copy()
    print(f"Training ML model on {len(all_completed_games)} completed games across {years_to_pull}...")
    
    all_completed_games['home_win'] = (all_completed_games['result'] > 0).astype(int)
    all_completed_games['home_off_epa'] = all_completed_games['home_team'].map(lambda x: historical_off_epa.get(x, 0.0))
    all_completed_games['home_def_epa'] = all_completed_games['home_team'].map(lambda x: historical_def_epa.get(x, 0.0))
    all_completed_games['away_off_epa'] = all_completed_games['away_team'].map(lambda x: historical_off_epa.get(x, 0.0))
    all_completed_games['away_def_epa'] = all_completed_games['away_team'].map(lambda x: historical_def_epa.get(x, 0.0))

    features = ['spread_line', 'total_line', 'home_off_epa', 'home_def_epa', 'away_off_epa', 'away_def_epa']
    X_train = all_completed_games[features].fillna(0)
    y_train = all_completed_games['home_win']

    model = LogisticRegression()
    if not X_train.empty:
        model.fit(X_train, y_train)
    else:
        # Failsafe fallback
        model.fit([[-3.0, 45.0, 0, 0, 0, 0], [3.0, 45.0, 0, 0, 0, 0]], [1, 0])

    # 6. Predict Upcoming Matchups for the Current Year
    upcoming_games = current_sched[current_sched['result'].isna()].copy()
    if not upcoming_games.empty:
        upcoming_games['home_off_epa'] = upcoming_games['home_team'].map(lambda x: historical_off_epa.get(x, 0.0))
        upcoming_games['home_def_epa'] = upcoming_games['home_team'].map(lambda x: historical_def_epa.get(x, 0.0))
        upcoming_games['away_off_epa'] = upcoming_games['away_team'].map(lambda x: historical_off_epa.get(x, 0.0))
        upcoming_games['away_def_epa'] = upcoming_games['away_team'].map(lambda x: historical_def_epa.get(x, 0.0))
        
        X_predict = upcoming_games[features].fillna(0)
        probabilities = model.predict_proba(X_predict)
        
        upcoming_games['home_win_prob'] = probabilities[:, 1]
        upcoming_games['away_win_prob'] = probabilities[:, 0]
        
        output = upcoming_games[['game_id', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob']]
        output.to_csv("weekly_predictions.csv", index=False)
        print("Weekly matchup probabilities successfully saved to weekly_predictions.csv.")
    else:
        print("No upcoming games found to predict for the current year.")

if __name__ == "__main__":
    main()
