import requests
import fcntl
import os
import datetime
from extensions import db
from models import Race, Result, Driver, Constructor, Result
from calculations import update_standings, calculate_points

# Using Jolpica Mirror for Ergast API
BASE_URL = "https://api.jolpi.ca/ergast/f1" 

# Circuit Image Mapping (Curated)
# Using generic layout images or specific URLs
CIRCUIT_IMG_MAP = {
    "albert_park": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Australia.png.transform/2col/image.png",
    "shanghai": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/China.png.transform/2col/image.png",
    "suzuka": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Japan.png.transform/2col/image.png",
    "bahrain": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Bahrain.png.transform/2col/image.png",
    "jeddah": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Saudi%20Arabia.png.transform/2col/image.png",
    "miami": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Miami.png.transform/2col/image.png",
    "imola": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Emilia%20Romagna.png.transform/2col/image.png",
    "monaco": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Monaco.png.transform/2col/image.png",
    "catalunya": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Spain.png.transform/2col/image.png",
    "villeneuve": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Canada.png.transform/2col/image.png",
    "red_bull_ring": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Austria.png.transform/2col/image.png",
    "silverstone": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Great%20Britain.png.transform/2col/image.png",
    "hungaroring": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Hungary.png.transform/2col/image.png",
    "spa": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Belgium.png.transform/2col/image.png",
    "zandvoort": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Netherlands.png.transform/2col/image.png",
    "monza": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Italy.png.transform/2col/image.png",
    "baku": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Azerbaijan.png.transform/2col/image.png",
    "marina_bay": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Singapore.png.transform/2col/image.png",
    "americas": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/United%20States.png.transform/2col/image.png",
    "rodriguez": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Mexico.png.transform/2col/image.png",
    "interlagos": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Brazil.png.transform/2col/image.png",
    "vegas": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Las%20Vegas.png.transform/2col/image.png",
    "losail": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Qatar.png.transform/2col/image.png",
    "yas_marina": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/Abu%20Dhabi.png.transform/2col/image.png"
}

def fetch_season_schedule(season=2025):
    print(f"Fetching schedule for {season}...")
    url = f"{BASE_URL}/{season}.json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        races = data['MRData']['RaceTable']['Races']
        
        # NOTE: db.session handled by caller or context
        for r in races:
            race_id = int(r['round']) 
            existing_race = Race.query.filter_by(season=season, round=race_id).first()
            
            circuit = r['Circuit']
            circuit_id = circuit['circuitId']
            
            # Match image
            img_url = None
            for k, v in CIRCUIT_IMG_MAP.items():
                if k in circuit_id:
                    img_url = v
                    break
            
            if not existing_race:
                new_race = Race(
                    season=season,
                    round=race_id,
                    name=r['raceName'],
                    date=datetime.datetime.strptime(r['date'], '%Y-%m-%d').date(),
                    circuit_name=circuit['circuitName'],
                    circuit_image_url=img_url,
                    is_completed=False 
                )
                db.session.add(new_race)
            else:
                existing_race.circuit_image_url = img_url
                
        db.session.commit()
        print(f"Season {season} schedule ingested.")
            
    except Exception as e:
        print(f"Error fetching schedule: {e}")

def get_or_create_driver(driver_data):
    driver = Driver.query.filter_by(external_id=driver_data['driverId']).first()
    if not driver:
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

# Reuse existing result fetcher (simplified)
def fetch_race_results(season, round_no):
    print(f"Fetching Round {round_no} for {season}...")
    try:
        url = f"{BASE_URL}/{season}/{round_no}/results.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"  Error fetching round {round_no}: {response.status_code}")
            return False
            
        data = response.json()
        race_table = data.get('MRData', {}).get('RaceTable', {})
        races_list = race_table.get('Races', [])
        
        if not races_list:
            print(f"  No data found for {season} round {round_no}")
            return False
            
        race_data = races_list[0]
        race_name = race_data['raceName']
        
        race = Race.query.filter_by(season=season, round=round_no).first()
        if not race:
            print(f"  Race not found in DB: {race_name}")
            return False
        
        # Clear existing if any
        Result.query.filter_by(race_id=race.id).delete()
        
        # Check sprint points
        sprint_points = {}
        try:
            sprint_url = f"{BASE_URL}/{season}/{round_no}/sprint.json"
            sprint_resp = requests.get(sprint_url, timeout=5)
            if sprint_resp.status_code == 200:
                s_data = sprint_resp.json()
                s_races = s_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                if s_races:
                    for sr in s_races[0].get('SprintResults', []):
                        sprint_points[sr['Driver']['driverId']] = float(sr['points'])
        except Exception as e:
            print(f"  Sprint fetch error: {e}")
            
        results = race_data.get('Results', [])
        for res_data in results:
            driver_data = res_data['Driver']
            constructor_data = res_data['Constructor']
            
            driver = get_or_create_driver(driver_data)
            constructor = get_or_create_constructor(constructor_data)
            
            position = int(res_data['position'])
            points = float(res_data['points'])
            grid = int(res_data['grid'])
            laps = int(res_data['laps'])
            status = res_data['status']
            
            fastest_lap_rank = res_data.get('FastestLap', {}).get('rank')
            fastest_lap = (fastest_lap_rank == "1")
            
            time_str = res_data.get('Time', {}).get('time', status)
            
            # Combine Sprint points with Main Race points
            sp_pts = sprint_points.get(driver_data['driverId'], 0.0)
            
            new_result = Result(
                race_id=race.id,
                driver_id=driver.id,
                constructor_id=constructor.id,
                position=position,
                points=points + sp_pts,
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
        
        update_standings(race.id)
        return True
    except Exception as e:
        print(f"  Exception fetching round {round_no}: {e}")
        return False
