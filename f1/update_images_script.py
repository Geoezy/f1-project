from app import app
from models import db, Driver, Constructor
import requests

def update_missing_images():
    with app.app_context():
        # Map driver surname to Wikipedia page to extract standard thumbnail image if possible,
        # or just hard-code the missing 2025 rookie/transfer F1 site URLs.
        
        # F1 CDN Images (Approximate structures for missing drivers)
        missing_drivers = {
            "bearman": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png.transform/2col/image.png",
            "antonelli": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/K/KIMANT01_Kimi_Antonelli/kimant01.png.transform/2col/image.png",
            "doohan": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/J/JACDOO01_Jack_Doohan/jacdoo01.png.transform/2col/image.png",
            "hadjar": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/I/ISAHAD01_Isack_Hadjar/isahad01.png.transform/2col/image.png",
            "colapinto": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/F/FRACOL01_Franco_Colapinto/fracol01.png.transform/2col/image.png",
            "lawson": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png.transform/2col/image.png",
            "bortoleto": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png.transform/2col/image.png"
        }
        
        missing_teams = {
            "kick sauber": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/kick_sauber.png.transform/2col/image.png",
            "rb": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/rb.png.transform/2col/image.png"
        }

        drivers = Driver.query.all()
        for d in drivers:
            fullname = d.name.lower()
            for key, url in missing_drivers.items():
                if key in fullname:
                    d.image_url = url
                    print(f"Updated Image for Driver: {d.name}")
                    
        teams = Constructor.query.all()
        for t in teams:
            tname = t.name.lower()
            for key, url in missing_teams.items():
                if key in tname:
                    t.car_image_url = url
                    print(f"Updated Image for Constructor: {t.name}")
                    
        db.session.commit()
        print("Done updating images.")
        
if __name__ == "__main__":
    update_missing_images()
