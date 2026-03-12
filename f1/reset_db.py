from app import app, db
from sqlalchemy import inspect

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    
    print("Inspecting Race table...")
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('race')]
    print(f"Race columns: {columns}")
    
    if 'season' in columns:
        print("SUCCESS: season column exists.")
    else:
        print("FAILURE: season column MISSING.")
