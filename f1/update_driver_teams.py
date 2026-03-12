from app import app
from models import Driver, Constructor, db, Result, Race

def assign_teams():
    with app.app_context():
        # Clean up duplicates if Max/Lando exist twice?
        import collections
        drivers = Driver.query.all()
        # Let's map teams backward from the latest Result
        for d in drivers:
            # If team is already assigned, leave it
            last_result = Result.query.join(Race).filter(Result.driver_id == d.id).order_by(Race.date.desc()).first()
            if last_result and not d.team_id:
                d.team_id = last_result.constructor_id
                print(f"Assigned {d.name} -> Team ID {d.team_id} from results")
                
        db.session.commit()
        
        # Hardcodes for Rookies/Transfers missing results
        transfers = {
            'Lewis Hamilton': 'Ferrari',
            'Carlos Sainz': 'Williams',
            'Nico Hülkenberg': 'Kick Sauber',
            'Esteban Ocon': 'Haas F1 Team',
            'Gabriel Bortoleto': 'Kick Sauber',
            'Andrea Kimi Antonelli': 'Mercedes',
            'Oliver Bearman': 'Haas F1 Team',
            'Jack Doohan': 'Alpine',
            'Isack Hadjar': 'RB',
            'Liam Lawson': 'RB',
            'Franco Colapinto': 'Williams'  # or whatever your DB expects
        }
        
        for name, team_name in transfers.items():
            dds = Driver.query.filter_by(name=name).all()
            cons = Constructor.query.filter_by(name=team_name).first()
            if cons:
                for d in dds:
                    d.team_id = cons.id
                    print(f"Hardcoded {d.name} -> {team_name}")
                    
        db.session.commit()
        print("Driver team relationships updated.")

if __name__ == "__main__":
    assign_teams()
