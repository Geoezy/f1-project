import requests
import os
import time
from app import app
from models import Driver, Constructor, db

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def get_wiki_thumb(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=800"
    r = requests.get(url, headers=headers).json()
    pages = r["query"]["pages"]
    for page_id in pages:
        if "thumbnail" in pages[page_id]:
            return pages[page_id]["thumbnail"]["source"]
    return None

def dl_img(url, filename, type_, name):
    dest = "static/images/assets"
    os.makedirs(dest, exist_ok=True)
    r = requests.get(url, headers=headers)
    print(f"Downloading {filename} from {url} -> Status {r.status_code}, length {len(r.content)}")
    if r.status_code == 200 and len(r.content) > 1000:
        with open(f"{dest}/{filename}", "wb") as f:
            f.write(r.content)
        
        local_url = f"/static/images/assets/{filename}?v=6"
        with app.app_context():
            if type_ == 'Driver':
                d = Driver.query.filter_by(name=name).first()
                if d: d.image_url = local_url
            else:
                c = Constructor.query.filter_by(name=name).first()
                if c: c.car_image_url = local_url
            db.session.commit()

# Assets to process
assets = [
    ("Andrea_Kimi_Antonelli", "kimi.jpg", "Driver", "Andrea Kimi Antonelli"),
    ("Arvid_Lindblad", "arvid.jpg", "Driver", "Arvid Lindblad"),
    ("Red_Bull_Racing_RB20", "redbull.jpg", "Constructor", "Red Bull Racing"),
    ("Cadillac", "cadillac.jpg", "Constructor", "Cadillac F1 Team"),
    ("Aston_Martin_AMR24", "aston.jpg", "Constructor", "Aston Martin")
]

for title, fname, type_, display_name in assets:
    url = get_wiki_thumb(title)
    if url:
        dl_img(url, fname, type_, display_name)
    else:
        print(f"[{display_name}] URL not found via API")
    time.sleep(1)

print("Master Wikipedia JSON/Scraper complete.")
