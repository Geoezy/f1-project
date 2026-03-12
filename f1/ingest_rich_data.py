import pycountry
import pycountry
from extensions import db
from app import app
from models import Driver, Constructor

# ... (Keep imports)

# Comprehensive 2025 Grid Data
DRIVERS_DATA = {
    "verstappen": {"country_code": "nl", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png", "podiums": 99, "wins": 54},
    "perez": {"country_code": "mx", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png", "podiums": 35, "wins": 6},
    "hamilton": {"country_code": "gb", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png", "podiums": 197, "wins": 103},
    "russell": {"country_code": "gb", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png", "podiums": 11, "wins": 1},
    "leclerc": {"country_code": "mc", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png", "podiums": 30, "wins": 5},
    "sainz": {"country_code": "es", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png", "podiums": 18, "wins": 2},
    "norris": {"country_code": "gb", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png", "podiums": 13, "wins": 1},
    "piastri": {"country_code": "au", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/2col/image.png", "podiums": 2, "wins": 0},
    "alonso": {"country_code": "es", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png", "podiums": 106, "wins": 32},
    "stroll": {"country_code": "ca", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png", "podiums": 3, "wins": 0},
    "gasly": {"country_code": "fr", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png", "podiums": 4, "wins": 1},
    "ocon": {"country_code": "fr", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png", "podiums": 3, "wins": 1},
    "albon": {"country_code": "th", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png", "podiums": 2, "wins": 0},
    "sargeant": {"country_code": "us", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LOGSAR01_Logan_Sargeant/logsar01.png.transform/2col/image.png", "podiums": 0, "wins": 0},
    "tsunoda": {"country_code": "jp", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png", "podiums": 0, "wins": 0},
    "ricciardo": {"country_code": "au", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png", "podiums": 32, "wins": 8},
    "bottas": {"country_code": "fi", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png", "podiums": 67, "wins": 10},
    "zhou": {"country_code": "cn", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GUAZHO01_Guanyu_Zhou/guazho01.png.transform/2col/image.png", "podiums": 0, "wins": 0},
    "hulkenberg": {"country_code": "de", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png", "podiums": 0, "wins": 0},
    "magnussen": {"country_code": "dk", "image": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png", "podiums": 1, "wins": 0}
}
# Added 'bearman', 'antonelli', 'doohan' etc if needed for 2025 specific

TEAMS_DATA = {
    "red_bull": {"base": "Milton Keynes, UK", "principal": "Christian Horner", "sponsors": "Oracle, Bybit, Honda", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/red_bull_racing.png.transform/2col/image.png"},
    "mercedes": {"base": "Brackley, UK", "principal": "Toto Wolff", "sponsors": "Petronas, Ineos", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mercedes.png.transform/2col/image.png"},
    "ferrari": {"base": "Maranello, Italy", "principal": "Fred Vasseur", "sponsors": "Shell, Santander, HP", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/ferrari.png.transform/2col/image.png"},
    "mclaren": {"base": "Woking, UK", "principal": "Andrea Stella", "sponsors": "Google, OKX", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mclaren.png.transform/2col/image.png"},
    "aston_martin": {"base": "Silverstone, UK", "principal": "Mike Krack", "sponsors": "Aramco, Cognizant", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/aston_martin.png.transform/2col/image.png"},
    "alpine": {"base": "Enstone, UK", "principal": "Bruno Famin", "sponsors": "BWT, Castrol", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/alpine.png.transform/2col/image.png"},
    "williams": {"base": "Grove, UK", "principal": "James Vowles", "sponsors": "Komatsu, Gulf", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/williams.png.transform/2col/image.png"},
    "rb": {"base": "Faenza, Italy", "principal": "Laurent Mekies", "sponsors": "Visa, Cash App", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/rb.png.transform/2col/image.png"},
    "sauber": {"base": "Hinwil, Switzerland", "principal": "Alessandro Alunni Bravi", "sponsors": "Kick, Stake", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/kick_sauber.png.transform/2col/image.png"},
    "haas": {"base": "Kannapolis, USA", "principal": "Ayao Komatsu", "sponsors": "MoneyGram", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/haas.png.transform/2col/image.png"}
}

def ingest_rich_data():
    print("Ingesting Rich Data for 2025 Grid...")
    with app.app_context():
        # DRIVERS
        drivers = Driver.query.all()
        for d in drivers:
            # Match by surname (family_name) or name if ID is int
            # Our dictionary keys are lower case surnames mostly
            # If d.family_name exists use it, else try name splitting?
            # Lets try to match d.name which is "First Last" to keys
            # Or map integer IDs manually? No too many.
            # Assuming keys are 'verstappen', 'norris' etc.
            
            fullname = d.name.lower() # "max verstappen"
            found_key = None
            
            # Simple fuzzy match
            for k in DRIVERS_DATA.keys():
                if k in fullname:
                    found_key = k
                    break
            
            if found_key:
                data = DRIVERS_DATA[found_key]
            else:
                data = None
                # Fallback for image using official F1 URL pattern if possible, or placeholder
                # https://media.formula1.com/content/dam/fom-website/drivers/Firstname_Lastname/...
                pass
            
            if data:
                d.country_code = data.get('country_code')
                d.image_url = data.get('image')
                d.podiums = data.get('podiums')
                d.world_championships = data.get('world_championships')
                d.highest_finish = data.get('highest_finish')
                d.biography = data.get('biography')
            else:
                 # Generic fill
                 if not d.image_url:
                     d.image_url = "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/placeholder.png.transform/2col/image.png"
                 
                 try:
                     if d.nationality:
                         # Handle Gentilic (Canadian -> Canada)
                         # Simple map or try fuzzy
                         d.country_code = pycountry.countries.search_fuzzy(d.nationality)[0].alpha_2.lower()
                     else:
                         d.country_code = 'xx'
                 except Exception:
                     # Fallback
                     d.country_code = 'xx'
        
        teams = Constructor.query.all()
        if teams:
            print(f"Debug: Constructor attributes: {dir(teams[0])}")
        for t in teams:
            # Fuzzy match name
            fullname = t.name.lower()
            data = None
            found_key = None
            
            for k in TEAMS_DATA.keys():
                if k.replace('_', ' ') in fullname:
                    found_key = k
                    break
            
            if found_key:
                data = TEAMS_DATA[found_key]
            
            if data:
                t.base = data.get('base')
                t.team_principal = data.get('principal')
                t.car_image_url = data.get('car')
                t.sponsors = data.get('sponsors')
            else:
                if not t.car_image_url:
                    t.car_image_url = "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/placeholder.png.transform/2col/image.png"

        db.session.commit()
        print("Rich Data Ingested.")

if __name__ == "__main__":
    try:
        ingest_rich_data()
    except Exception as e:
        print(f"Error: {e}")
