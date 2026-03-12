from app import app
from models import Driver, Constructor, db

def fix_rookies():
    with app.app_context():
        # Arvid Lindblad F3/F2 photo
        d = Driver.query.filter_by(name='Arvid Lindblad').first()
        if d:
            d.image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Arvid_Lindblad_in_2024.jpg/800px-Arvid_Lindblad_in_2024.jpg'
            
        # Audi logo
        audi = Constructor.query.filter_by(name='Audi').first()
        if audi:
            audi.car_image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Audi-Logo_2016.svg/1024px-Audi-Logo_2016.svg.png'
            
        # Cadillac logo
        cad = Constructor.query.filter_by(name='Cadillac F1 Team').first()
        if cad:
            cad.car_image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/1200px-Cadillac_emblem.svg.png'
            
        db.session.commit()
        print("Updated Rookies.")

if __name__ == "__main__":
    fix_rookies()
