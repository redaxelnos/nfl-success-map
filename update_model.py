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
    for col in cols:
        if col in df.columns:
            df[col] = df[col].replace(NFL_ABBR_MAP)
    return df

def main():
    current_year = datetime.datetime.now().year
    years_to_pull = [current_year - 2, current_year - 1, current_year]
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

    # Determine Ranking Season
    current_completed = sched[(sched['season'] == current_year) & (sched['result'].notna())]
    ranking_year = current_year if len(current_completed) >= 10 else current_year - 1
    print(f"Generating Power Rankings & SOS baselines from {ranking_year} season...")

    # 3. Calculate Clean Season-Specific Metrics
    pbp_rank = pbp[pbp['season'] == ranking_year]
    off_epa_series = pbp_rank.groupby('posteam')['epa'].mean()
    def_epa_series = pbp_rank.groupby('defteam')['epa'].mean()
    
    # Turnover Differential
    pbp_rank_all = raw_pbp[raw_pbp['season'] == ranking_year].copy()
    pbp_rank_all = clean_abbr(pbp_rank_all, ['posteam', 'defteam'])
    to_takeaways = pbp_rank_all.groupby('defteam')['interception'].sum() + pbp_rank_all.groupby('defteam')['fumble_lost'].sum()
    to_giveaways = pbp_rank_all.groupby('posteam')['interception'].sum() + pbp_rank_all.groupby('posteam')['fumble_lost'].sum()
    turnover_margin = (to_takeaways.fillna(0) - to_giveaways.fillna(0)).to_dict()

    # Standings & SOS
    rank_games = sched[(sched['season'] == ranking_year) & (sched['result'].notna())]
    all_teams = sorted(list(set(sched['home_team'].unique()) | set(sched['away_team'].unique())))
    
    team_records = {t: {'points': 0, 'games': 0} for t in all_teams}
    for _, g in rank_games.iterrows():
        h, a, res = g['home_team'], g['away_team'], g['result']
        if h in team_records and a in team_records:
            team_records[h]['games'] += 1
            team_records[a]['games'] += 1
            if res > 0:
                team_records[h]['points'] += 1.0
            elif res < 0:
                team_records[a]['points'] += 1.0
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

        off_val = off_epa_series.get(t, 0.0)
        def_val = def_epa_series.get(t, 0.0)
        to_val = int(turnover_margin.get(t, 0))
        
        # Power Score Baseline
        rating = 1500.0 + (off_val * 140.0) - (def_val * 140.0) + (to_val * 4.0)
        t_pts = team_records[t]['points']
        t_gms = max(1, team_records[t]['games'])
        win_pct = t_pts / t_gms
        playoff_prob = round(1.0 / (1.0 + np.exp(-((rating - 1500.0) / 45.0 + (win_pct - 0.5) * 6.0))) * 100.0, 1)

        ranking_rows.append({
            'abbr': t,
            'raw_off': off_val,
            'raw_def': def_val,
            'TO': to_val,
            'SOS': f"{sos_num:.3f}",
            'Rating': round(rating, 1),
            'BasePlayoff': max(1.0, min(99.0, playoff_prob))
        })

    rank_df = pd.DataFrame(ranking_rows)
    rank_df['Off'] = rank_df['raw_off'].rank(ascending=False, method='min').astype(int)
    rank_df['Def'] = rank_df['raw_def'].rank(ascending=True, method='min').astype(int)
    rank_df[['abbr', 'Off', 'Def', 'TO', 'SOS', 'Rating', 'BasePlayoff']].to_csv("team_rankings.csv", index=False)
    print("Exported team_rankings.csv")

    # 4. Construct Leakage-Free Historical Features
    # Compute EPA strictly per-season to prevent multi-year future data leakage
    season_off_epa = pbp.groupby(['season', 'posteam'])['epa'].mean().to_dict()
    season_def_epa = pbp.groupby(['season', 'defteam'])['epa'].mean().to_dict()

    completed = sched[sched['result'].notna()].copy()
    completed = completed.sort_values(by=['season', 'week']).reset_index(drop=True)
    completed['home_win'] = (completed['result'] > 0).astype(int)
    
    # Feature lookup based on game's active season
    completed['home_off_epa'] = completed.apply(lambda r: season_off_epa.get((r['season'], r['home_team']), 0.0), axis=1)
    completed['home_def_epa'] = completed.apply(lambda r: season_def_epa.get((r['season'], r['home_team']), 0.0), axis=1)
    completed['away_off_epa'] = completed.apply(lambda r: season_off_epa.get((r['season'], r['away_team']), 0.0), axis=1)
    completed['away_def_epa'] = completed.apply(lambda r: season_def_epa.get((r['season'], r['away_team']), 0.0), axis=1)

    features = ['spread_line', 'total_line', 'home_off_epa', 'home_def_epa', 'away_off_epa', 'away_def_epa']
    X = completed[features].fillna(0)
    y = completed['home_win']

    # 5. Chronological Walk-Forward Backtesting (No Random Shuffling)
    if len(completed) > 50:
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

    # 6. Train Production Pipeline on Full Dataset
    prod_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(C=0.1, random_state=42))
    ])
    prod_pipe.fit(X, y)

    # 7. Predict Upcoming Regular Season Games
    upcoming = sched[(sched['season'] == current_year) & (sched['result'].isna())].copy()
    if not upcoming.empty:
        # Use ranking_year EPA for preseason baseline or current season when active
        upcoming['home_off_epa'] = upcoming['home_team'].map(lambda t: season_off_epa.get((ranking_year, t), 0.0))
        upcoming['home_def_epa'] = upcoming['home_team'].map(lambda t: season_def_epa.get((ranking_year, t), 0.0))
        upcoming['away_off_epa'] = upcoming['away_team'].map(lambda t: season_off_epa.get((ranking_year, t), 0.0))
        upcoming['away_def_epa'] = upcoming['away_team'].map(lambda t: season_def_epa.get((ranking_year, t), 0.0))

        X_upcoming = upcoming[features].fillna(0)
        probs = prod_pipe.predict_proba(X_upcoming)
        
        upcoming['home_win_prob'] = probs[:, 1]
        upcoming['away_win_prob'] = probs[:, 0]
        
        output = upcoming[['game_id', 'season', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob']]
        output.to_csv("weekly_predictions.csv", index=False)
        print("Exported weekly_predictions.csv")

if __name__ == "__main__":
    main()
