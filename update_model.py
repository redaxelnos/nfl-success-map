import os
import datetime
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

# Canonical 32-team abbreviations matching ESPN/Frontend
NFL_ABBR_MAP = {
    "LA": "LAR", "OAK": "LV", "SD": "LAC", "WSH": "WAS", "STL": "LAR"
}

def clean_abbr(df, cols):
    """Standardizes team abbreviations across all nflverse data to prevent join failures."""
    for col in cols:
        if col in df.columns:
            df[col] = df[col].replace(NFL_ABBR_MAP)
    return df

def main():
    current_year = datetime.datetime.now().year
    # Pull 4 years to ensure the earliest training year has a prior year to roll over from for Week 1
    years_to_pull = [current_year - 3, current_year - 2, current_year - 1, current_year]
    print(f"[{datetime.datetime.now()}] Ingesting data for seasons {years_to_pull}...")
    
    # 1. Pull & Normalize Schedules
    try:
        raw_sched = nfl.import_schedules(years_to_pull)
    except Exception as e:
        print(f"ERROR: Could not pull NFL schedules: {e}")
        return

    # Strictly filter for Regular Season to prevent backup/preseason chaos from distorting baselines
    sched = raw_sched[raw_sched['game_type'] == 'REG'].copy()
    sched = clean_abbr(sched, ['home_team', 'away_team'])
    
    # 2. Pull & Normalize Play-by-Play
    try:
        raw_pbp = nfl.import_pbp_data(years_to_pull)
    except Exception as e:
        print(f"ERROR: Could not pull NFL play-by-play data: {e}")
        return

    pbp = raw_pbp[(raw_pbp['pass'] == 1) | (raw_pbp['rush'] == 1)].copy()
    pbp = clean_abbr(pbp, ['posteam', 'defteam'])

    # Determine Ranking Season (Fall back to prior year if current season is in preseason/Week 1)
    current_completed = sched[(sched['season'] == current_year) & (sched['result'].notna())]
    ranking_year = current_year if len(current_completed) >= 10 else current_year - 1

    all_teams = sorted(list(set(sched['home_team'].unique()) | set(sched['away_team'].unique())))

    # -------------------------------------------------------------------------
    # PART A: CUMULATIVE EXPANDING WINDOW FEATURE ENGINEERING (ZERO LEAKAGE)
    # -------------------------------------------------------------------------
    
    # Calculate per-game Offense and Defense EPA
    game_off = pbp.groupby(['game_id', 'season', 'week', 'posteam'])['epa'].mean().reset_index()
    game_off = game_off.rename(columns={'posteam': 'team', 'epa': 'game_off_epa'})
    
    game_def = pbp.groupby(['game_id', 'season', 'week', 'defteam'])['epa'].mean().reset_index()
    game_def = game_def.rename(columns={'defteam': 'team', 'epa': 'game_def_epa'})

    # Merge into a chronologically sorted team game log
    team_games = pd.merge(game_off, game_def, on=['game_id', 'season', 'week', 'team'], how='outer')
    team_games = team_games.sort_values(['season', 'week']).reset_index(drop=True)

    # 1. Calculate the cumulative average strictly PRIOR to the current game using .shift(1)
    team_games['cum_off_epa'] = team_games.groupby(['season', 'team'])['game_off_epa'].transform(lambda x: x.expanding().mean().shift(1))
    team_games['cum_def_epa'] = team_games.groupby(['season', 'team'])['game_def_epa'].transform(lambda x: x.expanding().mean().shift(1))

    # 2. Build the Offseason Rollover for Week 1 (Uses final true average of the prior year)
    season_means = team_games.groupby(['season', 'team'])[['game_off_epa', 'game_def_epa']].mean().reset_index()
    season_means['season'] += 1 # Shift the year forward to act as the baseline for the next season
    season_means = season_means.rename(columns={'game_off_epa': 'prev_off_epa', 'game_def_epa': 'prev_def_epa'})

    # 3. Apply the Rollover
    team_games = pd.merge(team_games, season_means, on=['season', 'team'], how='left')
    team_games['cum_off_epa'] = team_games['cum_off_epa'].fillna(team_games['prev_off_epa']).fillna(0)
    team_games['cum_def_epa'] = team_games['cum_def_epa'].fillna(team_games['prev_def_epa']).fillna(0)

    # 4. Attach strict, no-leakage features back to the schedule
    home_features = team_games[['game_id', 'team', 'cum_off_epa', 'cum_def_epa']].rename(
        columns={'team': 'home_team', 'cum_off_epa': 'home_off_epa', 'cum_def_epa': 'home_def_epa'})
    away_features = team_games[['game_id', 'team', 'cum_off_epa', 'cum_def_epa']].rename(
        columns={'team': 'away_team', 'cum_off_epa': 'away_off_epa', 'cum_def_epa': 'away_def_epa'})

    sched = pd.merge(sched, home_features, on=['game_id', 'home_team'], how='left')
    sched = pd.merge(sched, away_features, on=['game_id', 'away_team'], how='left')

    # -------------------------------------------------------------------------
    # PART B: STATIC POWER RANKINGS & SOS FOR DASHBOARD VISUALS
    # -------------------------------------------------------------------------
    print(f"Generating Static Power Rankings & SOS baselines from {ranking_year} season...")
    pbp_rank = pbp[pbp['season'] == ranking_year]
    off_epa_static = pbp_rank.groupby('posteam')['epa'].mean()
    def_epa_static = pbp_rank.groupby('defteam')['epa'].mean()
    
    # Turnover Differential
    raw_pbp_rank = raw_pbp[raw_pbp['season'] == ranking_year].copy()
    raw_pbp_rank = clean_abbr(raw_pbp_rank, ['posteam', 'defteam'])
    to_take = raw_pbp_rank.groupby('defteam')['interception'].sum() + raw_pbp_rank.groupby('defteam')['fumble_lost'].sum()
    to_give = raw_pbp_rank.groupby('posteam')['interception'].sum() + raw_pbp_rank.groupby('posteam')['fumble_lost'].sum()
    to_margin = (to_take.fillna(0) - to_give.fillna(0)).to_dict()

    rank_games = sched[(sched['season'] == ranking_year) & (sched['result'].notna())]
    team_records = {t: {'points': 0, 'games': 0} for t in all_teams}
    
    for _, g in rank_games.iterrows():
        h, a, res = g['home_team'], g['away_team'], g['result']
        if h in team_records and a in team_records:
            team_records[h]['games'] += 1
            team_records[a]['games'] += 1
            if res > 0: team_records[h]['points'] += 1.0
            elif res < 0: team_records[a]['points'] += 1.0
            else: 
                team_records[h]['points'] += 0.5
                team_records[a]['points'] += 0.5

    rank_full_sched = sched[sched['season'] == ranking_year]
    ranking_rows = []
    
    for t in all_teams:
        t_sched = rank_full_sched[(rank_full_sched['home_team'] == t) | (rank_full_sched['away_team'] == t)]
        opps = [r['away_team'] if r['home_team'] == t else r['home_team'] for _, r in t_sched.iterrows()]
        
        opp_pts = sum([team_records[o]['points'] for o in opps if o in team_records])
        opp_gms = sum([team_records[o]['games'] for o in opps if o in team_records])
        sos_num = (opp_pts / opp_gms) if opp_gms > 0 else 0.500

        off_val = off_epa_static.get(t, 0.0)
        def_val = def_epa_static.get(t, 0.0)
        to_val = int(to_margin.get(t, 0))
        
        rating = 1500.0 + (off_val * 140.0) - (def_val * 140.0) + (to_val * 4.0)
        t_pts = team_records[t]['points']
        t_gms = max(1, team_records[t]['games'])
        playoff_prob = round(1.0 / (1.0 + np.exp(-((rating - 1500.0) / 45.0 + ((t_pts / t_gms) - 0.5) * 6.0))) * 100.0, 1)

        ranking_rows.append({
            'abbr': t, 'raw_off': off_val, 'raw_def': def_val, 'TO': to_val,
            'SOS': f"{sos_num:.3f}", 'Rating': round(rating, 1), 'BasePlayoff': max(1.0, min(99.0, playoff_prob))
        })

    rank_df = pd.DataFrame(ranking_rows)
    if not rank_df.empty:
        rank_df['Off'] = rank_df['raw_off'].rank(ascending=False, method='min').astype(int)
        rank_df['Def'] = rank_df['raw_def'].rank(ascending=True, method='min').astype(int)
        rank_df[['abbr', 'Off', 'Def', 'TO', 'SOS', 'Rating', 'BasePlayoff']].to_csv("team_rankings.csv", index=False)
        print("Exported team_rankings.csv")

    # -------------------------------------------------------------------------
    # PART C: CHRONOLOGICAL ML TRAINING & TRUE OUT-OF-SAMPLE EVALUATION
    # -------------------------------------------------------------------------
    completed = sched[sched['result'].notna()].copy()
    completed = completed.sort_values(by=['season', 'week']).reset_index(drop=True)
    completed = completed.dropna(subset=['home_off_epa', 'away_off_epa']) # Drop very first week of dataset if no rollover
    completed['home_win'] = (completed['result'] > 0).astype(int)

    features = ['spread_line', 'total_line', 'home_off_epa', 'home_def_epa', 'away_off_epa', 'away_def_epa']
    X = completed[features].fillna(0)
    y = completed['home_win']

    if len(completed) > 50:
        # Time-Series Split: Train on past, evaluate strictly on future
        split_idx = int(len(completed) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        eval_pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('model', LogisticRegression(C=0.1, random_state=42))
        ])
        eval_pipe.fit(X_train, y_train)

        y_pred = eval_pipe.predict(X_test)
        y_prob = eval_pipe.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        brier = float(brier_score_loss(y_test, y_prob))
        ll = float(log_loss(y_test, y_prob))
        
        pd.DataFrame([{'accuracy': acc, 'brier_score': brier, 'log_loss': ll}]).to_csv("model_metrics.csv", index=False)
        print(f"Validated Model (Out-of-Time): Acc={acc:.3f}, Brier={brier:.3f}, LogLoss={ll:.3f}")

    # Train production pipeline on ALL known data for max predictive power
    prod_pipe = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(C=0.1, random_state=42))])
    prod_pipe.fit(X, y)

    # -------------------------------------------------------------------------
    # PART D: PREDICT UPCOMING MATCHUPS
    # -------------------------------------------------------------------------
    upcoming = sched[(sched['season'] == current_year) & (sched['result'].isna())].copy()
    if not upcoming.empty:
        
        # Calculate the absolute latest known EPA for each team
        latest_epa = {}
        for t in all_teams:
            curr_games = team_games[(team_games['season'] == current_year) & (team_games['team'] == t)]
            if len(curr_games) > 0: # Middle of season: Use current year average
                off_val = curr_games['game_off_epa'].mean()
                def_val = curr_games['game_def_epa'].mean()
            else: # Preseason/Week 1: Fall back to prior year final average
                prev_games = team_games[(team_games['season'] == current_year - 1) & (team_games['team'] == t)]
                off_val = prev_games['game_off_epa'].mean() if len(prev_games) > 0 else 0.0
                def_val = prev_games['game_def_epa'].mean() if len(prev_games) > 0 else 0.0
            latest_epa[t] = {'off': off_val, 'def': def_val}

        upcoming['home_off_epa'] = upcoming['home_team'].map(lambda t: latest_epa.get(t, {}).get('off', 0.0))
        upcoming['home_def_epa'] = upcoming['home_team'].map(lambda t: latest_epa.get(t, {}).get('def', 0.0))
        upcoming['away_off_epa'] = upcoming['away_team'].map(lambda t: latest_epa.get(t, {}).get('off', 0.0))
        upcoming['away_def_epa'] = upcoming['away_team'].map(lambda t: latest_epa.get(t, {}).get('def', 0.0))

        X_upcoming = upcoming[features].fillna(0)
        probs = prod_pipe.predict_proba(X_upcoming)
        
        upcoming['home_win_prob'] = probs[:, 1]
        upcoming['away_win_prob'] = probs[:, 0]
        
        output = upcoming[['game_id', 'season', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob']]
        output.to_csv("weekly_predictions.csv", index=False)
        print("Exported weekly_predictions.csv")

if __name__ == "__main__":
    main()
