from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False, default=2026)
    round = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    circuit_name = db.Column(db.String(100), nullable=False)
    circuit_image_url = db.Column(db.String(255), nullable=True) # URL to track image
    is_completed = db.Column(db.Boolean, default=False)
    
    results = db.relationship('Result', backref='race', lazy=True)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(50), unique=True) # ID from external API (e.g., 'max_verstappen')
    name = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(50))
    code = db.Column(db.String(5))
    team_id = db.Column(db.Integer, db.ForeignKey('constructor.id'))

class Constructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(50), unique=True) # ID from external API (e.g., 'red_bull')
    name = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(50))
    
    drivers = db.relationship('Driver', backref='team', lazy=True)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    constructor_id = db.Column(db.Integer, db.ForeignKey('constructor.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Float, default=0.0)
    grid = db.Column(db.Integer)
    laps = db.Column(db.Integer)
    status = db.Column(db.String(50)) # Finished, Accident, +1 Lap etc.
    fastest_lap = db.Column(db.Boolean, default=False)
    time = db.Column(db.String(50)) # Time string or gap

    __table_args__ = (db.UniqueConstraint('race_id', 'driver_id', name='_race_driver_uc'),)

class DriverStanding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False, default=2026)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    points = db.Column(db.Float, default=0.0)
    position = db.Column(db.Integer)
    wins = db.Column(db.Integer, default=0)
    
    driver = db.relationship('Driver', backref='standings')

class ConstructorStanding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False, default=2026)
    constructor_id = db.Column(db.Integer, db.ForeignKey('constructor.id'), nullable=False)
    points = db.Column(db.Float, default=0.0)
    position = db.Column(db.Integer)
    wins = db.Column(db.Integer, default=0)
    
    constructor = db.relationship('Constructor', backref='standings')
