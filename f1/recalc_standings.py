from app import app, db, Race, Result, DriverStanding, ConstructorStanding

def recalculate_standings():
    print("Recalculating Standings for 2020-2026...")
    with app.app_context():
        # Clear existing standings? Or just upsert?
        # Safer to clear for now to avoid duplicates if ID logic is weak
        DriverStanding.query.delete()
        ConstructorStanding.query.delete()
        db.session.commit()
        
        for season in range(2020, 2027):
            print(f"Propcessing Season {season}...")
            
            # 1. Driver Standings
            # Get all results for this season
            # Group by driver_id
            
            # Sqlalchemy aggregate
            from sqlalchemy import func
            driver_stats = db.session.query(
                Result.driver_id,
                func.sum(Result.points).label('total_points'),
                func.count(Result.id).filter(Result.position == 1).label('wins')
            ).join(Race).filter(Race.season == season).group_by(Result.driver_id).all()
            
            # Rank them
            driver_stats.sort(key=lambda x: x.total_points, reverse=True)
            
            for rank, (driver_id, points, wins) in enumerate(driver_stats, 1):
                ds = DriverStanding(
                    season=season,
                    driver_id=driver_id,
                    points=points,
                    position=rank,
                    wins=wins
                )
                db.session.add(ds)
                
            # 2. Constructor Standings
            const_stats = db.session.query(
                Result.constructor_id,
                func.sum(Result.points).label('total_points'),
                func.count(Result.id).filter(Result.position == 1).label('wins')
            ).join(Race).filter(Race.season == season).group_by(Result.constructor_id).all()
            
            const_stats.sort(key=lambda x: x.total_points, reverse=True)
            
            for rank, (const_id, points, wins) in enumerate(const_stats, 1):
                cs = ConstructorStanding(
                    season=season,
                    constructor_id=const_id,
                    points=points,
                    position=rank,
                    wins=wins
                )
                db.session.add(cs)
            
            db.session.commit()
            print(f"Updated {len(driver_stats)} drivers and {len(const_stats)} teams for {season}.")

if __name__ == "__main__":
    recalculate_standings()
