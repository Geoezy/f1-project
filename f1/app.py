from flask import Flask, jsonify, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from extensions import db
from models import Race, Result, DriverStanding, ConstructorStanding, Driver, Constructor
from ingestion import fetch_season_schedule, fetch_race_results
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'f1_2026.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- Scheduler ---
def scheduled_task():
    """
    Periodic task to check for new race results.
    """
    with app.app_context():
        # 1. Ensure schedule is up to date (e.g. if dates change)
        print("Scheduler: Checking for updates...")
        # For simplicity, we might not fetch schedule every time, but good to ensure DB is populated
        # fetch_season_schedule() 
        
        import datetime
        today = datetime.date.today()
        
        # 2. Check for completed races that need results
        # Find uncompleted races that have already happened
        past_uncompleted_races = Race.query.filter(
            Race.is_completed == False,
            Race.date <= today
        ).order_by(Race.date).all()
        
        if past_uncompleted_races:
            for race in past_uncompleted_races:
                print(f"Scheduler: Attempting to fetch results for {race.season} {race.name}...")
                success = fetch_race_results(race.season, race.round)
                if success:
                    print(f"Scheduler: Successfully updated {race.name}")
                else:
                    print(f"Scheduler: Results not yet available for {race.name}")
        else:
            print("Scheduler: All past races are completed. Waiting for next race.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", seconds=60) # Check every 60 seconds
# scheduler.start() moved to main block

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/api/races/<int:race_id>/results')
def get_race_results_api(race_id):
    results = Result.query.filter_by(race_id=race_id).order_by(Result.position).all()
    data = []
    for r in results:
        driver = Driver.query.get(r.driver_id)
        constructor = Constructor.query.get(r.constructor_id)
        data.append({
            'position': r.position,
            'driver_name': driver.name if driver else "Unknown",
            'constructor_name': constructor.name if constructor else "Unknown",
            'points': r.points,
            'time': r.time
        })
    return jsonify(data)

@app.route('/api/races')
def get_races():
    season = request.args.get('season', default=2025, type=int)
    races = Race.query.filter_by(season=season).order_by(Race.date).all()
    data = []
    for r in races:
        winner_team = None
        winner_driver_name = None
        winner_driver_image = None
        
        if r.is_completed:
            # Get winner result (pos 1)
            winner = Result.query.filter_by(race_id=r.id, position=1).first()
            if winner:
                driver = Driver.query.get(winner.driver_id)
                if driver:
                    winner_driver_name = driver.name
                    winner_driver_image = driver.image_url
                    
                cons = Constructor.query.get(winner.constructor_id)
                if cons:
                    winner_team = cons.name
                
                winner_time = winner.time
        
        data.append({
            'id': r.id,
            'round': r.round,
            'name': r.name,
            'date': r.date.isoformat(),
            'circuit': r.circuit_name,
            'circuit_image': r.circuit_image_url,
            'is_completed': r.is_completed,
            'winner_team': winner_team,
            'winner_driver_name': winner_driver_name,
            'winner_driver_image': winner_driver_image,
            'winner_time': locals().get('winner_time', 'N/A')
        })
    return jsonify(data)

@app.route('/api/races/next')
def get_next_race():
    import datetime
    next_race = Race.query.filter(Race.date >= datetime.date.today()).order_by(Race.date).first()
    if next_race:
        return jsonify({
            'id': next_race.id,
            'round': next_race.round,
            'name': next_race.name,
            'date': next_race.date.isoformat(),
            'circuit': next_race.circuit_name,
            'circuit_image': next_race.circuit_image_url,
            'is_completed': next_race.is_completed
        })
    return jsonify({}), 404

@app.route('/api/races/<int:race_id>')
def get_race_details(race_id):
    race = Race.query.get_or_404(race_id)
    results = Result.query.filter_by(race_id=race_id).order_by(Result.position).all()
    
    results_data = []
    for r in results:
        driver = Driver.query.get(r.driver_id)
        constructor = Constructor.query.get(r.constructor_id)
        results_data.append({
            'position': r.position,
            'driver_id': driver.id,
            'driver_name': driver.name,
            'driver_image_url': driver.image_url,
            'constructor_name': constructor.name,
            'points': r.points,
            'time': r.time,
            'grid': r.grid,
            'laps': r.laps,
            'reason': r.status,
            'fastest_lap': r.fastest_lap
        })
        
    return jsonify({
        'name': race.name,
        'season': race.season,
        'round': race.round,
        'date': race.date.isoformat(),
        'circuit': race.circuit_name,
        'circuit_image': race.circuit_image_url,
        'is_completed': race.is_completed,
        'winner_driver_name': results_data[0]['driver_name'] if results_data else None,
        'winner_driver_image': results_data[0]['driver_image_url'] if results_data else None,
        'winner_time': results_data[0]['time'] if results_data else None,
        'results': results_data
    })

from models import Race, Result, Driver, Constructor, DriverStanding, ConstructorStanding, db
# ... (imports)

@app.route('/api/standings/drivers')
def get_driver_standings():
    season = request.args.get('season', default=2025, type=int)
    from sqlalchemy import func
    
    # Check if pre-calculated/mock standings exist in DB
    has_completed_races = Race.query.filter_by(season=season, is_completed=True).first()
    precalc = DriverStanding.query.filter_by(season=season).order_by(DriverStanding.position).all()
    
    use_precalc = False
    if precalc:
        if season < 2026:
            use_precalc = True
        elif season >= 2026 and not has_completed_races:
            use_precalc = True

    if use_precalc:
        data = []
        for s in precalc:
            driver = s.driver
            team_name = "Unknown"
            if driver:
                last_result = Result.query.join(Race).filter(
                    Race.season == season,
                    Result.driver_id == driver.id
                ).order_by(Race.date.desc()).first()
                if last_result:
                    cons = Constructor.query.get(last_result.constructor_id)
                    if cons: team_name = cons.name
                elif driver.team:
                    team_name = driver.team.name

            data.append({
                'position': s.position,
                'driver_name': driver.name if driver else "Unknown",
                'nationality': driver.nationality if driver else "",
                'country_code': driver.country_code if driver else "",
                'constructor_name': team_name,
                'points': s.points,
                'image_url': driver.image_url if driver else ""
            })
        return jsonify(data)
        
    # Dynamic calculation using SQLAlchemy aggregation
    standings_query = db.session.query(
        Result.driver_id,
        func.sum(Result.points).label('total_points')
    ).join(Race).filter(Race.season == season).group_by(Result.driver_id).order_by(func.sum(Result.points).desc()).all()
    
    data = []
    
    # If no results (e.g. start of 2025), show all drivers with 0 points
    if not standings_query and season == 2025:
         drivers = Driver.query.all()
         for d in drivers:
             data.append({
                'position': 0,
                'driver_name': d.name,
                'nationality': d.nationality,
                'country_code': d.country_code or '',
                'constructor_name': d.team.name if d.team else "Unknown",
                'points': 0,
                'image_url': d.image_url
             })
    else:
        for i, (driver_id, points) in enumerate(standings_query):
            driver = Driver.query.get(driver_id)
            if not driver: continue
            
            # Get team for this season (latest result)
            last_result = Result.query.join(Race).filter(
                Race.season == season, 
                Result.driver_id == driver_id
            ).order_by(Race.date.desc()).first()
            
            team_name = "Unknown"
            if last_result:
                cons = Constructor.query.get(last_result.constructor_id)
                if cons: team_name = cons.name
            elif driver.team: # Fallback
                team_name = driver.team.name
                
            data.append({
                'position': i + 1,
                'driver_name': driver.name,
                'nationality': driver.nationality,
                'country_code': driver.country_code or driver.nationality[:3].upper() if driver.nationality else "",
                'constructor_name': team_name,
                'points': float(points),
                'image_url': driver.image_url
            })
            
    return jsonify(data)

@app.route('/api/standings/constructors')
def get_constructor_standings():
    season = request.args.get('season', default=2025, type=int)
    from sqlalchemy import func
    
    has_completed_races = Race.query.filter_by(season=season, is_completed=True).first()
    precalc = ConstructorStanding.query.filter_by(season=season).order_by(ConstructorStanding.position).all()
    
    use_precalc = False
    if precalc:
        if season < 2026:
            use_precalc = True
        elif season >= 2026 and not has_completed_races:
            use_precalc = True

    if use_precalc:
        data = []
        for s in precalc:
            cons = s.constructor
            data.append({
                'position': s.position,
                'constructor_name': cons.name if cons else "Unknown",
                'points': s.points,
                'car_image_url': cons.car_image_url if cons else "",
                'sponsors': cons.sponsors if cons else "",
                'base': cons.base if cons else ""
            })
        return jsonify(data)
        
    standings_query = db.session.query(
        Result.constructor_id,
        func.sum(Result.points).label('total_points')
    ).join(Race).filter(Race.season == season).group_by(Result.constructor_id).order_by(func.sum(Result.points).desc()).all()
    
    data = []
    
    if not standings_query and season == 2025:
         teams = Constructor.query.all()
         for t in teams:
             data.append({
                'position': 0,
                'constructor_name': t.name,
                'points': 0,
                'car_image_url': t.car_image_url
             })
    else:
        for i, (constructor_id, points) in enumerate(standings_query):
            cons = Constructor.query.get(constructor_id)
            if not cons: continue
            
            data.append({
                'position': i + 1,
                'constructor_name': cons.name,
                'points': float(points),
                'car_image_url': cons.car_image_url,
                'sponsors': cons.sponsors,
                'base': cons.base
            })
        
    return jsonify(data)

@app.route('/api/drivers/<int:driver_id>')
def get_driver_details(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    
    # Calculate key stats
    results = Result.query.filter_by(driver_id=driver_id).all()
    wins = sum(1 for r in results if r.position == 1)
    podiums = sum(1 for r in results if r.position <= 3)
    points = sum(r.points for r in results)
    starts = len(results)
    
    # Get current or last known constructor
    constructor_name = "Unknown"
    if driver.team_id:
        cons = Constructor.query.get(driver.team_id)
        if cons:
            constructor_name = cons.name
    
    return jsonify({
        'id': driver.id,
        'name': driver.name,
        'nationality': driver.nationality,
        'image_url': driver.image_url,
        'constructor_name': constructor_name,
        'stats': {
            'wins': wins,
            'podiums': podiums,
            'points': points,
            'starts': starts
        }
    })

@app.route('/api/init')
def init_db():
    """Helper to initialize DB and fetch schedule manually"""
    db.create_all()
    # Fetch all seasons 2020-2026
    # Import locally to avoid circular import if structured poorly, but here it's fine
    from ingestion import fetch_all_seasons
    fetch_all_seasons()
    return jsonify({"message": "Database initialized and schedules (2020-2026) fetched."})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 1. Fetch Schedules
        if not Race.query.filter_by(season=2025).first():
            print("Seeding 2025 Schedule...")
            fetch_season_schedule(2025)
            
        if not Race.query.filter_by(season=2026).first():
            print("Seeding 2026 Schedule...")
            fetch_season_schedule(2026)
            
        # 2. Seed Drivers & Teams (Critical for Fresh DB)
        if not Driver.query.filter_by(name='Lando Norris').first():
             print("Seeding Drivers & Constructors...")
             # Teams
             teams = [
                 {'name': 'McLaren', 'ext_id': 'mclaren', 'nat': 'British', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/mclaren.png.transform/4col/image.png'},
                 {'name': 'Red Bull Racing', 'ext_id': 'red_bull', 'nat': 'Austrian', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/red-bull-racing.png.transform/4col/image.png'},
                 {'name': 'Ferrari', 'ext_id': 'ferrari', 'nat': 'Italian', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/ferrari.png.transform/4col/image.png'},
                 {'name': 'Mercedes', 'ext_id': 'mercedes', 'nat': 'German', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/mercedes.png.transform/4col/image.png'},
                 {'name': 'Aston Martin', 'ext_id': 'aston_martin', 'nat': 'British', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/aston-martin.png.transform/4col/image.png'},
                 {'name': 'Alpine', 'ext_id': 'alpine', 'nat': 'French', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/alpine.png.transform/4col/image.png'},
                 {'name': 'Williams', 'ext_id': 'williams', 'nat': 'British', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/williams.png.transform/4col/image.png'},
                 {'name': 'RB', 'ext_id': 'rb', 'nat': 'Italian', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/rb.png.transform/4col/image.png'},
                 {'name': 'Kick Sauber', 'ext_id': 'sauber', 'nat': 'Swiss', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/kick-sauber.png.transform/4col/image.png'},
                 {'name': 'Haas F1 Team', 'ext_id': 'haas', 'nat': 'American', 'img': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2025/haas-f1-team.png.transform/4col/image.png'}
             ]
             for t in teams:
                 cons = Constructor.query.filter_by(name=t['name']).first()
                 if not cons:
                     db.session.add(Constructor(name=t['name'], external_id=t['ext_id'], nationality=t['nat'], car_image_url=t.get('img')))
                 elif not cons.car_image_url and 'img' in t:
                     cons.car_image_url = t['img']
                     db.session.add(cons)
             db.session.commit()

             # Drivers
             drivers = [
                 {'name': 'Lando Norris', 'code': 'NOR', 'num': 4, 'team': 'McLaren', 'img': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png'},
                 {'name': 'Max Verstappen', 'code': 'VER', 'num': 1, 'team': 'Red Bull Racing', 'img': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png'},
                 {'name': 'Oscar Piastri', 'code': 'PIA', 'num': 81, 'team': 'McLaren', 'img': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/2col/image.png'},
                 {'name': 'George Russell', 'code': 'RUS', 'num': 63, 'team': 'Mercedes', 'img': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png'},
                 {'name': 'Charles Leclerc', 'code': 'LEC', 'num': 16, 'team': 'Ferrari', 'img': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png'},
                 {'name': 'Lewis Hamilton', 'code': 'HAM', 'num': 44, 'team': 'Ferrari', 'img': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png'}
             ]
             for d in drivers:
                 if not Driver.query.filter_by(name=d['name']).first():
                     team = Constructor.query.filter_by(name=d['team']).first()
                     db.session.add(Driver(name=d['name'], code=d['code'], team_id=team.id if team else None, image_url=d['img']))
             db.session.commit()

        # 3. Mock 2025 Standings (so app isn't empty)
        if not DriverStanding.query.filter_by(season=2025).first():
             d_norris = Driver.query.filter_by(name='Lando Norris').first()
             d_ver = Driver.query.filter_by(name='Max Verstappen').first()
             d_pia = Driver.query.filter_by(name='Oscar Piastri').first()
             d_rus = Driver.query.filter_by(name='George Russell').first()
             d_lec = Driver.query.filter_by(name='Charles Leclerc').first()
             
             if d_norris and d_ver:
                  s_nor = DriverStanding(season=2025, driver_id=d_norris.id, points=423.0, wins=7, position=1)
                  s_ver = DriverStanding(season=2025, driver_id=d_ver.id, points=421.0, wins=8, position=2)
                  s_pia = DriverStanding(season=2025, driver_id=d_pia.id, points=410.0, wins=7, position=3)
                  s_rus = DriverStanding(season=2025, driver_id=d_rus.id, points=319.0, wins=2, position=4)
                  s_lec = DriverStanding(season=2025, driver_id=d_lec.id, points=242.0, wins=0, position=5)
                  
                  db.session.add_all([s_nor, s_ver, s_pia, s_rus, s_lec])
                  db.session.commit()
                  print("2025 Standings Seeded.")

    scheduler.start()
    app.run(debug=True, port=5001, use_reloader=False)
