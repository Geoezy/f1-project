import json
import os
import requests
from app import app, db
from models import Race

# Base URL for the images
BASE_URL = "https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/white"

def get_latest_layout(circuit_data):
    """Finds the layout used in 2026 or the most recent one."""
    latest_layout = None
    latest_year = -1
    
    for layout in circuit_data.get('layouts', []):
        seasons = layout['seasons']
        # Parse seasons string "2021-2026, 2000" etc
        ranges = seasons.split(',')
        for r in ranges:
            if '-' in r:
                start, end = r.split('-')
                if int(end) >= 2026:
                    return layout['layoutId'] # Active now
                if int(end) > latest_year:
                    latest_year = int(end)
                    latest_layout = layout['layoutId']
            else:
                year = int(r)
                if year == 2026:
                    return layout['layoutId']
                if year > latest_year:
                    latest_year = year
                    latest_layout = layout['layoutId']
                    
    return latest_layout

def fetch_stable_images():
    with open('circuits.json', 'r') as f:
        circuits_data = json.load(f)
        
    # Map name -> data
    circuit_map = {c['name']: c for c in circuits_data}
    
    # Manual Name Fixes (DB Name -> JSON Name)
    NAME_MAPPING = {
        "Autodromo Nazionale di Monza": "Autodromo Nazionale Monza",
        "Autódromo Internacional do Algarve": "Algarve International Circuit",
        "Autodromo Internazionale del Mugello": "Autodromo Internazionale del Mugello", # Match
        "Circuit of the Americas": "Circuit of the Americas", # Match
        "Red Bull Ring": "Red Bull Ring", # Match
        "Istanbul Park": "Istanbul Park", # Match
        "Jeddah Corniche Circuit": "Jeddah Corniche Circuit", # Match
        "Las Vegas Strip Street Circuit": "Las Vegas Street Circuit",
        "Losail International Circuit": "Lusail International Circuit",
        "Marina Bay Street Circuit": "Marina Bay Street Circuit", 
        "Miami International Autodrome": "Miami International Autodrome",
        "Shanghai International Circuit": "Shanghai International Circuit",
        "Suzuka Circuit": "Suzuka Circuit",
        "Yas Marina Circuit": "Yas Marina Circuit",
        "Circuit Park Zandvoort": "Circuit Park Zandvoort",
        "Hungaroring": "Hungaroring",
        "Circuit de Spa-Francorchamps": "Circuit de Spa-Francorchamps",
        "Circuit Gilles Villeneuve": "Circuit Gilles Villeneuve",
        "Circuit de Monaco": "Circuit de Monaco",
        "Circuit de Barcelona-Catalunya": "Circuit de Barcelona-Catalunya",
        "Albert Park Grand Prix Circuit": "Melbourne Grand Prix Circuit",
        "Autódromo Hermanos Rodríguez": "Autódromo Hermanos Rodríguez",
        "Autódromo José Carlos Pace": "Autódromo José Carlos Pace",
        "Baku City Circuit": "Baku City Circuit",
        "Bahrain International Circuit": "Bahrain International Circuit",
        "Imola": "Autodromo Internazionale Enzo e Dino Ferrari",
        "Autodromo Enzo e Dino Ferrari": "Autodromo Internazionale Enzo e Dino Ferrari",
        "Nürburgring": "Nürburgring",
        "Sochi Autodrom": "Sochi Autodrom", 
        "Madring": "Circuito de Madring" # Fictional?
    }

    with app.app_context():
        races = Race.query.all()
        unique_circuits = sorted(list(set(r.circuit_name.strip() for r in races))) # Strip in DB names
        
        print(f"Processing {len(unique_circuits)} circuits...")
        
        for db_name in unique_circuits:
            print(f"Checking '{db_name}'...")
            
            # 1. Direct key usage from manual map
            target_json_name = NAME_MAPPING.get(db_name, db_name)
            
            # 2. Find in JSON Map
            c_data = circuit_map.get(target_json_name)
            
            # 3. Fuzzy search if still not found
            if not c_data:
                for name, data in circuit_map.items():
                    # Check exact match stripped
                    if name.strip() == target_json_name.strip():
                        c_data = data
                        break
                    # Check contains
                    if target_json_name in name or name in target_json_name:
                         c_data = data
                         # keep searching for exact match if possible, but store this
                         break
            
            if c_data:
                print(f"  Matched to JSON: {c_data['name']}")
                layout_id = get_latest_layout(c_data)
                
                # Special overrides if 2026 layout missing or specific preference
                if db_name == "Jeddah Corniche Circuit": layout_id = "jeddah-1"
                if db_name == "Las Vegas Strip Street Circuit": layout_id = "las-vegas-1"
                if db_name == "Miami International Autodrome": layout_id = "miami-1"
                if db_name == "Losail International Circuit": layout_id = "lusail-1"
                
                if layout_id:
                    url = f"{BASE_URL}/{layout_id}.svg"
                    filename = f"{layout_id}.svg"
                    local_path = f"static/img/circuits/{filename}"
                    web_path = f"/static/img/circuits/{filename}"
                    
                    if not os.path.exists(local_path):
                        print(f"  Downloading {url}...")
                        try:
                            r = requests.get(url)
                            if r.status_code == 200:
                                with open(local_path, 'wb') as f:
                                    f.write(r.content)
                            else:
                                print(f"  Failed to download: {r.status_code}")
                                continue
                        except Exception as e:
                            print(f"  Download error: {e}")
                            continue
                    else:
                        print("  File already exists.")

                    # Update DB (using the original db_name with wildcards if needed, or exact)
                    # We iterate unique names so filter_by should work
                    Race.query.filter(Race.circuit_name == db_name).update({Race.circuit_image_url: web_path}, synchronize_session=False)
                    print(f"  Updated DB to {web_path}")
                else:
                    print("  No layout found.")
            else:
                print("  Not found in JSON map.")
                
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    fetch_stable_images()
