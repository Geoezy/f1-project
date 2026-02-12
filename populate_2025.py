from app import app
from ingestion import fetch_season_schedule, fetch_race_results
from models import Race, db
import time

def populate_future():
    print("Fetching 2025 and 2026 data...")
    for year in [2025, 2026]:
        try:
            fetch_season_schedule(year)
            races = Race.query.filter_by(season=year).all()
            for race in races:
                fetch_race_results(year, race.round)
            time.sleep(2)
        except Exception as e:
            print(f"Error fetching {year}: {e}")

if __name__ == "__main__":
    with app.app_context():
        populate_future()
