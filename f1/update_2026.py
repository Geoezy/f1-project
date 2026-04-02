from app import app, db
from models import Race

with app.app_context():
    races_to_delete = Race.query.filter(
        Race.season == 2026,
        Race.name.in_(['Bahrain Grand Prix', 'Saudi Arabian Grand Prix'])
    ).all()
    
    if races_to_delete:
        for r in races_to_delete:
            print(f"Deleting 2026 race: {r.name}")
            db.session.delete(r)
        db.session.commit()
    else:
        print("Bahrain and Saudi Arabian GPs not found or already deleted for 2026.")

    # Reorder remaining races by date
    remaining_races = Race.query.filter_by(season=2026).order_by(Race.date).all()
    for index, r in enumerate(remaining_races, start=1):
        if r.round != index:
            print(f"Updating round for {r.name} from {r.round} to {index} (Date: {r.date})")
            r.round = index
            
    db.session.commit()
    print("2026 season updated.")
