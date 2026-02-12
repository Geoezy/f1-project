import random
from app import app
from models import db, Race, Result, Driver, Constructor
from ingestion import calculate_points, update_standings

# Simulation Weights (Driver ID -> Weight)
# Based on 2025 Performance trends (hypothetical)
# 32: Piastri (High), 3: Norris (High), 20: Verstappen (High)
# 15: Russell (Med-High), 37: Antonelli (Med), 2: Leclerc (Med)
# 5: Sainz (Med-Low - Williams), 14: Alonso (Med)

DRIVER_WEIGHTS = {
    3: 98,  # Norris (Champion)
    32: 92, # Piastri (Strong 2nd)
    20: 88, # Verstappen
    15: 85, # Russell
    2: 84,  # Leclerc
    37: 78, # Antonelli
    14: 75, # Alonso
    33: 70, # Lawson
    6: 65,  # Perez
    5: 60,  # Sainz
}

def get_weight(driver_id):
    return DRIVER_WEIGHTS.get(driver_id, 40) # Default low weight

def simulate_2025():
    print("Simulating REALISTIC 2025 Season...")
    
    # 1. Clear existing 2025 results
    races_2025 = Race.query.filter_by(season=2025).all()
    for race in races_2025:
        Result.query.filter_by(race_id=race.id).delete()
        race.is_completed = False
    db.session.commit()
    
    drivers = Driver.query.all()
    
    for race in races_2025:
        print(f"Simulating {race.name}...")
        
        # Weighted random shuffle
        # We assign a random score based on weight + variance
        race_scores = []
        for d in drivers:
            score = get_weight(d.id) + random.uniform(-15, 15)
            # DNF Chance (low for top drivers, higher for others)
            if random.random() < 0.05: 
                score = -999 # Crash
            race_scores.append((d, score))
            
        # Sort by score desc
        race_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Assign positions
        for pos, (driver, score) in enumerate(race_scores, start=1):
            if score == -999:
                status = "Collision"
                position = 20 # approximated DNF pos
                points = 0
            else:
                status = "Finished"
                position = pos
                # Fastest lap logic: usually top 5 driver
                is_fastest = (pos == 1 and random.random() < 0.3) or (pos < 10 and random.random() < 0.1)
                points = calculate_points(pos, is_fastest)
            
            # Determine team (Use current map or let ingestion logic handle if we had valid team_id)
            # We must use the team_id from the driver object IF it was fixed.
            # fix_team_history.py fixed the *Results* but not the Driver.team_id permanently in all cases used here?
            # Actually, calculate_points doesn't need team. Result entry needs team.
            # We should use driver.team_id, but remember 2025 mapping.
            # Let's re-apply the 2025 mapping logic here to be safe.
            
            # (Copying map from fix_team_history.py for consistency)
            TEAMS_2025 = {
                4: 2, 5: 8, 1: 13, 29: 13, 20: 9, 6: 9, 2: 2, 3: 3, 32: 3,
                15: 1, 14: 11, 18: 11, 7: 12, 8: 10, 13: 8, 17: 10, 21: 13,
                24: 14, 33: 14, 34: 12, 35: 10, 37: 1, 36: 12, 38: 13, 39: 14
            }
            team_id = TEAMS_2025.get(driver.id, driver.team_id) # Fallback to current
            
            result = Result(
                race_id=race.id,
                driver_id=driver.id,
                constructor_id=team_id,
                position=position,
                points=points,
                grid=position, # simplified
                laps=50 if status == "Finished" else random.randint(0, 40),
                status=status,
                fastest_lap=(pos==1 and is_fastest), # Simplified
                time="1:30:00.000" if pos == 1 else f"+{pos * 2}.000"
            )
            db.session.add(result)
            
        race.is_completed = True
        db.session.commit()
        update_standings(race.id)

    print("2025 Simulation Complete.")

if __name__ == "__main__":
    with app.app_context():
        simulate_2025()
