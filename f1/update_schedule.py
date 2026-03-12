from app import app
from ingestion import fetch_season_schedule

with app.app_context():
    # Fetch historical data
    for year in range(2020, 2026):
        fetch_season_schedule(year)

