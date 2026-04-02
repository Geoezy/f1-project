import requests
import time
from app import app, db
from models import Driver, Constructor

urls = {
    'rimi.jpg': ('Driver', 'Kimi Antonelli', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Andrea_Kimi_Antonelli_driving_the_Mercedes_W15_at_the_2024_Italian_Grand_Prix_%281%29_%28cropped%29.jpg/800px-Andrea_Kimi_Antonelli_driving_the_Mercedes_W15_at_the_2024_Italian_Grand_Prix_%281%29_%28cropped%29.jpg'),
    'audi_new.png': ('Team', 'Audi', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Audi_logo.svg/800px-Audi_logo.svg.png'),
    'cadillac_new.png': ('Team', 'Cadillac', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Cadillac.svg/800px-Cadillac.svg.png')
}

with app.app_context():
    for filename, (type_, name_frag, url) in urls.items():
        print(f"Downloading {filename}...")
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            filepath = f"static/images/assets/{filename}"
            with open(filepath, 'wb') as f:
                f.write(r.content)
            
            local_url = f"/{filepath}?v={int(time.time())}"
            print(f"Saved {filepath}, updating DB to {local_url}")
            
            if type_ == 'Driver':
                d = Driver.query.filter(Driver.name.ilike(f'%kimi%')).first()
                if d:
                    d.image_url = local_url
            else:
                t = Constructor.query.filter(Constructor.name.ilike(f'%{name_frag}%')).first()
                if t:
                    t.car_image_url = local_url
        else:
            print(f"Failed to download {url}: {r.status_code}")
    db.session.commit()
    print("Done")
