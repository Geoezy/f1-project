from app import app
from models import Race
import os

with app.app_context():
    print("Verifying Circuit Images...")
    races = Race.query.all()
    unique_circuits = set()
    
    for r in races:
        if r.circuit_name not in unique_circuits:
            unique_circuits.add(r.circuit_name)
            print(f"Circuit: {r.circuit_name}")
            print(f"  DB URL: {r.circuit_image_url}")
            
            if r.circuit_image_url and r.circuit_image_url.startswith('/static/'):
                # Check if file exists
                rel_path = r.circuit_image_url.lstrip('/')
                if os.path.exists(rel_path):
                    size = os.path.getsize(rel_path)
                    print(f"  File Status: EXISTS (Size: {size} bytes)")
                else:
                    print(f"  File Status: MISSING at {rel_path}")
            else:
                print("  File Status: N/A (External or None)")
            print("-" * 30)
