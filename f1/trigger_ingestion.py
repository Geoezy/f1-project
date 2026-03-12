
from app import app
from ingestion import fetch_all_seasons

if __name__ == "__main__":
    with app.app_context():
        print("Starting full data ingestion...")
        fetch_all_seasons()
        print("Ingestion complete.")
