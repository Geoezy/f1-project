import requests
import json
import time
import urllib.request
import os
from app import app
from models import Driver, Constructor, db

def get_url(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=800"
    headers = {"User-Agent": "MyF1App/1.0 (contact@example.com)"}
    r = requests.get(url, headers=headers).json()
    pages = r["query"]["pages"]
    for page_id in pages:
        if "thumbnail" in pages[page_id]:
            return pages[page_id]["thumbnail"]["source"]
    return None

def dl(url, filename):
    req = urllib.request.Request(url, headers={'User-Agent': 'MyF1App/1.0 (contact@example.com)'})
    with urllib.request.urlopen(req) as response, open(f"static/images/assets/{filename}", 'wb') as out_file:
        data = response.read()
        out_file.write(data)
        print(f"Downloaded {filename}: {len(data)} bytes")
        return len(data)

urls = {
    'Andrea Kimi Antonelli': ('kimi.jpg', get_url("Andrea_Kimi_Antonelli"), 'Driver'),
    'Arvid Lindblad': ('arvid.jpg', get_url("Arvid_Lindblad"), 'Driver'),
    'Audi': ('audi.jpg', get_url("Audi"), 'Constructor'),
    'Cadillac F1 Team': ('cadillac.png', get_url("Cadillac"), 'Constructor')
}

dest = "static/images/assets"
os.makedirs(dest, exist_ok=True)

with app.app_context():
    for name, (filename, url, type_) in urls.items():
        if url:
            try:
                size = dl(url, filename)
                local_url = f"/static/images/assets/{filename}?v=4"
                
                if type_ == 'Driver':
                    d = Driver.query.filter_by(name=name).first()
                    if d: d.image_url = local_url
                else:
                    c = Constructor.query.filter_by(name=name).first()
                    if c: c.car_image_url = local_url
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
            time.sleep(2)
        else:
            print(f"No URL for {name}")
            
    db.session.commit()
print("Images mapped recursively through wiki API.")
