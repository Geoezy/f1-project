from app import app
from models import Constructor, db

team_data = {
    "Red Bull Racing": {
        "new_name": "Oracle Red Bull Racing",
        "base": "Milton Keynes, UK",
        "sponsors": "Oracle, BYBIT, Ford"
    },
    "Ferrari": {
        "new_name": "Scuderia Ferrari HP",
        "base": "Maranello, Italy",
        "sponsors": "HP, Shell, Santander"
    },
    "Mercedes": {
        "new_name": "Mercedes-AMG Petronas F1 Team",
        "base": "Brackley & Brixworth, UK",
        "sponsors": "Petronas, Microsoft, INEOS"
    },
    "McLaren": {
        "new_name": "McLaren Mastercard F1 Team",
        "base": "Woking, UK",
        "sponsors": "Mastercard, OKX, Google"
    },
    "Aston Martin": {
        "new_name": "Aston Martin Aramco Formula One Team",
        "base": "Silverstone, UK",
        "sponsors": "Aramco, Cognizant, Honda"
    },
    "Alpine": {
        "new_name": "BWT Alpine Formula One Team",
        "base": "Enstone, UK",
        "sponsors": "BWT, Castrol, Mercedes"
    },
    "Williams": {
        "new_name": "Atlassian Williams F1 Team",
        "base": "Grove, UK",
        "sponsors": "Atlassian, Komatsu, Duracell"
    },
    "RB": {
        "new_name": "Visa Cash App Racing Bulls",
        "base": "Faenza, Italy",
        "sponsors": "Visa, Cash App"
    },
    "Kick Sauber": {
        "new_name": "Stake Sauber / Audi Project",
        "base": "Hinwil, Switzerland",
        "sponsors": "Stake, Kick"
    },
    "Haas F1 Team": {
        "new_name": "TGR Haas F1 Team",
        "base": "Kannapolis, USA",
        "sponsors": "Toyota Gazoo Racing, MoneyGram"
    },
    "Audi": {
        "new_name": "Audi Revolut F1 Team",
        "base": "Hinwil, Switzerland",
        "sponsors": "Revolut, adidas, bp"
    },
    "Cadillac F1 Team": {
        "new_name": "Cadillac Formula 1 Team",
        "base": "Fishers, Indiana, USA",
        "sponsors": "Tommy Hilfiger, Jim Beam, Tenneco"
    }
}

def migrate():
    with app.app_context():
        for name, data in team_data.items():
            # Match by partial name
            team = Constructor.query.filter(Constructor.name.like(f"%{name}%")).first()
            if team:
                print(f"Updating Team: {team.name} -> {data['new_name']}")
                team.name = data['new_name']
                team.base = data['base']
                team.sponsors = data['sponsors']
            else:
                print(f"Team not found: {name}")
        
        db.session.commit()
        print("Team data migration completed successfully.")

if __name__ == "__main__":
    migrate()
