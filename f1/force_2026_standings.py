from app import app
from models import Driver, Constructor, DriverStanding, ConstructorStanding, db

def seed_2026_standings():
    with app.app_context():
        # Clear any existing 2026 standings
        DriverStanding.query.filter_by(season=2026).delete()
        ConstructorStanding.query.filter_by(season=2026).delete()
        
        # Get 2025 standings to use as order
        d_2025 = DriverStanding.query.filter_by(season=2025).order_by(DriverStanding.position).all()
        
        # if 2025 is missing for some reason, just grab drivers
        if not d_2025:
            drivers = Driver.query.all()
            for i, d in enumerate(drivers):
                ds = DriverStanding(season=2026, driver_id=d.id, points=0, position=i+1, wins=0)
                db.session.add(ds)
        else:
            # Map 2025 drivers
            used_driver_ids = set()
            new_pos = 1
            for s in d_2025:
                # Driver might not be on grid for 2026 (e.g., Magnussen), but let's just carry them over 
                # or we can manually filter out retired? It's fine to carry them over for now or use the full set
                ds = DriverStanding(season=2026, driver_id=s.driver_id, points=0, position=new_pos, wins=0)
                db.session.add(ds)
                used_driver_ids.add(s.driver_id)
                new_pos += 1
                
            # Add any drivers not in 2025 standings (like Rookies: Antonelli, Bearman, Doohan, Bortoleto, etc)
            all_drivers = Driver.query.all()
            for d in all_drivers:
                if d.id not in used_driver_ids:
                    ds = DriverStanding(season=2026, driver_id=d.id, points=0, position=new_pos, wins=0)
                    db.session.add(ds)
                    new_pos += 1
                    
        # Same for constructors
        c_2025 = ConstructorStanding.query.filter_by(season=2025).order_by(ConstructorStanding.position).all()
        if not c_2025:
            teams = Constructor.query.all()
            for i, t in enumerate(teams):
                cs = ConstructorStanding(season=2026, constructor_id=t.id, points=0, position=i+1, wins=0)
                db.session.add(cs)
        else:
            used_team_ids = set()
            new_pos = 1
            for s in c_2025:
                cs = ConstructorStanding(season=2026, constructor_id=s.constructor_id, points=0, position=new_pos, wins=0)
                db.session.add(cs)
                used_team_ids.add(s.constructor_id)
                new_pos += 1
                
            all_teams = Constructor.query.all()
            for t in all_teams:
                if t.id not in used_team_ids:
                    cs = ConstructorStanding(season=2026, constructor_id=t.id, points=0, position=new_pos, wins=0)
                    db.session.add(cs)
                    new_pos += 1
                    
        db.session.commit()
        print("2026 Standings Seeded (Ordered by 2025 form)")

if __name__ == "__main__":
    seed_2026_standings()
