from app import app
from models import Constructor, db

def use_official_urls():
    with app.app_context():
        # Audi (ID 11)
        audi = Constructor.query.get(11)
        if audi:
            print(f"Updating Audi to official URL...")
            audi.car_image_url = "https://media.formula1.com/image/upload/c_lfill,w_3392/q_auto/v1740000001/common/f1/2026/audi/2026audicarright.webp"
        
        # Cadillac (ID 12)
        cadillac = Constructor.query.get(12)
        if cadillac:
            print(f"Updating Cadillac to official URL...")
            cadillac.car_image_url = "https://media.formula1.com/image/upload/c_lfill,w_3392/q_auto/v1740000001/common/f1/2026/cadillac/2026cadillaccarright.webp"
            
        db.session.commit()
        print("Official URLs applied.")

if __name__ == "__main__":
    use_official_urls()
