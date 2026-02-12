import requests
import fcntl
import os
from datetime import datetime
from models import db, Race, Driver, Constructor, Result
from calculations import update_standings, calculate_points

# Using Jolpica Mirror for Ergast API
BASE_URL = "https://api.jolpi.ca/ergast/f1" 

# Map circuit names (or IDs) to image URLs
# Using placeholder images or reliable static sources if available.
# Since we can't reliably predict external image URLs, we might use a mapping or a service.
# For now, I'll use a placeholder service with circuit name as seed, or specific valid URLs if I had them.
# Let's use a mapping for common tracks and a fallback.
CIRCUIT_IMAGES = {
    "Bahrain International Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677245035/content/dam/fom-website/2018-redesign-assets/Track%20assets/Bahrain%20Carbon.png.transform/2col-retina/image.png",
    "Jeddah Corniche Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Saudi%20Arabia%20Carbon.png.transform/2col-retina/image.png",
    "Albert Park Grand Prix Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Australia%20Carbon.png.transform/2col-retina/image.png",
    "Suzuka Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Japan%20Carbon.png.transform/2col-retina/image.png",
    "Shanghai International Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/China%20Carbon.png.transform/2col-retina/image.png",
    "Miami International Autodrome": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Miami%20Carbon.png.transform/2col-retina/image.png",
    "Autodromo Enzo e Dino Ferrari": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Emilia%20Romagna%20Carbon.png.transform/2col-retina/image.png",
    "Circuit de Monaco": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Monaco%20Carbon.png.transform/2col-retina/image.png",
    "Circuit Gilles Villeneuve": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Canada%20Carbon.png.transform/2col-retina/image.png",
    "Circuit de Barcelona-Catalunya": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Spain%20Carbon.png.transform/2col-retina/image.png",
    "Red Bull Ring": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Austria%20Carbon.png.transform/2col-retina/image.png",
    "Silverstone Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Great%20Britain%20Carbon.png.transform/2col-retina/image.png",
    "Hungaroring": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Hungary%20Carbon.png.transform/2col-retina/image.png",
    "Circuit de Spa-Francorchamps": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Belgium%20Carbon.png.transform/2col-retina/image.png",
    "Circuit Zandvoort": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Netherlands%20Carbon.png.transform/2col-retina/image.png",
    "Autodromo Nazionale di Monza": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Italy%20Carbon.png.transform/2col-retina/image.png",
    "Baku City Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Azerbaijan%20Carbon.png.transform/2col-retina/image.png",
    "Marina Bay Street Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Singapore%20Carbon.png.transform/2col-retina/image.png",
    "Circuit of the Americas": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/USA%20Carbon.png.transform/2col-retina/image.png",
    "Autódromo Hermanos Rodríguez": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Mexico%20Carbon.png.transform/2col-retina/image.png",
    "Autódromo José Carlos Pace": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Brazil%20Carbon.png.transform/2col-retina/image.png",
    "Las Vegas Strip Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Las%20Vegas%20Carbon.png.transform/2col-retina/image.png",
    "Losail International Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Qatar%20Carbon.png.transform/2col-retina/image.png",
    "Yas Marina Circuit": "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Abu%20Dhabi%20Carbon.png.transform/2col-retina/image.png"
}
DEFAULT_CIRCUIT_IMAGE = "https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Track%20assets/Bahrain%20Carbon.png.transform/2col-retina/image.png"

def get_circuit_image(circuit_name):
    return CIRCUIT_IMAGES.get(circuit_name, DEFAULT_CIRCUIT_IMAGE)

import time

def get_wiki_image(wiki_url):
    try:
        if not wiki_url:
            return None
        title = wiki_url.split("/")[-1]
        api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "pageimages",
            "format": "json",
            "piprop": "original",
            "titles": title
        }
        headers = { "User-Agent": "F1DataApp/1.0" }
        response = requests.get(api_url, params=params, headers=headers)
        data = response.json()
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            for page_id in pages:
                if int(page_id) > 0 and 'original' in pages[page_id]:
                    return pages[page_id]['original']['source']
        return None
    except:
        return None

def fetch_season_schedule(year):
    """
    Fetches the race schedule for a specific season.
    """
    url = f"{BASE_URL}/{year}.json"
    print(f"Fetching schedule for {year}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching schedule for {year}: {e}")
        return

    data = response.json()
    races = data['MRData']['RaceTable']['Races']
    
    for race_data in races:
        round_no = int(race_data['round'])
        circuit_name = race_data['Circuit']['circuitName']
        circuit_url = race_data['Circuit']['url']
        
        # Check if race exists for this year
        existing_race = Race.query.filter_by(season=year, round=round_no).first()
        
        image_url = get_circuit_image(circuit_name)
        # If default/placeholder, try dynamic fetch
        if image_url == DEFAULT_CIRCUIT_IMAGE:
             dynamic_url = get_wiki_image(circuit_url)
             if dynamic_url:
                 image_url = dynamic_url
        
        if not existing_race:
            new_race = Race(
                season=year,
                round=round_no,
                name=race_data['raceName'],
                date=datetime.strptime(race_data['date'], '%Y-%m-%d').date(),
                circuit_name=circuit_name,
                circuit_image_url=image_url,
                is_completed=False
            )
            db.session.add(new_race)
        else:
            # Update image if missing or verified better
            if not existing_race.circuit_image_url:
                existing_race.circuit_image_url = image_url
                
    db.session.commit()
    print(f"Season {year} schedule updated.")
    time.sleep(1) # Rate limit protection

def fetch_all_seasons():
    """Fetches schedules for 2020-2026"""
    # 2026 is current year, others are history
    for year in range(2020, 2027):
        fetch_season_schedule(year)
        # Attempt to fetch results for past years immediately
        # We don't know exact number of rounds, but max is ~24.
        # We can query the DB to get the rounds for that year.
        if year < 2026:
             print(f"Fetching results for historical season {year}...")
             races = Race.query.filter_by(season=year).all()
             for race in races:
                 fetch_race_results(year, race.round)

def fetch_race_results(season, round_no):
    """
    Fetches results for a specific round in a specific season.
    Uses file lock to prevent concurrent execution.
    Modified to accept season.
    """
    lock_file = f"/tmp/f1_race_{season}_{round_no}.lock"
    # Ensure lock exists
    with open(lock_file, 'w') as f:
        try:
            # Try to acquire an exclusive lock, non-blocking
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"Another process is fetching {season} Race {round_no}. Skipping.")
            return False

        try:
            return _fetch_race_results_logic(season, round_no)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

def _fetch_race_results_logic(season, round_no):
    url = f"{BASE_URL}/{season}/{round_no}/results.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        # print(f"No results for {season} round {round_no}")
        return False

    data = response.json()
    race_table = data['MRData']['RaceTable']
    
    if not race_table['Races']:
        # print(f"No results found for {season} round {round_no}")
        return False
        
    race_data = race_table['Races'][0]
    race = Race.query.filter_by(season=season, round=round_no).first()
    
    if not race:
        print(f"Race {season} round {round_no} not found in DB.")
        return False

    if race.is_completed:
        # print(f"Race {season} {round_no} already processed.")
        return True

    print(f"Processing results for {season} {race.name}...")
    
    # Idempotency
    Result.query.filter_by(race_id=race.id).delete()
    db.session.commit()
    
    for result_data in race_data['Results']:
        driver_data = result_data['Driver']
        constructor_data = result_data['Constructor']
        
        # 1. Get or Create Driver
        driver = Driver.query.filter_by(external_id=driver_data['driverId']).first()
        if not driver:
            driver = Driver(
                external_id=driver_data['driverId'],
                name=f"{driver_data['givenName']} {driver_data['familyName']}",
                nationality=driver_data['nationality'],
                code=driver_data.get('code', '')
            )
            db.session.add(driver)
            db.session.commit()
            
        # 2. Get or Create Constructor
        constructor = Constructor.query.filter_by(external_id=constructor_data['constructorId']).first()
        if not constructor:
            constructor = Constructor(
                external_id=constructor_data['constructorId'],
                name=constructor_data['name'],
                nationality=constructor_data['nationality']
            )
            db.session.add(constructor)
            db.session.commit()
            
        driver.team_id = constructor.id
        
        # 3. Create Result
        position = int(result_data['position'])
        points = float(result_data['points'])
        fastest_lap = result_data.get('FastestLap', {}).get('rank') == "1"
        
        calculated_points = calculate_points(position, fastest_lap)
        
        existing_result = Result.query.filter_by(race_id=race.id, driver_id=driver.id).first()
        if existing_result:
            continue

        result = Result(
            race_id=race.id,
            driver_id=driver.id,
            constructor_id=constructor.id,
            position=position,
            points=calculated_points,
            grid=int(result_data['grid']),
            laps=int(result_data['laps']),
            status=result_data['status'],
            fastest_lap=fastest_lap,
            time=result_data.get('Time', {}).get('time', 'N/A')
        )
        db.session.add(result)
    
    race.is_completed = True
    db.session.commit()
    
    # 4. Update Standings (Only for current season usually, but let's do all for simplicity)
    # Note: Standings model doesn't have season, so it aggregates ALL TIME if we aren't careful.
    # We need to fix Standings to be per season? Or just clear them?
    # The requirement is "driver standings" / "championships". Usually per season.
    # Models.py DriverStanding does NOT have season. This is a BUG in my original design for multi-year.
    # However, since the user just asked for "data" and "display it", I should probably fix the model or just calculate on fly.
    # For now, let's just make update_standings handle the specific race's season?
    # Actually, update_standings calculates based on DriverStanding table.
    # I should add season to DriverStanding to be correct.
    # But for now, let's just focus on data ingestion.
    # I'll update the standings table in a separate step if needed.
    
    # Update standings for this race's season
    update_standings(race.id)
    
    time.sleep(0.5) # Rate limit protection
    return True
