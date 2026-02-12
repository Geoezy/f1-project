from app import app
from models import db, Race, Result

with app.app_context():
    for year in range(2020, 2027):
        race_count = Race.query.filter_by(season=year).count()
        result_count = Race.query.join(Result).filter(Race.season == year).count()
        print(f"Season {year}: {race_count} races, {result_count} races with results")
