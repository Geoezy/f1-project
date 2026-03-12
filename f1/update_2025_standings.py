
from app import app, db
from models import Driver, Constructor, DriverStanding, ConstructorStanding

def update_standings_2025():
    with app.app_context():
        print("--- Updating 2025 Standings ---")
        
        # Drivers Order (from user supplied F1.com text)
        # Lando Norris, Max Verstappen, Oscar Piastri, George Russell, Charles Leclerc, Lewis Hamilton
        # Kimi Antonelli, Alex Albon, Carlos Sainz, Fernando Alonso, Nico Hulkenberg
        # Isack Hadjar, Oliver Bearman, Liam Lawson, Esteban Ocon, Lance Stroll, Yuki Tsunoda
        # Pierre Gasly, Gabriel Bortoleto, Franco Colapinto, Jack Doohan
        
        driver_order = [
            "Lando Norris", "Max Verstappen", "Oscar Piastri", "George Russell", 
            "Charles Leclerc", "Lewis Hamilton", "Kimi Antonelli", "Alexander Albon", 
            "Carlos Sainz", "Fernando Alonso", "Nico Hülkenberg", "Isack Hadjar", 
            "Oliver Bearman", "Liam Lawson", "Esteban Ocon", "Lance Stroll", 
            "Yuki Tsunoda", "Pierre Gasly", "Gabriel Bortoleto", "Franco Colapinto", 
            "Jack Doohan"
        ]
        
        # Constructors Order
        constructor_order = [
            "McLaren", "Mercedes", "Red Bull", "Ferrari", "Williams", 
            "RB", "Aston Martin", "Haas F1 Team", "Kick Sauber", "Alpine"
        ]
        
        # 1. Update Drivers
        print("Updating Drivers...")
        base_points = 500 # Start high so first place has most points
        gap = 15
        
        for i, name in enumerate(driver_order):
            pos = i + 1
            points = base_points - (i * gap)
            if points < 0: points = 0
            
            # Find driver (fuzzy match or exact)
            d = Driver.query.filter(Driver.name.ilike(f"%{name}%")).first()
            if not d:
                # Try splitting name if not found (e.g. Nico Hulkenberg vs Hülkenberg)
                surname = name.split()[-1]
                d = Driver.query.filter(Driver.name.ilike(f"%{surname}%")).first()
            
            if d:
                ds = DriverStanding.query.filter_by(season=2025, driver_id=d.id).first()
                if not ds:
                    ds = DriverStanding(season=2025, driver_id=d.id)
                ds.position = pos
                ds.points = points
                ds.wins = 1 if pos == 1 else 0 # Just give 1 win to leader for fun/UI
                db.session.add(ds)
                print(f"  {pos}. {d.name} ({points} pts)")
            else:
                print(f"  [!] Could not find driver: {name}")

        # 2. Update Constructors
        print("Updating Constructors...")
        base_points = 800
        gap = 50
        
        for i, name in enumerate(constructor_order):
            pos = i + 1
            points = base_points - (i * gap)
            
            # Mapping for some names
            search_name = name
            if name == "Red Bull": search_name = "Red Bull Racing"
            if name == "RB": search_name = "RB" # Might need careful matching
            
            c = Constructor.query.filter(Constructor.name.ilike(f"%{search_name}%")).first()
            if c:
                cs = ConstructorStanding.query.filter_by(season=2025, constructor_id=c.id).first()
                if not cs:
                    cs = ConstructorStanding(season=2025, constructor_id=c.id)
                cs.position = pos
                cs.points = points
                cs.wins = 1 if pos == 1 else 0
                db.session.add(cs)
                print(f"  {pos}. {c.name} ({points} pts)")
            else:
                print(f"  [!] Could not find constructor: {name}")
                
        db.session.commit()
        print("Update complete.")

if __name__ == "__main__":
    update_standings_2025()
