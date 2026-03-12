
import requests
import json

def verify_api():
    base_url = "http://127.0.0.1:5001/api/standings"
    
    print("--- Verifying Driver Standings ---")
    try:
        r = requests.get(f"{base_url}/drivers?season=2025")
        if r.status_code == 200:
            data = r.json()
            print(f"Top 3 Drivers:")
            for i in range(min(3, len(data))):
                d = data[i]
                print(f"  {d['position']}. {d['driver_name']} ({d['constructor_name']}) - {d['points']} pts")
            
            # Check Hamilton
            ham = next((d for d in data if "Hamilton" in d['driver_name']), None)
            if ham:
                print(f"  ... {ham['position']}. {ham['driver_name']} ({ham['constructor_name']})")
        else:
            print(f"Failed to fetch drivers: {r.status_code}")
    except Exception as e:
        print(f"Driver check failed: {e}")

    print("\n--- Verifying Constructor Standings ---")
    try:
        r = requests.get(f"{base_url}/constructors?season=2025")
        if r.status_code == 200:
            data = r.json()
            print(f"Top 3 Teams:")
            for i in range(min(3, len(data))):
                c = data[i]
                print(f"  {c['position']}. {c['constructor_name']} - {c['points']} pts")
        else:
            print(f"Failed to fetch constructors: {r.status_code}")
    except Exception as e:
        print(f"Constructor check failed: {e}")

if __name__ == "__main__":
    print("=== 2025 VERIFICATION ===")
    verify_api()
    
    print("\n=== 2024 VERIFICATION ===")
    # Quick one-off check for 2024
    base_url = "http://127.0.0.1:5001/api/standings"
    try:
        r = requests.get(f"{base_url}/drivers?season=2024")
        if r.status_code == 200:
            data = r.json()
            print(f"Top 3 Drivers (2024):")
            for i in range(min(3, len(data))):
                d = data[i]
                print(f"  {d['position']}. {d['driver_name']} ({d['constructor_name']}) - {d['points']} pts")
    except Exception as e:
        print(f"2024 Check Failed: {e}")
