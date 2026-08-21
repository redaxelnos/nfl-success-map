import nfl_data_py as nfl
import pandas as pd
from sklearn.linear_model import LogisticRegression
import datetime

def main():
    # 1. Define current parameters
    current_year = datetime.datetime.now().year
    
    # 2. Ingest Open Source NFL Schedule & Results
    print(f"Pulling schedule data for {current_year}...")
    sched = nfl.import_schedules([current_year])
    
    completed_games = sched.dropna(subset=['result']).copy()
    
    if completed_games.empty:
        print("Not enough current season data. Run this after Week 1.")
        return

    # 3. Feature Engineering (Simplified)
    completed_games['home_win'] = (completed_games['result'] > 0).astype(int)
    features = ['spread_line', 'total_line']
    X_train = completed_games[features].fillna(0)
    y_train = completed_games['home_win']

    # 4. Train the AI / Statistical Model
    print("Training scikit-learn Logistic Regression model...")
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # 5. Predict Upcoming Week's Odds
    upcoming_games = sched[sched['result'].isna()].copy()
    
    if not upcoming_games.empty:
        X_predict = upcoming_games[features].fillna(0)
        
        probabilities = model.predict_proba(X_predict)
        
        upcoming_games['home_win_prob'] = probabilities[:, 1]
        upcoming_games['away_win_prob'] = probabilities[:, 0]
        
        output = upcoming_games[['game_id', 'week', 'home_team', 'away_team', 'home_win_prob', 'away_win_prob']]
        
        # 6. Export to CSV (GitHub Actions will commit this file)
        output.to_csv("weekly_predictions.csv", index=False)
        print("Predictions successfully updated and saved.")
    else:
        print("No upcoming games found to predict.")

if __name__ == "__main__":
    main()
