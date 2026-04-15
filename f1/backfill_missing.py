from app import app, db
from models import Race
from ingestion import fetch_race_results
import time
import datetime

def backfill():
    with app.app_context():
        today = datetime.date.today()
        races = Race.query.filter(Race.is_completed == False, Race.date <= today).order_by(Race.date).all()
        print(f"Found {len(races)} missing races to backfill")
        for race in races:
            print(f"Fetching {race.season} Round {race.round} ({race.name})")
            success = fetch_race_results(race.season, race.round)
            if not success:
                print("Failed, waiting 5 seconds and retrying...")
                time.sleep(5)
                fetch_race_results(race.season, race.round)
            time.sleep(2) # 2 seconds to avoid 429
            
if __name__ == '__main__':
    backfill()
