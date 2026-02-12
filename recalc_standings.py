from app import app
from models import Race, db, DriverStanding, ConstructorStanding
from calculations import update_standings

def recalc_all():
    print("Recalculating standings for all seasons (2020-2026)...")
    
    # We can iterate through all races and call update_standings.
    # However, update_standings(race_id) recalculates the WHOLE season for that race.
    # So we only need to call it ONCE per season.
    # Ideally, we call it for the LAST race of each season.
    
    for year in range(2020, 2027):
        print(f"Processing Season {year}...")
        # Get one race from this season (any race will trigger the logic for the whole season 
        # based on my previous view of calculations.py, let's verify that logic though.
        # Viewed logic: 
        # season = race.season
        # season_races = Race.query.filter_by(season=season).all()
        # ... logic aggregates all results for those races.
        # So yes, calling it for ONE race in the season is enough.
        
        race = Race.query.filter_by(season=year).first()
        if race:
            update_standings(race.id)
            print(f"  Updated Standings for {year}")
        else:
            print(f"  No races found for {year}")
            
    print("Recalculation Complete.")

if __name__ == "__main__":
    with app.app_context():
        # Clear existing standings first to be sure? 
        # update_standings does a delete, so it should be fine.
        recalc_all()
