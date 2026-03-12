from app import app
from models import Driver, Constructor, db

def apply_wiki_urls():
    with app.app_context():
        # Clean URLs directly to the browser
        driver_images = {
            'Andrea Kimi Antonelli': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg/800px-Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg',
            'Arvid Lindblad': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Arvid_Lindblad_in_2024.jpg/800px-Arvid_Lindblad_in_2024.jpg'
        }
        
        team_images = {
            'Audi': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Das_Audi_Forum_Ingolstadt.JPG/800px-Das_Audi_Forum_Ingolstadt.JPG',
            'Cadillac F1 Team': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/512px-Cadillac_emblem.svg.png'
        }
        
        for name, url in driver_images.items():
            d = Driver.query.filter_by(name=name).first()
            if d: d.image_url = url
                
        for name, url in team_images.items():
            c = Constructor.query.filter_by(name=name).first()
            if c: c.car_image_url = url
                
        db.session.commit()
        print("Restored direct Wikipedia URLs to DB.")

if __name__ == "__main__":
    apply_wiki_urls()
def add_more_teams():
    with app.app_context():
        # Clean URLs directly to the browser
        team_images = {
            'Red Bull Racing': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Red_Bull_Racing_RB20_Verstappen.jpeg/800px-Red_Bull_Racing_RB20_Verstappen.jpeg',
            'Aston Martin': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Aston_Martin_AMR24_Alonso.jpeg/800px-Aston_Martin_AMR24_Alonso.jpeg'
        }
        for name, url in team_images.items():
            c = Constructor.query.filter_by(name=name).first()
            if c: c.car_image_url = url
        db.session.commit()

if __name__ == "__main__":
    add_more_teams()
