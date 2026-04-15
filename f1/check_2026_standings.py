from app import app
from models import ConstructorStanding, Constructor

with app.app_context():
    standings = ConstructorStanding.query.filter_by(season=2026).all()
    print("CONSTRUCTOR STANDINGS 2026:")
    for s in standings:
        print(f"Pos: {s.position}, Team Name: {s.constructor.name}, Team ID: {s.constructor_id}")
