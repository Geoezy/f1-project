
from app import app, db
from models import Race
from datetime import datetime, timedelta

def seed_2026():
    with app.app_context():
        # Check if 2026 races exist
        if Race.query.filter_by(season=2026).first():
            print("2026 season already exists.")
            return
            
        print("Seeding 2026 Schedule (Based on 2025 + 364 days)...")
        
        # Get 2025 races
        races_25 = Race.query.filter_by(season=2025).order_by(Race.round).all()
        
        for r in races_25:
            new_date = r.date + timedelta(days=364) # Shift roughly a year
            
            nr = Race(
                season=2026,
                round=r.round,
                name=r.name,
                circuit_name=r.circuit_name,
                date=new_date,
                circuit_image_url=r.circuit_image_url,
                is_completed=False
            )
            db.session.add(nr)
            print(f"  Added: {nr.name} ({new_date.date()})")
            
        db.session.commit()
        print("2026 Seeded.")

if __name__ == "__main__":
    seed_2026()
