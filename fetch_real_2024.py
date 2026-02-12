import requests
import time
from app import app
from models import db, Race, Result, Driver, Constructor
from ingestion import calculate_points, update_standings

# Constants
API_BASE = "http://api.jolpi.ca/ergast/f1"

def get_or_create_driver(driver_data):
    driver = Driver.query.filter_by(external_id=driver_data['driverId']).first()
    if not driver:
        # Check if code exists, might be missing for some older/new drivers
        code = driver_data.get('code', driver_data['familyName'][:3].upper())
        driver = Driver(
            external_id=driver_data['driverId'],
            name=f"{driver_data['givenName']} {driver_data['familyName']}",
            nationality=driver_data['nationality'],
            code=code
        )
        db.session.add(driver)
        db.session.commit()
    return driver

def get_or_create_constructor(constructor_data):
    constructor = Constructor.query.filter_by(external_id=constructor_data['constructorId']).first()
    if not constructor:
        constructor = Constructor(
            external_id=constructor_data['constructorId'],
            name=constructor_data['name'],
            nationality=constructor_data['nationality']
        )
        db.session.add(constructor)
        db.session.commit()
    return constructor

def fetch_real_2024():
    print("Purging incorrect 2024 results...")
    # Delete all results for 2024
    races_2024 = Race.query.filter_by(season=2024).all()
    for race in races_2024:
        Result.query.filter_by(race_id=race.id).delete()
        race.is_completed = False
    db.session.commit()
    print("Purge complete.")
    
    print("Fetching REAL 2024 results from API...")
    
    # We know there are 24 rounds
    for round_no in range(1, 25):
        print(f"Fetching Round {round_no}...")
        try:
            url = f"{API_BASE}/2024/{round_no}/results.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"  Error fetching round {round_no}: {response.status_code}")
                time.sleep(1)
                continue
                
            data = response.json()
            race_table = data.get('MRData', {}).get('RaceTable', {})
            races_list = race_table.get('Races', [])
            
            if not races_list:
                print(f"  No data found for round {round_no}")
                continue
                
            race_data = races_list[0]
            race_name = race_data['raceName']
            
            # Find local race object
            race = Race.query.filter_by(season=2024, round=round_no).first()
            if not race:
                print(f"  Race not found in DB: {race_name}")
                continue
            
            # Process Results
            results = race_data.get('Results', [])
            for res_data in results:
                driver_data = res_data['Driver']
                constructor_data = res_data['Constructor']
                
                driver = get_or_create_driver(driver_data)
                constructor = get_or_create_constructor(constructor_data)
                
                # Update driver's team link if valid? 
                # Actually fix_team_history.py did a hard set, but ingestion might overwrite.
                # Let's trust the Result.constructor_id which is what matters now.
                
                position = int(res_data['position'])
                points = float(res_data['points'])
                grid = int(res_data['grid'])
                laps = int(res_data['laps'])
                status = res_data['status']
                
                # Fastest Lap
                fastest_lap_rank = res_data.get('FastestLap', {}).get('rank')
                fastest_lap = (fastest_lap_rank == "1")
                
                # Time
                time_str = res_data.get('Time', {}).get('time', status)
                
                new_result = Result(
                    race_id=race.id,
                    driver_id=driver.id,
                    constructor_id=constructor.id,
                    position=position,
                    points=points,
                    grid=grid,
                    laps=laps,
                    status=status,
                    fastest_lap=fastest_lap,
                    time=time_str
                )
                db.session.add(new_result)
            
            race.is_completed = True
            db.session.commit()
            print(f"  Imported {len(results)} results for {race_name}")
            
            # Update Standings
            update_standings(race.id)
            
            time.sleep(0.5) # Rate limit
            
        except Exception as e:
            print(f"  Exception fetching round {round_no}: {e}")
            
    print("2024 Fetch Complete.")

if __name__ == "__main__":
    with app.app_context():
        fetch_real_2024()
