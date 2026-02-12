from app import app
from models import Race, Result

with app.app_context():
    races_2025 = Race.query.filter_by(season=2025).all()
    print(f"Total 2025 Races: {len(races_2025)}")
    
    completed_races = [r for r in races_2025 if r.is_completed]
    print(f"Completed 2025 Races: {len(completed_races)}")
    
    results_count = Result.query.join(Race).filter(Race.season == 2025).count()
    print(f"Total 2025 Results Rows: {results_count}")
