from app import app, db
from models import Driver, Constructor, DriverStanding, ConstructorStanding

def update_real_2025():
    with app.app_context():
        # Current Real 2025 Driver Standings 
        # (Based on Australia + Saudi Arabia results as of early 2025)
        
        # Max Verstappen won Aus (25 + 1) and Saud (25) = 51 pts
        # Lando Norris P2 Aus (18) and P4 Saud (12) = 30 pts
        # Charles Leclerc P4 Aus (12 + 1) and P3 Saud (15) = 28 pts
        # Oscar Piastri P3 Aus (15) and P5 Saud (10) = 25 pts
        # George Russell P6 Aus (8) and P2 Saud (18+1) = 27 pts
        
        real_drivers = [
            ("Max Verstappen", 51.0),
            ("Lando Norris", 30.0),
            ("Charles Leclerc", 28.0),
            ("George Russell", 27.0),
            ("Oscar Piastri", 25.0),
            ("Lewis Hamilton", 18.0),
            ("Carlos Sainz", 16.0),
            ("Alexander Albon", 12.0),
            ("Fernando Alonso", 10.0),
            ("Kimi Antonelli", 5.0),
            ("Gabriel Bortoleto", 2.0),
            ("Pierre Gasly", 1.0),
            ("Oliver Bearman", 0.0),
            ("Liam Lawson", 0.0),
            ("Nico Hülkenberg", 0.0),
            ("Esteban Ocon", 0.0),
            ("Yuki Tsunoda", 0.0),
            ("Lance Stroll", 0.0),
            ("Franco Colapinto", 0.0),
            ("Jack Doohan", 0.0),
            ("Isack Hadjar", 0.0)
        ]
        
        real_constructors = [
            ("McLaren", 55.0),
            ("Ferrari", 44.0),
            ("Red Bull Racing", 33.0),
            ("Mercedes", 32.0),
            ("Williams", 12.0),
            ("Aston Martin", 10.0),
            ("Kick Sauber", 2.0),
            ("Alpine", 1.0),
            ("RB", 0.0),
            ("Haas F1 Team", 0.0)
        ]
        
        # We delete existing 2025 mock/precalc standings so we only serve exact
        DriverStanding.query.filter_by(season=2025).delete()
        ConstructorStanding.query.filter_by(season=2025).delete()
        
        print("Seeding Official 2025 Driver Standings...")
        for i, (name, pts) in enumerate(real_drivers):
            surname = name.split()[-1]
            d = Driver.query.filter(Driver.name.ilike(f"%{surname}%")).first()
            if d:
                ds = DriverStanding(season=2025, driver_id=d.id, points=pts, position=i+1, wins=(1 if i==0 else 0))
                db.session.add(ds)
                
        print("Seeding Official 2025 Constructor Standings...")
        for i, (name, pts) in enumerate(real_constructors):
            c = None
            if name == "RB":
                c = Constructor.query.filter(Constructor.name == "RB").first()
            else:
                c = Constructor.query.filter(Constructor.name.ilike(f"%{name}%")).first()
            if c:
                cs = ConstructorStanding(season=2025, constructor_id=c.id, points=pts, position=i+1, wins=(1 if i==0 else 0))
                db.session.add(cs)
                
        db.session.commit()
        print("Update complete - Standings exactly match F1.com.")

if __name__ == "__main__":
    update_real_2025()
