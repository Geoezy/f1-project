from app import app
from models import Driver, Constructor

with app.app_context():
    print("DRIVERS:")
    for d in Driver.query.all():
        print(f"ID: {d.id}, Name: {d.name}, URL: {d.image_url}")
    print("\nTEAMS:")
    for c in Constructor.query.all():
        print(f"ID: {c.id}, Name: {c.name}, URL: {c.car_image_url}")
