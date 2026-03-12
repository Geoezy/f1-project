import requests
import os
from app import app
from models import Driver, Constructor, db

assets = {
    'Andrea Kimi Antonelli': ('https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg/800px-Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg', 'kimi.jpg', 'Driver'),
    'Arvid Lindblad': ('https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Arvid_Lindblad_at_the_Red_Bull_Fan_Zone_%E2%80%93_Crown_Riverwalk%2C_Melbourne_%28028A7869%29_%28cropped%29.jpg/800px-Arvid_Lindblad_at_the_Red_Bull_Fan_Zone_%E2%80%93_Crown_Riverwalk%2C_Melbourne_%28028A7869%29_%28cropped%29.jpg', 'arvid.jpg', 'Driver'),
    'Red Bull Racing': ('https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Red_Bull_Racing_RB20_Verstappen.jpeg/800px-Red_Bull_Racing_RB20_Verstappen.jpeg', 'redbull.jpg', 'Constructor'),
    'Aston Martin': ('https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Aston_Martin_AMR24_Alonso.jpeg/800px-Aston_Martin_AMR24_Alonso.jpeg', 'aston.jpg', 'Constructor'),
    'Audi': ('https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Das_Audi_Forum_Ingolstadt.JPG/800px-Das_Audi_Forum_Ingolstadt.JPG', 'audi.jpg', 'Constructor'),
    'Cadillac F1 Team': ('https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/512px-Cadillac_emblem.svg.png', 'cadillac.png', 'Constructor')
}

dest = "static/images/assets"
os.makedirs(dest, exist_ok=True)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

with app.app_context():
    for name, (url, filename, type_) in assets.items():
        filepath = os.path.join(dest, filename)
        r = requests.get(url, headers=headers)
        if r.status_code == 200 and len(r.content) > 2000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"Downloaded {filename} ({len(r.content)} bytes)")
            local_url = f"/static/images/assets/{filename}?v=1"  # Add cache buster to the image url
            
            if type_ == 'Driver':
                d = Driver.query.filter_by(name=name).first()
                if d: d.image_url = local_url
            else:
                c = Constructor.query.filter_by(name=name).first()
                if c: c.car_image_url = local_url
        else:
            print(f"Failed {filename}: {r.status_code} ({len(r.content)} bytes)")
            
    db.session.commit()
print("Done patching DB with local assets.")
