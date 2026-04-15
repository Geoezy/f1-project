from app import app
from models import Driver

with app.app_context():
    max_d = Driver.query.filter(Driver.name.like('%Max Verstappen%')).all()
    for d in max_d:
        print(f"ID: {d.id}, Name: {d.name}, URL: {d.image_url}")
