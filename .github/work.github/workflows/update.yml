name: Weekly NFL Data Model Update

on:
  schedule:
    # Runs at 10:00 UTC (6:00 AM Eastern Time) every Tuesday morning
    - cron: '0 10 * * 2' 
  workflow_dispatch: # Allows you to click a button to run it manually

jobs:
  update-model:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Prediction Model
        run: |
          python update_model.py

      - name: Commit and Push Updated Data
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add weekly_predictions.csv
          git commit -m "Automated update: NFL weekly statistical odds" || echo "No changes to commit"
          git push
