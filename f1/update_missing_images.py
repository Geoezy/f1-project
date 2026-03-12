from app import app
from models import Driver, Constructor, db

def fix_images():
    with app.app_context():
        driver_images = {
            'Sergio Pérez': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png',
            'Nico Hülkenberg': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png',
            'Sebastian Vettel': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/S/SEBVET01_Sebastian_Vettel/sebvet01.png.transform/2col/image.png',
            'Kimi Räikkönen': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/K/KIMRAI01_Kimi_R%C3%A4ikk%C3%B6nen/kimrai01.png.transform/2col/image.png',
            'Mick Schumacher': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MICSCH02_Mick_Schumacher/micsch02.png.transform/2col/image.png',
            'Nikita Mazepin': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NIKMAZ01_Nikita_Mazepin/nikmaz01.png.transform/2col/image.png',
            'Antonio Giovinazzi': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ANTGIO01_Antonio_Giovinazzi/antgio01.png.transform/2col/image.png',
            'Nyck de Vries': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NYCDEV01_Nyck_De%20Vries/nycdev01.png.transform/2col/image.png',
            'Nicholas Latifi': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICLAT01_Nicholas_Latifi/niclat01.png.transform/2col/image.png',
            'Daniil Kvyat': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/D/DANKVY01_Daniil_Kvyat/dankvy01.png.transform/2col/image.png',
            'Romain Grosjean': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/R/ROMGRO01_Romain_Grosjean/romgro01.png.transform/2col/image.png',
            'Robert Kubica': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/R/ROBKUB01_Robert_Kubica/robkub01.png.transform/2col/image.png',
            'Arvid Lindblad': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/placeholder.png.transform/2col/image.png',
            'Jack Aitken': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/J/JACAIT01_Jack_Aitken/jacait01.png.transform/2col/image.png',
            'Pietro Fittipaldi': 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/P/PIEFIT01_Pietro_Fittipaldi/piefit01.png.transform/2col/image.png'
        }
        
        constructor_images = {
            'Alfa Romeo': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/alfa-romeo.png.transform/2col/image.png',
            'AlphaTauri': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/alphatauri.png.transform/2col/image.png',
            'Racing Point': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/racing-point.png.transform/2col/image.png',
            'Renault': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/renault.png.transform/2col/image.png',
            'Audi': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/placeholder.png.transform/2col/image.png',
            'Cadillac F1 Team': 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/placeholder.png.transform/2col/image.png'
        }

        for name, url in driver_images.items():
            driver = Driver.query.filter_by(name=name).first()
            if driver:
                driver.image_url = url
                
        for name, url in constructor_images.items():
            cons = Constructor.query.filter_by(name=name).first()
            if cons:
                cons.car_image_url = url
                
        db.session.commit()
        print("Updated missing images.")

if __name__ == "__main__":
    fix_images()
