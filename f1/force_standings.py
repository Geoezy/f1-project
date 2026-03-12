from app import app, db
from models import DriverStanding, ConstructorStanding

def force_recalc_positions():
    with app.app_context():
        print("Recalculating standing positions...")
        seasons = [2020, 2021, 2022, 2023, 2024, 2025]
        
        for season in seasons:
            # Drivers
            driver_standings = DriverStanding.query.filter_by(season=season).order_by(
                DriverStanding.points.desc(), 
                DriverStanding.wins.desc()
            ).all()
            
            for i, ds in enumerate(driver_standings):
                ds.position = i + 1
                
            # Constructors
            constructor_standings = ConstructorStanding.query.filter_by(season=season).order_by(
                ConstructorStanding.points.desc(), 
                ConstructorStanding.wins.desc()
            ).all()
            
            for i, cs in enumerate(constructor_standings):
                cs.position = i + 1
                
        db.session.commit()
        print("Positions updated successfully!")

if __name__ == "__main__":
    force_recalc_positions()
