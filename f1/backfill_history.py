from app import app, db
from ingestion import fetch_season_schedule, fetch_race_results
from models import Race
import time

def backfill_history():
    start_year = 2020
    end_year = 2025 # 2026 is handled by main app
    
    print(f"Starting backfill from {start_year} to {end_year}...")
    
    with app.app_context():
        # 1. Fetch Schedules
        for year in range(start_year, end_year + 1):
            fetch_season_schedule(year)
            time.sleep(1) # Be nice to API
            
        # 2. Fetch Results
        # Iterate through all races in DB that are not completed (or just check all for those years)
        # We query by season to be efficient
        for year in range(start_year, end_year + 1):
            print(f"Fetching results for {year}...")
            races = Race.query.filter_by(season=year).all()
            for race in races:
                if not race.is_completed:
                    print(f"  Fetching {race.name}...")
                    success = fetch_race_results(year, race.round)
                    if not success:
                        print(f"  Failed/No results for {race.name}")
                    time.sleep(0.5) # Rate limit
                else:
                    # Optional: Uncomment to force refresh
                     pass
            
    print("Backfill complete.")

if __name__ == "__main__":
    backfill_history()
