
from app import app
from models import Driver, DriverStanding, Race

def verify_updates():
    with app.app_context():
        print("--- Verifying Images ---")
        # Check a few key races
        races = Race.query.filter(Race.season == 2025).limit(5).all()
        for r in races:
            print(f"2025 {r.name}: {r.circuit_image_url}")

        print("\n--- Verifying 2025 Roster ---")
        # Check Hamilton
        ham = Driver.query.filter(Driver.name.ilike("%Hamilton%")).first()
        if ham:
            print(f"Hamilton Team: {ham.team.name if ham.team else 'None'}")
            # Check standing
            standing = DriverStanding.query.filter_by(season=2025, driver_id=ham.id).first()
            if standing:
                print(f"Hamilton 2025 Standing: {standing.points} pts, Pos {standing.position}")
            else:
                print("Hamilton 2025 Standing: MISSING")
                
        # Check Sainz
        sainz = Driver.query.filter(Driver.name.ilike("%Sainz%")).first()
        if sainz:
            print(f"Sainz Team: {sainz.team.name if sainz.team else 'None'}")

if __name__ == "__main__":
    verify_updates()
