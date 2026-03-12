import requests
import time
from app import app
from models import Driver, Constructor, db

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,*/*;q=0.8"
}

def dl_special(title, filename, is_driver, display_name):
    # Special:FilePath always redirects to the actual image URL automatically!
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{title}"
    r = requests.get(url, headers=headers)
    print(f"Downloading {filename} -> Status: {r.status_code}, length: {len(r.content)}")
    if r.status_code == 200 and len(r.content) > 1000:
        with open(f"static/images/assets/{filename}", "wb") as f:
            f.write(r.content)
            
        with app.app_context():
            local = f"/static/images/assets/{filename}?v=9"
            if is_driver:
                d = Driver.query.filter_by(name=display_name).first()
                if d: d.image_url = local
            else:
                c = Constructor.query.filter_by(name=display_name).first()
                if c: c.car_image_url = local
            db.session.commit()
            print(f"Patched {display_name} -> {local}")

# The EXACT Wikimedia filenames for Kimi and Cadillac SVG
dl_special("Andrea_Kimi_Antonelli_Monza_2024_(cropped).jpg", "kimi.jpg", True, "Andrea Kimi Antonelli")
time.sleep(2)
dl_special("Cadillac_emblem.svg", "cadillac.svg", False, "Cadillac F1 Team")
