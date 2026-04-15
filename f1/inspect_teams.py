from app import app
from models import Constructor

with app.app_context():
    teams = Constructor.query.all()
    print("TEAMS IN DATABASE:")
    for t in teams:
        print(f"ID: {t.id}, Name: {t.name}, Base: {t.base}, Sponsors: {t.sponsors}, Image: {t.car_image_url}")
