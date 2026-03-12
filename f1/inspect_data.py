
from app import app
from models import Race, Result, Driver, Constructor

def inspect_2025():
    with app.app_context():
        print("--- 2025 Roster Check ---")
        # Check key moves
        drivers_to_check = ["Lewis Hamilton", "Carlos Sainz", "Valtteri Bottas", "Nico Hülkenberg"]
        
        for name in drivers_to_check:
            driver = Driver.query.filter(Driver.name.ilike(f"%{name}%")).first()
            if driver:
                # Check team in Driver table
                team_name = driver.team.name if driver.team else "None"
                print(f"Driver: {driver.name} | Team (DB): {team_name}")
                
                # Check results in 2025
                results = Result.query.join(Race).filter(Race.season == 2025, Result.driver_id == driver.id).all()
                if results:
                    last_result = results[-1]
                    r_team = Constructor.query.get(last_result.constructor_id).name
                    print(f"  -> Last 2025 Result Team: {r_team}")
                else:
                    print(f"  -> No 2025 Results")
            else:
                print(f"Driver {name} not found.")

        print("\n--- Image Check ---")
        races = Race.query.filter_by(season=2025).limit(5).all()
        for r in races:
            print(f"Race: {r.name} | Image: {r.circuit_image_url}")

if __name__ == "__main__":
    inspect_2025()
