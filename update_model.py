import os
import datetime
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.linear_model import LogisticRegressionCV, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

# Canonical 32-team abbreviations
NFL_ABBR_MAP = {"LA": "LAR", "OAK": "LV", "SD": "LAC", "WSH": "WAS", "STL": "LAR"}
AFC_TEAMS = {'BAL', 'BUF', 'CIN', 'CLE', 'DEN', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LV', 'MIA', 'NE', 'NYJ', 'PIT', 'TEN'}
NFC_TEAMS = {'ARI', 'ATL', 'CAR', 'CHI', 'DAL', 'DET', 'GB', 'LAR', 'MIN', 'NO', 'NYG', 'PHI', 'SEA', 'SF', 'TB', 'WAS'}
TEAM_CONF = {t: 'AFC' for t in AFC_TEAMS}
TEAM_CONF.update({t: 'NFC' for t in NFC_TEAMS})

def clean_abbr(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = df[col].replace(NFL_ABBR_MAP)
    return df

def main():
    current_year = datetime.datetime.now().year
    years_to_pull = [current_year - 3, current_year - 2, current_year - 1, current_year]
    print(f"[{datetime.datetime.now()}] Ingesting data for seasons {years_to_pull}...")
    
    # 1. Pull & Normalize Data
    try:
        raw_sched = nfl.import_schedules(years_to_pull)
        raw_pbp = nfl.import_pbp_data(years_to_pull)
    except Exception as e:
        print(f"ERROR pulling nflverse data: {e}")
        return

    sched = raw_sched[raw_sched['game_type'] == 'REG'].copy()
    sched = clean_abbr(sched, ['home_team', 'away_team'])
    
    pbp = raw_pbp[(raw_pbp['pass'] == 1) | (raw_pbp['rush'] == 1)].copy()
    pbp = clean_abbr(pbp, ['posteam', 'defteam'])

    current_completed = sched[(sched['season'] == current_year) & (sched['result'].notna())]
    ranking_year = current_year if len(current_completed) >= 10 else current_year - 1
    all_teams = sorted(list(set(sched['home_team'].unique()) | set(sched['away_team'].unique())))

    # -------------------------------------------------------------------------
    # PART A: ADVANCED FEATURE ENGINEERING (Early Downs & Fumble Luck)
    # -------------------------------------------------------------------------
    print("Engineering Early-Down EPA & Expected Turnover (Luck-Regressed) metrics...")
    
    pbp['is_early_pass'] = ((pbp['pass'] == 1) & (pbp['down'].isin([1.0, 2.0]))).astype(int)
    pbp['is_rush'] = (pbp['rush'] == 1).astype(int)
    pbp['success'] = (pbp['epa'] > 0).astype(int)
    
    pbp['early_pass_epa'] = np.where(pbp['is_early_pass'] == 1, pbp['epa'], np.nan)
    pbp['rush_epa'] = np.where(pbp['is_rush'] == 1, pbp['epa'], np.nan)

    # Offense
    game_off = pbp.groupby(['game_id', 'season', 'week', 'posteam']).agg(
        off_early_pass_epa=('early_pass_epa', 'mean'),
        off_rush_epa=('rush_epa', 'mean'),
        off_success=('success', 'mean'),
        off_ints=('interception', 'sum'),
        off_fumbles=('fumble', 'sum'),
        off_fumbles_lost=('fumble_lost', 'sum')
    ).reset_index().rename(columns={'posteam': 'team'})
    
    # Defense
    game_def = pbp.groupby(['game_id', 'season', 'week', 'defteam']).agg(
        def_early_pass_epa=('early_pass_epa', 'mean'),
        def_rush_epa=('rush_epa', 'mean'),
        def_success=('success', 'mean'),
        def_ints=('interception', 'sum'),
        def_fumbles=('fumble', 'sum'),
        def_fumbles_lost=('fumble_lost', 'sum')
    ).reset_index().rename(columns={'defteam': 'team'})
    
    team_games = pd.merge(game_off, game_def, on=['game_id', 'season', 'week', 'team'], how='outer').fillna(0)
    
    # Expected Turnover Margin (Luck Regression: Fumble Recoveries treated as 50/50)
    team_games['exp_giveaways'] = team_games['off_ints'] + 0.5 * team_games['off_fumbles']
    team_games['exp_takeaways'] = team_games['def_ints'] + 0.5 * team_games['def_fumbles']
    team_games['exp_to_margin'] = team_games['exp_takeaways'] - team_games['exp_giveaways']
    team_games['actual_to_margin'] = (team_games['def_ints'] + team_games['def_fumbles_lost']) - (team_games['off_ints'] + team_games['off_fumbles_lost'])

    team_games = team_games.sort_values(['season', 'week']).reset_index(drop=True)
    
    # Expanding Windows & Season Rollovers (Zero Leakage)
    cols_to_expand = ['off_early_pass_epa', 'off_rush_epa', 'off_success',
                      'def_early_pass_epa', 'def_rush_epa', 'def_success',
                      'exp_to_margin', 'actual_to_margin']
    
    for c in cols_to_expand:
        team_games[f'cum_{c}'] = team_games.groupby(['season', 'team'])[c].transform(lambda x: x.expanding().mean().shift(1))
        
    season_means = team_games.groupby(['season', 'team'])[cols_to_expand].mean().reset_index()
    season_means['season'] += 1
    season_means = season_means.rename(columns={c: f'prev_{c}' for c in cols_to_expand})
    
    team_games = pd.merge(team_games, season_means, on=['season', 'team'], how='left')
    for c in cols_to_expand:
        team_games[f'cum_{c}'] = team_games[f'cum_{c}'].fillna(team_games[f'prev_{c}']).fillna(0)

    # Attach features to schedule
    home_features = team_games[['game_id', 'team'] + [f'cum_{c}' for c in cols_to_expand]].rename(
        columns={'team': 'home_team', **{f'cum_{c}': f'home_{c}' for c in cols_to_expand}})
    away_features = team_games[['game_id', 'team'] + [f'cum_{c}' for c in cols_to_expand]].rename(
        columns={'team': 'away_team', **{f'cum_{c}': f'away_{c}' for c in cols_to_expand}})

    sched = pd.merge(sched, home_features, on=['game_id', 'home_team'], how='left')
    sched = pd.merge(sched, away_features, on=['game_id', 'away_team'], how='left')

    # -------------------------------------------------------------------------
    # PART B: TIME-SERIES TUNED MACHINE LEARNING & MARKET DISCREPANCY
    # -------------------------------------------------------------------------
    print("Tuning Hyperparameters & Training Market Discrepancy Engine...")
    completed = sched[sched['result'].notna()].copy()
    completed = completed.sort_values(by=['season', 'week']).reset_index(drop=True)
    completed = completed.dropna(subset=['home_off_success', 'away_off_success'])
    completed['home_win'] = (completed['result'] > 0).astype(int)
    
    features = [
        'spread_line', 'total_line',
        'home_off_early_pass_epa', 'home_off_rush_epa', 'home_off_success',
        'home_def_early_pass_epa', 'home_def_rush_epa', 'home_def_success', 'home_exp_to_margin',
        'away_off_early_pass_epa', 'away_off_rush_epa', 'away_off_success',
        'away_def_early_pass_epa', 'away_def_rush_epa', 'away_def_success', 'away_exp_to_margin'
    ]
    
    X = completed[features].fillna(0)
    y_prob = completed['home_win']
    y_margin = completed['result'] # Result = Home Score - Away Score

    # Time-Series Split for proper chronological hyperparameter tuning
    tscv = TimeSeriesSplit(n_splits=5)

    # 1. Win Probability Pipeline
    prob_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegressionCV(Cs=10, cv=tscv, scoring='neg_log_loss', max_iter=1000, random_state=42))
    ])
    prob_pipe.fit(X, y_prob)

    # 2. Market Discrepancy Margin Pipeline
    margin_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RidgeCV(cv=tscv))
    ])
    margin_pipe.fit(X, y_margin)

    # Out-of-Sample Performance Logging
    if len(completed) > 50:
        split_idx = int(len(completed) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y_prob.iloc[:split_idx], y_prob.iloc[split_idx:]
        
        eval_pipe = Pipeline([('scaler', StandardScaler()), ('model', LogisticRegressionCV(Cs=10, cv=tscv, max_iter=1000))])
        eval_pipe.fit(X_train, y_train)
        preds = eval_pipe.predict(X_test)
        probs = eval_pipe.predict_proba(X_test)[:, 1]
        
        pd.DataFrame([{
            'accuracy': float(accuracy_score(y_test, preds)),
            'brier_score': float(brier_score_loss(y_test, probs)),
            'log_loss': float(log_loss(y_test, probs))
        }]).to_csv("model_metrics.csv", index=False)

    # -------------------------------------------------------------------------
    # PART C: DYNAMIC TEAM POWER RATINGS (EVALUATED VS "AVERAGE" TEAM)
    # -------------------------------------------------------------------------
    print("Projecting True Team Power Ratings via Margin Regression...")
    latest_metrics = {}
    for t in all_teams:
        curr = team_games[(team_games['season'] == ranking_year) & (team_games['team'] == t)]
        if not curr.empty:
            latest_metrics[t] = {c: curr[f'cum_{c}'].iloc[-1] for c in cols_to_expand}
        else:
            prev = team_games[(team_games['season'] == ranking_year - 1) & (team_games['team'] == t)]
            latest_metrics[t] = {c: prev[f'cum_{c}'].iloc[-1] if not prev.empty else 0.0 for c in cols_to_expand}

    avg_features = X.mean().to_dict()
    ratings = {}
    
    # Calculate Power Rating by forcing each team to play a mathematically "Average" opponent
    for t in all_teams:
        mock_game = avg_features.copy()
        mock_game['spread_line'] = 0.0  # Neutral Field
        mock_game['total_line'] = 45.0  # League Average Total
        
        mock_game['home_off_early_pass_epa'] = latest_metrics[t]['off_early_pass_epa']
        mock_game['home_off_rush_epa'] = latest_metrics[t]['off_rush_epa']
        mock_game['home_off_success'] = latest_metrics[t]['off_success']
        mock_game['home_def_early_pass_epa'] = latest_metrics[t]['def_early_pass_epa']
        mock_game['home_def_rush_epa'] = latest_metrics[t]['def_rush_epa']
        mock_game['home_def_success'] = latest_metrics[t]['def_success']
        mock_game['home_exp_to_margin'] = latest_metrics[t]['exp_to_margin']
        
        mock_df = pd.DataFrame([mock_game])[features]
        expected_pt_diff = margin_pipe.predict(mock_df)[0]
        ratings[t] = 1500.0 + (expected_pt_diff * (400.0 / 14.0)) # Scale to Elo

    # -------------------------------------------------------------------------
    # PART D: PREDICT MATCHUPS & CALCULATE MARKET EDGE
    # -------------------------------------------------------------------------
    upcoming = sched[(sched['season'] == current_year) & (sched['result'].isna())].copy()
    
    # Fast 10k Monte Carlo Playoffs
    playoff_probs = {t: 50.0 for t in all_teams}
    if not upcoming.empty:
        for t in all_teams:
            upcoming[f'home_{t}'] = upcoming['home_team'] == t
            upcoming.loc[upcoming['home_team'] == t, 'home_off_early_pass_epa'] = latest_metrics[t]['off_early_pass_epa']
            upcoming.loc[upcoming['home_team'] == t, 'home_off_rush_epa'] = latest_metrics[t]['off_rush_epa']
            upcoming.loc[upcoming['home_team'] == t, 'home_off_success'] = latest_metrics[t]['off_success']
            upcoming.loc[upcoming['home_team'] == t, 'home_def_early_pass_epa'] = latest_metrics[t]['def_early_pass_epa']
            upcoming.loc[upcoming['home_team'] == t, 'home_def_rush_epa'] = latest_metrics[t]['def_rush_epa']
            upcoming.loc[upcoming['home_team'] == t, 'home_def_success'] = latest_metrics[t]['def_success']
            upcoming.loc[upcoming['home_team'] == t, 'home_exp_to_margin'] = latest_metrics[t]['exp_to_margin']
            
            upcoming.loc[upcoming['away_team'] == t, 'away_off_early_pass_epa'] = latest_metrics[t]['off_early_pass_epa']
            upcoming.loc[upcoming['away_team'] == t, 'away_off_rush_epa'] = latest_metrics[t]['off_rush_epa']
            upcoming.loc[upcoming['away_team'] == t, 'away_off_success'] = latest_metrics[t]['off_success']
            upcoming.loc[upcoming['away_team'] == t, 'away_def_early_pass_epa'] = latest_metrics[t]['def_early_pass_epa']
            upcoming.loc[upcoming['away_team'] == t, 'away_def_rush_epa'] = latest_metrics[t]['def_rush_epa']
            upcoming.loc[upcoming['away_team'] == t, 'away_def_success'] = latest_metrics[t]['def_success']
            upcoming.loc[upcoming['away_team'] == t, 'away_exp_to_margin'] = latest_metrics[t]['exp_to_margin']

        X_upcoming = upcoming[features].fillna(0)
        
        # 1. Calculate Probabilities
        probs = prob_pipe.predict_proba(X_upcoming)
        upcoming['home_win_prob'] = probs[:, 1]
        upcoming['away_win_prob'] = probs[:, 0]
        
        # 2. Calculate Market Edge via Discrepancy Engine
        upcoming['model_margin'] = margin_pipe.predict(X_upcoming)
        upcoming['market_margin'] = -upcoming['spread_line'].fillna(0) # Invert spread_line to match margin perspective
        upcoming['home_edge'] = upcoming['model_margin'] - upcoming['market_margin']
        
        upcoming[['game_id', 'season', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob', 'model_margin', 'market_margin', 'home_edge']].to_csv("weekly_predictions.csv", index=False)
        print("Exported weekly_predictions.csv with Market Edges.")

        # Monte Carlo Base Wins
        base_wins = {t: 0.0 for t in all_teams}
        for _, g in sched[(sched['season'] == current_year) & (sched['result'].notna())].iterrows():
            if g['result'] > 0: base_wins[g['home_team']] += 1.0
            elif g['result'] < 0: base_wins[g['away_team']] += 1.0
            else: base_wins[g['home_team']] += 0.5; base_wins[g['away_team']] += 0.5

        n_sims = 10000
        sim_draws = np.random.rand(n_sims, len(upcoming))
        sim_hw = (sim_draws < upcoming['home_win_prob'].values).astype(float)
        sim_aw = 1.0 - sim_hw
        
        sim_st = {t: np.full(n_sims, base_wins.get(t, 0.0)) for t in all_teams}
        for i, (h, a) in enumerate(zip(upcoming['home_team'].values, upcoming['away_team'].values)):
            sim_st[h] += sim_hw[:, i]
            sim_st[a] += sim_aw[:, i]
            
        for t in all_teams: sim_st[t] += np.random.rand(n_sims) * 0.1
        
        afc_m = np.array([sim_st[t] for t in [x for x in all_teams if TEAM_CONF.get(x) == 'AFC']])
        nfc_m = np.array([sim_st[t] for t in [x for x in all_teams if TEAM_CONF.get(x) == 'NFC']])
        
        afc_p = afc_m >= np.partition(afc_m, -7, axis=0)[-7, :]
        nfc_p = nfc_m >= np.partition(nfc_m, -7, axis=0)[-7, :]
        
        for i, t in enumerate([x for x in all_teams if TEAM_CONF.get(x) == 'AFC']): playoff_probs[t] = (np.sum(afc_p[i, :]) / n_sims) * 100.0
        for i, t in enumerate([x for x in all_teams if TEAM_CONF.get(x) == 'NFC']): playoff_probs[t] = (np.sum(nfc_p[i, :]) / n_sims) * 100.0

    # -------------------------------------------------------------------------
    # PART E: EXPORT RANKINGS FOR DASHBOARD
    # -------------------------------------------------------------------------
    rank_games_hist = sched[(sched['season'] == ranking_year) & (sched['result'].notna())]
    hist_wins = {t: sum([1.0 if r>0 else 0.5 for _,_,r in rank_games_hist[rank_games_hist['home_team']==t].itertuples(index=False)]) + 
                    sum([1.0 if r<0 else 0.5 for _,_,r in rank_games_hist[rank_games_hist['away_team']==t].itertuples(index=False)]) for t in all_teams}
    hist_gms = {t: len(rank_games_hist[(rank_games_hist['home_team']==t) | (rank_games_hist['away_team']==t)]) for t in all_teams}

    team_sos = {}
    for t in all_teams:
        opps = sched[(sched['season'] == ranking_year) & ((sched['home_team'] == t) | (sched['away_team'] == t))]
        opp_list = [r['away_team'] if r['home_team'] == t else r['home_team'] for _, r in opps.iterrows()]
        o_pts = sum([hist_wins.get(o, 0.0) for o in opp_list])
        o_gms = sum([hist_gms.get(o, 0) for o in opp_list])
        team_sos[t] = f".{int(round((o_pts / o_gms) * 1000)):03d}" if o_gms > 0 else ".500"

    ranking_rows = [{
        'abbr': t,
        'raw_off': latest_metrics[t]['off_early_pass_epa'], # Rank Offense by stable early-down passing
        'raw_def': latest_metrics[t]['def_success'],        # Rank Defense by overall play success rate allowed
        'TO': int(latest_metrics[t]['actual_to_margin']),
        'SOS': team_sos.get(t, ".500"),
        'Rating': round(ratings[t], 1),
        'BasePlayoff': round(playoff_probs[t], 1)
    } for t in all_teams]

    rank_df = pd.DataFrame(ranking_rows)
    if not rank_df.empty:
        rank_df['Off'] = rank_df['raw_off'].rank(ascending=False, method='min').astype(int)
        rank_df['Def'] = rank_df['raw_def'].rank(ascending=True, method='min').astype(int)
        rank_df[['abbr', 'Off', 'Def', 'TO', 'SOS', 'Rating', 'BasePlayoff']].to_csv("team_rankings.csv", index=False)
        print("Exported team_rankings.csv successfully.")

if __name__ == "__main__":
    main()
