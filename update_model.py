import os
import datetime
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

# Canonical 32-team abbreviations matching ESPN/Frontend
NFL_ABBR_MAP = {
    "LA": "LAR", "OAK": "LV", "SD": "LAC", "WSH": "WAS", "STL": "LAR"
}

AFC_TEAMS = {'BAL', 'BUF', 'CIN', 'CLE', 'DEN', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LV', 'MIA', 'NE', 'NYJ', 'PIT', 'TEN'}
NFC_TEAMS = {'ARI', 'ATL', 'CAR', 'CHI', 'DAL', 'DET', 'GB', 'LAR', 'MIN', 'NO', 'NYG', 'PHI', 'SEA', 'SF', 'TB', 'WAS'}
TEAM_CONF = {t: 'AFC' for t in AFC_TEAMS}
TEAM_CONF.update({t: 'NFC' for t in NFC_TEAMS})

def clean_abbr(df, cols):
    """Standardizes team abbreviations across all nflverse data to prevent join failures."""
    for col in cols:
        if col in df.columns:
            df[col] = df[col].replace(NFL_ABBR_MAP)
    return df

def main():
    current_year = datetime.datetime.now().year
    years_to_pull = [current_year - 3, current_year - 2, current_year - 1, current_year]
    print(f"[{datetime.datetime.now()}] Ingesting data for seasons {years_to_pull}...")
    
    # 1. Pull & Normalize Schedules
    try:
        raw_sched = nfl.import_schedules(years_to_pull)
    except Exception as e:
        print(f"ERROR: Could not pull NFL schedules: {e}")
        return

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
    raw_pbp_clean = clean_abbr(raw_pbp.copy(), ['posteam', 'defteam'])

    current_completed = sched[(sched['season'] == current_year) & (sched['result'].notna())]
    ranking_year = current_year if len(current_completed) >= 10 else current_year - 1

    all_teams = sorted(list(set(sched['home_team'].unique()) | set(sched['away_team'].unique())))

    # -------------------------------------------------------------------------
    # PART A: CUMULATIVE EXPANDING WINDOW FEATURE ENGINEERING (ZERO LEAKAGE)
    # -------------------------------------------------------------------------
    game_off = pbp.groupby(['game_id', 'season', 'week', 'posteam'])['epa'].mean().reset_index()
    game_off = game_off.rename(columns={'posteam': 'team', 'epa': 'game_off_epa'})
    
    game_def = pbp.groupby(['game_id', 'season', 'week', 'defteam'])['epa'].mean().reset_index()
    game_def = game_def.rename(columns={'defteam': 'team', 'epa': 'game_def_epa'})

    team_games = pd.merge(game_off, game_def, on=['game_id', 'season', 'week', 'team'], how='outer')
    team_games = team_games.sort_values(['season', 'week']).reset_index(drop=True)

    team_games['cum_off_epa'] = team_games.groupby(['season', 'team'])['game_off_epa'].transform(lambda x: x.expanding().mean().shift(1))
    team_games['cum_def_epa'] = team_games.groupby(['season', 'team'])['game_def_epa'].transform(lambda x: x.expanding().mean().shift(1))

    season_means = team_games.groupby(['season', 'team'])[['game_off_epa', 'game_def_epa']].mean().reset_index()
    season_means['season'] += 1
    season_means = season_means.rename(columns={'game_off_epa': 'prev_off_epa', 'game_def_epa': 'prev_def_epa'})

    team_games = pd.merge(team_games, season_means, on=['season', 'team'], how='left')
    team_games['cum_off_epa'] = team_games['cum_off_epa'].fillna(team_games['prev_off_epa']).fillna(0)
    team_games['cum_def_epa'] = team_games['cum_def_epa'].fillna(team_games['prev_def_epa']).fillna(0)

    home_features = team_games[['game_id', 'team', 'cum_off_epa', 'cum_def_epa']].rename(
        columns={'team': 'home_team', 'cum_off_epa': 'home_off_epa', 'cum_def_epa': 'home_def_epa'})
    away_features = team_games[['game_id', 'team', 'cum_off_epa', 'cum_def_epa']].rename(
        columns={'team': 'away_team', 'cum_off_epa': 'away_off_epa', 'cum_def_epa': 'away_def_epa'})

    sched = pd.merge(sched, home_features, on=['game_id', 'home_team'], how='left')
    sched = pd.merge(sched, away_features, on=['game_id', 'away_team'], how='left')

    # -------------------------------------------------------------------------
    # PART B: MACHINE LEARNING MODELS (RIDGE RATING + LOGISTIC PROBABILITY)
    # -------------------------------------------------------------------------
    completed = sched[sched['result'].notna()].copy()
    completed = completed.sort_values(by=['season', 'week']).reset_index(drop=True)
    completed = completed.dropna(subset=['home_off_epa', 'away_off_epa'])
    completed['home_win'] = (completed['result'] > 0).astype(int)
    
    # 1. Ridge Regression for Adaptive Power Ratings (Learns Scoreboard Value of EPA)
    completed['diff_off'] = completed['home_off_epa'] - completed['away_off_epa']
    completed['diff_def'] = completed['home_def_epa'] - completed['away_def_epa']
    
    rating_model = Ridge(alpha=1.0)
    rating_model.fit(completed[['diff_off', 'diff_def']], completed['result'])
    beta_off, beta_def = rating_model.coef_
    
    # 2. Logistic Regression for Win Probability Forecasts
    features = ['spread_line', 'total_line', 'home_off_epa', 'home_def_epa', 'away_off_epa', 'away_def_epa']
    X = completed[features].fillna(0)
    y = completed['home_win']

    if len(completed) > 50:
        split_idx = int(len(completed) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        eval_pipe = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(C=0.1, random_state=42))])
        eval_pipe.fit(X_train, y_train)

        y_pred = eval_pipe.predict(X_test)
        y_prob = eval_pipe.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        brier = float(brier_score_loss(y_test, y_prob))
        ll = float(log_loss(y_test, y_prob))
        
        pd.DataFrame([{'accuracy': acc, 'brier_score': brier, 'log_loss': ll}]).to_csv("model_metrics.csv", index=False)

    prod_pipe = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(C=0.1, random_state=42))])
    prod_pipe.fit(X, y)

    # -------------------------------------------------------------------------
    # PART C: DYNAMIC TEAM RANKINGS & MONTE CARLO PLAYOFF SIMULATION
    # -------------------------------------------------------------------------
    print("Generating fully dynamic, learned Team Rankings and Monte Carlo Playoff Odds...")
    
    # Isolate Current Active Efficiency Metrics
    latest_epa = {}
    for t in all_teams:
        curr_games = team_games[(team_games['season'] == ranking_year) & (team_games['team'] == t)]
        if len(curr_games) > 0:
            latest_epa[t] = {'off': curr_games['game_off_epa'].mean(), 'def': curr_games['game_def_epa'].mean()}
        else:
            prev_games = team_games[(team_games['season'] == ranking_year - 1) & (team_games['team'] == t)]
            latest_epa[t] = {
                'off': prev_games['game_off_epa'].mean() if len(prev_games) > 0 else 0.0,
                'def': prev_games['game_def_epa'].mean() if len(prev_games) > 0 else 0.0
            }

    # Derive Power Rating from Adaptive Ridge Coefficients
    ratings = {}
    for t in all_teams:
        pts_above_avg = (beta_off * latest_epa[t]['off']) + (beta_def * latest_epa[t]['def'])
        ratings[t] = 1500.0 + (pts_above_avg * (400.0 / 14.0))

    # Predict entire remaining schedule
    upcoming = sched[(sched['season'] == current_year) & (sched['result'].isna())].copy()
    if not upcoming.empty:
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

    # Fast Vectorized 10,000-Iteration Monte Carlo Simulation
    rank_games = sched[(sched['season'] == current_year) & (sched['result'].notna())]
    base_wins = {t: 0.0 for t in all_teams}
    for _, g in rank_games.iterrows():
        if g['result'] > 0: base_wins[g['home_team']] += 1.0
        elif g['result'] < 0: base_wins[g['away_team']] += 1.0
        else:
            base_wins[g['home_team']] += 0.5
            base_wins[g['away_team']] += 0.5

    n_sims = 10000
    playoff_probs = {t: 50.0 for t in all_teams}
    
    if not upcoming.empty:
        home_teams = upcoming['home_team'].values
        away_teams = upcoming['away_team'].values
        home_probs = upcoming['home_win_prob'].values
        
        sim_draws = np.random.rand(n_sims, len(upcoming))
        sim_home_wins = (sim_draws < home_probs).astype(float)
        sim_away_wins = 1.0 - sim_home_wins
        
        sim_standings = {t: np.full(n_sims, base_wins.get(t, 0.0)) for t in all_teams}
        for i in range(len(upcoming)):
            h, a = home_teams[i], away_teams[i]
            sim_standings[h] += sim_home_wins[:, i]
            sim_standings[a] += sim_away_wins[:, i]
            
        for t in all_teams:
            sim_standings[t] += np.random.rand(n_sims) * 0.1 # Tiebreaker resolution noise
            
        afc_teams = [t for t in all_teams if TEAM_CONF.get(t) == 'AFC']
        nfc_teams = [t for t in all_teams if TEAM_CONF.get(t) == 'NFC']
        
        afc_matrix = np.array([sim_standings[t] for t in afc_teams])
        nfc_matrix = np.array([sim_standings[t] for t in nfc_teams])
        
        # Sort divisions & conferences to find top 7 seeds
        afc_thresh = np.partition(afc_matrix, -7, axis=0)[-7, :]
        nfc_thresh = np.partition(nfc_matrix, -7, axis=0)[-7, :]
        
        afc_playoffs = afc_matrix >= afc_thresh
        nfc_playoffs = nfc_matrix >= nfc_thresh
        
        for i, t in enumerate(afc_teams): playoff_probs[t] = (np.sum(afc_playoffs[i, :]) / n_sims) * 100.0
        for i, t in enumerate(nfc_teams): playoff_probs[t] = (np.sum(nfc_playoffs[i, :]) / n_sims) * 100.0

    # Calculate SOS and Turnover Displays
    rank_full_sched = sched[sched['season'] == ranking_year]
    rank_games_hist = sched[(sched['season'] == ranking_year) & (sched['result'].notna())]
    hist_wins = {t: 0.0 for t in all_teams}
    hist_games = {t: 0 for t in all_teams}
    
    for _, g in rank_games_hist.iterrows():
        h, a, res = g['home_team'], g['away_team'], g['result']
        hist_games[h] += 1
        hist_games[a] += 1
        if res > 0: hist_wins[h] += 1.0
        elif res < 0: hist_wins[a] += 1.0
        else:
            hist_wins[h] += 0.5
            hist_wins[a] += 0.5

    team_sos = {}
    for t in all_teams:
        t_sched = rank_full_sched[(rank_full_sched['home_team'] == t) | (rank_full_sched['away_team'] == t)]
        opps = [r['away_team'] if r['home_team'] == t else r['home_team'] for _, r in t_sched.iterrows()]
        
        opp_pts = sum([hist_wins.get(o, 0.0) for o in opps])
        opp_gms = sum([hist_games.get(o, 0) for o in opps])
        sos_num = (opp_pts / opp_gms) if opp_gms > 0 else 0.500
        team_sos[t] = f".{int(round(sos_num * 1000)):03d}"

    to_pbp = raw_pbp_clean[raw_pbp_clean['season'] == ranking_year]
    to_take = to_pbp.groupby('defteam')['interception'].sum() + to_pbp.groupby('defteam')['fumble_lost'].sum()
    to_give = to_pbp.groupby('posteam')['interception'].sum() + to_pbp.groupby('posteam')['fumble_lost'].sum()
    to_margin = (to_take.fillna(0) - to_give.fillna(0)).to_dict()

    ranking_rows = []
    for t in all_teams:
        ranking_rows.append({
            'abbr': t,
            'raw_off': latest_epa[t]['off'],
            'raw_def': latest_epa[t]['def'],
            'TO': int(to_margin.get(t, 0)),
            'SOS': team_sos.get(t, ".500"),
            'Rating': round(ratings[t], 1),
            'BasePlayoff': round(playoff_probs[t], 1)
        })

    rank_df = pd.DataFrame(ranking_rows)
    if not rank_df.empty:
        rank_df['Off'] = rank_df['raw_off'].rank(ascending=False, method='min').astype(int)
        rank_df['Def'] = rank_df['raw_def'].rank(ascending=True, method='min').astype(int)
        rank_df[['abbr', 'Off', 'Def', 'TO', 'SOS', 'Rating', 'BasePlayoff']].to_csv("team_rankings.csv", index=False)

if __name__ == "__main__":
    main()
