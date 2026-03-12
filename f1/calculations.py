from models import db, Race, Result, DriverStanding, ConstructorStanding

POINTS_SYSTEM = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1
}

def calculate_points(position, fastest_lap=False):
    """
    Calculate points for a given position.
    Adds +1 for fastest lap if inside top 10.
    """
    points = POINTS_SYSTEM.get(position, 0)
    if fastest_lap and position <= 10:
        points += 1
    return points

def update_standings(race_id):
    """
    Recalculate standings for the season associated with the race.
    Should be called after results are ingested for a race.
    """
    race = Race.query.get(race_id)
    if not race:
        return
        
    season = race.season
    
    # Get all races for this season
    season_races = Race.query.filter_by(season=season).all()
    race_ids = [r.id for r in season_races]
    
    # Get all results for this season
    results = Result.query.filter(Result.race_id.in_(race_ids)).all()
    
    driver_points = {} # driver_id -> {points, wins}
    constructor_points = {} # constructor_id -> {points, wins}
    
    for r in results:
        # Driver Stats
        if r.driver_id not in driver_points:
            driver_points[r.driver_id] = {'points': 0, 'wins': 0}
        driver_points[r.driver_id]['points'] += r.points
        if r.position == 1:
            driver_points[r.driver_id]['wins'] += 1
            
        # Constructor Stats
        if r.constructor_id not in constructor_points:
            constructor_points[r.constructor_id] = {'points': 0, 'wins': 0}
        constructor_points[r.constructor_id]['points'] += r.points
        if r.position == 1:
            # Wins for constructor are counted if any of their drivers win
            constructor_points[r.constructor_id]['wins'] += 1
            
    # Update DB - Driver
    # Delete old standings for this season to avoid duplicates/stale data
    DriverStanding.query.filter_by(season=season).delete()
    # Sort manually to grant positions
    sorted_drivers = sorted(driver_points.items(), key=lambda x: (x[1]['points'], x[1]['wins']), reverse=True)
    
    for i, (driver_id, stats) in enumerate(sorted_drivers):
        ds = DriverStanding(
            season=season,
            driver_id=driver_id,
            points=stats['points'],
            wins=stats['wins'],
            position=i+1
        )
        db.session.add(ds)
        
    sorted_constructors = sorted(constructor_points.items(), key=lambda x: (x[1]['points'], x[1]['wins']), reverse=True)
        
    # Update DB - Constructor
    ConstructorStanding.query.filter_by(season=season).delete()
    for i, (constructor_id, stats) in enumerate(sorted_constructors):
        cs = ConstructorStanding(
            season=season,
            constructor_id=constructor_id,
            points=stats['points'],
            wins=stats['wins'],
            position=i+1
        )
        db.session.add(cs)
        
    db.session.commit()
