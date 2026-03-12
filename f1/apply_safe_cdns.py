from app import app
from models import Driver, Constructor, db

def apply_safe_cdns():
    with app.app_context():
        # Pure CDN generic static files that don't block embedded images
        driver_images = {
            'Andrea Kimi Antonelli': 'https://cdn.racingnews365.com/Riders/Antonelli/_570x570_crop_center-center_none/f1_2024_aa_mer_base.png',
            'Arvid Lindblad': 'https://s3.eu-west-1.amazonaws.com/redbull-motorsports/drivers/Lindblad/Profile-Desktop.png'
        }
        
        team_images = {
            'Audi': 'https://cdn.motor1.com/images/mgl/p33mVP/s1/audi-f1-livery.jpg',
            'Cadillac F1 Team': 'https://cdn.motor1.com/images/mgl/LAAW6M/s1/andretti-cadillac-f1-entry.jpg',
            'Red Bull Racing': 'https://cdn.racingnews365.com/Cars/Red-Bull/_1024x576_crop_center-center_none/red-bull-rb20-1.jpg',
            'Aston Martin': 'https://cdn.racingnews365.com/Cars/Aston-Martin/_1024x576_crop_center-center_none/aston-martin-amr24.jpg'
        }
        
        for name, url in driver_images.items():
            d = Driver.query.filter_by(name=name).first()
            if d: d.image_url = url
                
        for name, url in team_images.items():
            c = Constructor.query.filter_by(name=name).first()
            if c: c.car_image_url = url
                
        db.session.commit()
        print("Restored stable Media CDN URLs to DB.")

if __name__ == "__main__":
    apply_safe_cdns()
