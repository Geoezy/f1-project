from app import app
from models import Race, Driver

with app.app_context():
    print("Checking Circuit Images:")
    races = Race.query.limit(5).all()
    for r in races:
        print(f"{r.name}: {r.circuit_image_url}")
        
    print("\nChecking Driver Images:")
    drivers = Driver.query.limit(5).all()
    for d in drivers:
        print(f"{d.name}: {d.image_url}")
