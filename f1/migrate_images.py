from app import app
from models import Driver, Constructor, db

updates = {
    "drivers": [
        {"name": "Sergio%P%rez", "url": "https://media.formula1.com/image/upload/c_lfill,w_3392/q_auto/v1740000001/fom-website/manual/Misc/Driver%20Of%20The%20Day/2024/Perez.webp"},
        {"name": "Max Verstappen", "url": "https://media.formula1.com/image/upload/t_16by9North/c_lfill,w_3392/q_auto/v1740000001/trackside-images/2025/F1_Grand_Prix_of_Abu_Dhabi/2250531225.webp"},
        {"name": "Carlos Sainz", "url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png"},
        {"name": "Gabriel Bortoleto", "url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png.transform/2col/image.png"},
        {"name": "Valtteri Bottas", "url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png"},
        {"name": "Nico Hülkenberg", "url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png"},
    ],
    "teams": [
        {"name": "Audi", "url": "/static/images/assets/audi_2026.png"},
        {"name": "Cadillac F1 Team", "url": "/static/images/assets/cadillac_2026.png"}
    ]
}

def migrate():
    with app.app_context():
        # Update Drivers
        for d_update in updates["drivers"]:
            drivers = Driver.query.filter(Driver.name.like(f"%{d_update['name']}%")).all()
            if drivers:
                for driver in drivers:
                    print(f"Updating Driver: {driver.name} (ID: {driver.id}) -> {d_update['url']}")
                    driver.image_url = d_update['url']
            else:
                print(f"Driver not found: {d_update['name']}")
        
        # Update Teams
        for t_update in updates["teams"]:
            team = Constructor.query.filter(Constructor.name.like(f"%{t_update['name']}%")).first()
            if team:
                print(f"Updating Team: {team.name} -> {t_update['url']}")
                team.car_image_url = t_update['url']
            else:
                print(f"Team not found: {t_update['name']}")
        
        db.session.commit()
        print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
