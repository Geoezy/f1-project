import urllib.request
import os
from app import app
from models import Driver, Constructor, db

def download_and_patch():
    # Target directory
    dest = os.path.join("static", "images", "assets")
    os.makedirs(dest, exist_ok=True)
    
    # URL list
    assets = {
        'Andrea Kimi Antonelli': ('https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg/800px-Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg', 'kimi.jpg', 'Driver'),
        'Arvid Lindblad': ('https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Arvid_Lindblad_in_2024.jpg/800px-Arvid_Lindblad_in_2024.jpg', 'arvid.jpg', 'Driver'),
        'Red Bull Racing': ('https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Red_Bull_Racing_RB20_Verstappen.jpeg/800px-Red_Bull_Racing_RB20_Verstappen.jpeg', 'redbull.jpg', 'Constructor'),
        'Aston Martin': ('https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Aston_Martin_AMR24_Alonso.jpeg/800px-Aston_Martin_AMR24_Alonso.jpeg', 'aston.jpg', 'Constructor'),
        'Audi': ('https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Audi-Logo_2016.svg/1024px-Audi-Logo_2016.svg.png', 'audi.png', 'Constructor'),
        'Cadillac F1 Team': ('https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/1200px-Cadillac_emblem.svg.png', 'cadillac.png', 'Constructor')
    }
    
    # Custom headers to bypass simple wikipedia blocks if any
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/100.0.0.0 Safari/537.36')]
    urllib.request.install_opener(opener)

    with app.app_context():
        for name, (url, filename, type_) in assets.items():
            filepath = os.path.join(dest, filename)
            try:
                urllib.request.urlretrieve(url, filepath)
                local_url = f"/static/images/assets/{filename}"
                
                if type_ == 'Driver':
                    d = Driver.query.filter_by(name=name).first()
                    if d:
                        d.image_url = local_url
                        print(f"Patched DB for {name} -> {local_url}")
                else:
                    c = Constructor.query.filter_by(name=name).first()
                    if c:
                        c.car_image_url = local_url
                        print(f"Patched DB for {name} -> {local_url}")
            except Exception as e:
                print(f"Failed to download {name}: {e}")
                
        db.session.commit()
    print("Download script complete.")

if __name__ == "__main__":
    download_and_patch()
