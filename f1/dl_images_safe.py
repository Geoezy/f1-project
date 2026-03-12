import requests
import os
import time
from app import app
from models import Driver, Constructor, db

assets = {
    'Andrea Kimi Antonelli': ('https://upload.wikimedia.org/wikipedia/commons/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg', 'kimi.jpg', 'Driver'),
    'Arvid Lindblad': ('https://upload.wikimedia.org/wikipedia/commons/c/c5/Arvid_Lindblad_in_2024.jpg', 'arvid.jpg', 'Driver'),
    'Audi': ('https://upload.wikimedia.org/wikipedia/commons/b/ba/Audi_show_car.jpg', 'audi.jpg', 'Constructor'),
    'Cadillac F1 Team': ('https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/512px-Cadillac_emblem.svg.png', 'cadillac.png', 'Constructor'),
    'Red Bull Racing': ('https://upload.wikimedia.org/wikipedia/commons/e/e0/Red_Bull_Racing_RB20_Verstappen.jpeg', 'redbull.jpg', 'Constructor'),
    'Aston Martin': ('https://upload.wikimedia.org/wikipedia/commons/5/52/Aston_Martin_AMR24_Alonso.jpeg', 'aston.jpg', 'Constructor')
}

dest = "static/images/assets"
os.makedirs(dest, exist_ok=True)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

with app.app_context():
    for name, (url, filename, type_) in assets.items():
        filepath = os.path.join(dest, filename)
        print(f"Downloading {name}...")
        try:
            r = requests.get(url, headers=headers, stream=True)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(1024): f.write(chunk)
                
                size = os.path.getsize(filepath)
                if size > 5000: # Ensure it's not a tiny Error HTML page
                    print(f"Success! Saved {filename} ({size} bytes)")
                    local_url = f"/static/images/assets/{filename}?v=2"
                    
                    if type_ == 'Driver':
                        d = Driver.query.filter_by(name=name).first()
                        if d: d.image_url = local_url
                    else:
                        c = Constructor.query.filter_by(name=name).first()
                        if c: c.car_image_url = local_url
                else:
                    print(f"File too small, possibly blocked. {size} bytes.")
            else:
                print(f"Failed {filename}: HTTP {r.status_code}")
        except Exception as e:
            print(f"Exception: {e}")
            
        time.sleep(3) # Wait 3 seconds to avoid 429 Too Many Requests
            
    db.session.commit()
print("Finished downloading local assets with rate limiting.")
