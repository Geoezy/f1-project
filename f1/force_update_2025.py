
from app import app, db
from models import Race, Driver, DriverStanding, Constructor
# from ingestion import get_wiki_image, DEFAULT_CIRCUIT_IMAGE
import time

def force_update_images():
    with app.app_context():
        print("--- Force Updating Race Images ---")
        # Get all races
        races = Race.query.all()
        count = 0
        total = len(races)
        
        for r in races:
            # Check if image is broken (media.formula1.com) or default
            if not r.circuit_image_url or "media.formula1.com" in r.circuit_image_url or r.circuit_image_url == DEFAULT_CIRCUIT_IMAGE:
                print(f"[{count}/{total}] Updating image for {r.name} ({r.season})...")
                
                # Construct wiki url if not stored (we don't store it in DB, need to reconstruct or use stored one if I added it?)
                # Actually ingestion uses 'url' from API which is usually wikipedia.
                # But we don't store that URL in Race model! 
                # We only have circuit_name.
                # We can try to guess the wiki url: f"https://en.wikipedia.org/wiki/{r.season}_{r.name.replace(' ', '_')}"
                
                wiki_url = f"https://en.wikipedia.org/wiki/{r.season}_{r.name.replace(' ', '_')}"
                
                # Special case overrides if needed, but let's try generic first
                img = get_wiki_image(wiki_url)
                
                if img:
                    r.circuit_image_url = img
                    print(f"  -> Found: {img}")
                else:
                    print("  -> No image found.")
                
                count += 1
                if count % 10 == 0:
                    db.session.commit()
                    print("Committed batch.")
                
        db.session.commit()
        print("Image update complete.")

def update_2025_roster():
    with app.app_context():
        print("\n--- Updating 2025 Roster & Standings ---")
        
        # 1. Define 2025 Grid (Top teams)
        # Ideally we fetch this, but for "force update" we will hardcode key transfers to ensure they appear
        
        transfers = [
            # Name, TeamName
            ("Lewis Hamilton", "Ferrari"),
            ("Carlos Sainz", "Williams"),
            ("Nico Hülkenberg", "Kick Sauber"),
            ("Esteban Ocon", "Haas F1 Team"),
            ("Oliver Bearman", "Haas F1 Team"),
            ("Kimi Antonelli", "Mercedes"), # Assuming
            ("Jack Doohan", "Alpine"), # Assuming
            ("Gabriel Bortoleto", "Kick Sauber") # Assuming
        ]
        
        updated_count = 0
        for driver_name, team_name in transfers:
            driver = Driver.query.filter(Driver.name.ilike(f"%{driver_name}%")).first()
            team = Constructor.query.filter(Constructor.name.ilike(f"%{team_name}%")).first()
            
            if driver and team:
                # Update Driver's current team linkage
                if driver.team_id != team.id:
                    print(f"Transfer: {driver.name} -> {team.name}")
                    driver.team_id = team.id
                    updated_count += 1
        
        db.session.commit()
        
        # 2. Seed Standings for 2025
        # Ensure ALL active drivers have a DriverStanding entry for 2025, even if 0 points
        
        # Get all drivers attached to a team (implies active)
        active_drivers = Driver.query.filter(Driver.team_id.isnot(None)).all()
        
        for d in active_drivers:
            # Check if standing exists
            standing = DriverStanding.query.filter_by(season=2025, driver_id=d.id).first()
            if not standing:
                print(f"Seeding 2025 Standing for {d.name} ({d.team.name if d.team else 'No Team'})")
                ns = DriverStanding(
                    season=2025, 
                    driver_id=d.id, 
                    points=0, 
                    wins=0, 
                    position=99 # Sort order default
                )
                db.session.add(ns)
        
        db.session.commit()
        print("2025 Roster update complete.")

if __name__ == "__main__":
    # force_update_images()
    update_2025_roster()
