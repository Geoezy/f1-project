from flask import Flask, jsonify, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, Race, Result, DriverStanding, ConstructorStanding, Driver, Constructor
from ingestion import fetch_season_schedule, fetch_race_results
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f1_2026.db'
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
        
        # 2. Check for completed races that need results
        # Find next uncompleted race
        next_race = Race.query.filter_by(is_completed=False).order_by(Race.date).first()
        if next_race:
            print(f"Scheduler: Attempting to fetch results for {next_race.name}...")
            success = fetch_race_results(next_race.round)
            if success:
                print(f"Scheduler: Successfully updated {next_race.name}")
        else:
            print("Scheduler: All races completed or no races found.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", seconds=60) # Check every 60 seconds
# scheduler.start() moved to main block

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/races')
def get_races():
    season = request.args.get('season', default=2026, type=int)
    races = Race.query.filter_by(season=season).order_by(Race.date).all()
    data = []
    for r in races:
        winner_team = None
        if r.is_completed:
            # Get winner result (pos 1)
            winner = Result.query.filter_by(race_id=r.id, position=1).first()
            if winner:
                cons = Constructor.query.get(winner.constructor_id)
                if cons:
                    winner_team = cons.name
        
        data.append({
            'id': r.id,
            'round': r.round,
            'name': r.name,
            'date': r.date.isoformat(),
            'circuit': r.circuit_name,
            'circuit_image': r.circuit_image_url,
            'is_completed': r.is_completed,
            'winner_team': winner_team
        })
    return jsonify(data)

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
            'driver_name': driver.name,
            'constructor_name': constructor.name,
            'points': r.points,
            'time': r.time,
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
        'results': results_data
    })

from models import Race, Result, Driver, Constructor, DriverStanding, ConstructorStanding, db
# ... (imports)

@app.route('/api/standings/drivers')
def get_driver_standings():
    season = request.args.get('season', default=2026, type=int)
    standings = DriverStanding.query.filter_by(season=season).order_by(DriverStanding.points.desc()).all()
    data = []
    for s in standings:
        driver = Driver.query.get(s.driver_id)
        constructor_name = "Unknown"
        
        # FIX: Get constructor from the latest result of this season, not the current driver.team_id
        last_result = Result.query.join(Race).filter(
            Race.season == season, 
            Result.driver_id == driver.id
        ).order_by(Race.date.desc()).first()
        
        if last_result:
             constructor = Constructor.query.get(last_result.constructor_id)
             if constructor:
                 constructor_name = constructor.name
        elif driver.team_id:
            # Fallback for 2026 or no results yet
             constructor = Constructor.query.get(driver.team_id)
             if constructor:
                 constructor_name = constructor.name
                
        data.append({
            'position': s.position if s.position else 0, 
            'driver_name': driver.name,
            'constructor_name': constructor_name,
            'points': s.points,
            'wins': s.wins
        })
    # Add manual ranking index
    for i, item in enumerate(data):
        item['position'] = i + 1
        
    return jsonify(data)

@app.route('/api/standings/constructors')
def get_constructor_standings():
    season = request.args.get('season', default=2026, type=int)
    standings = ConstructorStanding.query.filter_by(season=season).order_by(ConstructorStanding.points.desc()).all()
    data = []
    for s in standings:
        constructor = Constructor.query.get(s.constructor_id)
        data.append({
            'position': s.position, 
            'constructor_name': constructor.name,
            'points': s.points,
            'wins': s.wins
        })
    
    # Add manual ranking index
    for i, item in enumerate(data):
        item['position'] = i + 1
        
    return jsonify(data)

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
    # Ensure DB exists
    if not os.path.exists('f1_2026.db'):
        with app.app_context():
            db.create_all()
            print("DB Created.")
    
    # Start Scheduler only in the main process
    scheduler.start()
            
    app.run(debug=True, port=5000, use_reloader=False)
