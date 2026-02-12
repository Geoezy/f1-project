from app import app
from ingestion import fetch_race_results

with app.app_context():
    print("Fetching results for Round 1...")
    success = fetch_race_results(1)
    if success:
        print("Success!")
    else:
        print("Failed.")
