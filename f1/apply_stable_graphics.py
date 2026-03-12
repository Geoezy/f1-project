from app import app
from models import Driver, Constructor, db

def apply_stable_graphics():
    with app.app_context():
        # High-res logos routed securely through Google's Favicon renderer
        team_images = {
            'Red Bull Racing': 'https://www.google.com/s2/favicons?domain=redbullracing.com&sz=256',
            'Aston Martin': 'https://www.google.com/s2/favicons?domain=astonmartinf1.com&sz=256',
            'Audi': 'https://www.google.com/s2/favicons?domain=audi.com&sz=256',
            'Cadillac F1 Team': 'https://www.google.com/s2/favicons?domain=cadillac.com&sz=256'
        }
        
        # Professional dynamic profile initials using exact team hex colors
        driver_images = {
            'Andrea Kimi Antonelli': 'https://ui-avatars.com/api/?name=Kimi+Antonelli&background=27F4D2&color=000&size=512&font-size=0.33', # Mercedes Teal
            'Arvid Lindblad': 'https://ui-avatars.com/api/?name=Arvid+Lindblad&background=0600EF&color=fff&size=512&font-size=0.33' # RedBull Blue
        }
        
        for name, url in driver_images.items():
            driver = Driver.query.filter_by(name=name).first()
            if driver:
                driver.image_url = url
                
        for name, url in team_images.items():
            team = Constructor.query.filter_by(name=name).first()
            if team:
                team.car_image_url = url
                
        db.session.commit()
        print("Stable, unblockable generated graphics applied to database.")

if __name__ == "__main__":
    apply_stable_graphics()
