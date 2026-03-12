from app import app
from ingestion import fetch_all_seasons
from models import Race, db

def populate():
    print("Starting manual population of data (2020-2026)...")
    fetch_all_seasons()
    print("Population complete.")

def check_images():
    print("Checking for missing circuit images...")
    races = Race.query.all()
    missing = set()
    for r in races:
        if not r.circuit_image_url or "placeholder" in r.circuit_image_url:
            missing.add(r.circuit_name)
    
    print(f"Missing images for: {missing}")

if __name__ == "__main__":
    with app.app_context():
        populate()
        check_images()
