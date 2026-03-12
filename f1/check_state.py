
import requests
from app import app
from models import Race, Result, DriverStanding

def check_db():
    with app.app_context():
        print("--- Database Stats ---")
        for year in range(2020, 2027):
            races = Race.query.filter_by(season=year).count()
            results = Result.query.join(Race).filter(Race.season == year).count()
            print(f"Season {year}: {races} races, {results} results")

def check_images():
    print("\n--- Image URL Check ---")
    with app.app_context():
        # Get a race that should have a new image
        race = Race.query.filter_by(season=2021, round=1).first()
        if race and race.circuit_image_url:
            url = race.circuit_image_url
            print(f"Checking Image for {race.name}: {url}")
            try:
                headers = { "User-Agent": "Mozilla/5.0" }
                response = requests.head(url, timeout=5, allow_redirects=True, headers=headers)
                print(f"Image Status: {response.status_code}")
            except Exception as e:
                print(f"Image Check Failed: {e}")
        else:
             print("No 2021 race found or no image URL.")

if __name__ == "__main__":
    check_db()
    check_images()
