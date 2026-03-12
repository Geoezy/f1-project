from app import app
from models import Driver, Constructor, DriverStanding, ConstructorStanding, db
import requests

def seed_final_2025():
    with app.app_context():
        # Clear existing 2025 mock data
        DriverStanding.query.filter_by(season=2025).delete()
        ConstructorStanding.query.filter_by(season=2025).delete()
        
        # 1. Driver Standings
        r = requests.get("https://api.jolpi.ca/ergast/f1/2025/driverStandings.json")
        if r.status_code == 200:
            data = r.json()
            standings = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if standings:
                for ds in standings[0].get("DriverStandings", []):
                    pos = int(ds.get("position"))
                    pts = float(ds.get("points"))
                    wins = int(ds.get("wins"))
                    driver_id_ext = ds.get("Driver", {}).get("driverId")
                    
                    # Try to find driver by external ID or name
                    surname = ds.get("Driver", {}).get("familyName")
                    d = Driver.query.filter(Driver.name.ilike(f"%{surname}%")).first()
                    
                    if not d:
                        print(f"Driver not found: {surname}")
                        continue
                        
                    db.session.add(DriverStanding(season=2025, driver_id=d.id, points=pts, position=pos, wins=wins))
        
        # 2. Constructor Standings
        r = requests.get("https://api.jolpi.ca/ergast/f1/2025/constructorStandings.json")
        if r.status_code == 200:
            data = r.json()
            standings = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if standings:
                for cs in standings[0].get("ConstructorStandings", []):
                    pos = int(cs.get("position"))
                    pts = float(cs.get("points"))
                    wins = int(cs.get("wins"))
                    cons_id_ext = cs.get("Constructor", {}).get("constructorId")
                    
                    name = cs.get("Constructor", {}).get("name")
                    
                    # Special mappings if needed
                    search_name = name
                    if "Sauber" in name: search_name = "Sauber"
                    elif "Haas" in name: search_name = "Haas"
                    elif "RB" in name: search_name = "RB"
                    elif "Alpine" in name: search_name = "Alpine"
                    
                    if search_name == "RB":
                        c = Constructor.query.filter(Constructor.name == "RB").first()
                    else:
                        c = Constructor.query.filter(Constructor.name.ilike(f"%{search_name}%")).first()
                        
                    if not c:
                        print(f"Constructor not found: {name}")
                        continue
                        
                    db.session.add(ConstructorStanding(season=2025, constructor_id=c.id, points=pts, position=pos, wins=wins))
                    
        db.session.commit()
        print("Final 2025 Standings Seeded from API")

if __name__ == "__main__":
    seed_final_2025()
