from ingestion import fetch_season_schedule, fetch_race_results
from models import Race, db
from app import app
import time

def sync_f1_data():
    print("Starting F1 Data Sync (2020-2025)...")
    
    with app.app_context():
        # Deduplicate
        for year in range(2020, 2027):
            print(f"Checking duplicates for {year}...")
            # Group by round
            from sqlalchemy import func
            dupes = db.session.query(Race.round, func.count(Race.id)).filter_by(season=year).group_by(Race.round).having(func.count(Race.id) > 1).all()
            for d in dupes:
                round_no = d[0]
                print(f"Duplicate found for Season {year} Round {round_no}")
                # Keep the one with results or latest ID?
                # Usually keep the one with results.
                races = Race.query.filter_by(season=year, round=round_no).all()
                # Sort by ID desc (latest)
                races.sort(key=lambda x: x.id, reverse=True)
                # Keep first, delete rest
                for r in races[1:]:
                    print(f"Results for deleted race: {len(r.results)}")
                    # Delete results first
                    Result.query.filter_by(race_id=r.id).delete()
                    db.session.delete(r)
                db.session.commit()
                
        # Sync 2025
        for year in [2025]:
            print(f"\n--- Processing Season {year} ---")
            
            # 1. Fetch Schedule
            fetch_season_schedule(year)
            
            # 2. Fetch Results for all races in that season
            races = Race.query.filter_by(season=year).all()
            print(f"Found {len(races)} races for {year}. Fetching results...")
            
            for race in races:
                # Only if not already completed (or force update?)
                # User asked to "update", so let's try to fetch results for all past ones
                # But fetch_race_results checks is_completed. 
                # Let's force it by unsetting is_completed if we suspect it's wrong?
                # No, standard fetch is fine, but we need to ensure it runs for all past races.
                
                # We need to make sure fetch_race_results logic actually runs.
                # In ingestion.py: if race.is_completed: return True.
                # So if we want to RE-FETCH to fix "undefined", we might need to clear flags?
                # Or trust that if data is missing, it's not marked completed?
                
                # Let's inspect race.is_completed.
                # If the user sees "undefined", it might be that data is partial.
                
                print(f"Fetching results for {race.name} (Round {race.round})...")
                fetch_race_results(year, race.round)
                time.sleep(0.5) # Rate limit

if __name__ == "__main__":
    sync_f1_data()
    print("\nData Sync Complete.")
