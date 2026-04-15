from app import app, db
from models import Driver, Constructor, Race
import requests
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_wiki_image(search_term):
    # Try querying wiki API directly
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={search_term}&prop=pageimages&format=json&pithumbsize=800"
    try:
        r = requests.get(url, headers=headers, timeout=5).json()
        pages = r.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
             if "thumbnail" in page_data:
                 return page_data["thumbnail"]["source"]
        
        # If not found directly by name, try searching first
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={search_term}&utf8=&format=json&srlimit=1"
        s = requests.get(search_url, headers=headers, timeout=5).json()
        search_results = s.get("query", {}).get("search", [])
        if search_results:
             title = search_results[0]["title"]
             url2 = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=800"
             r2 = requests.get(url2, headers=headers, timeout=5).json()
             pages2 = r2.get("query", {}).get("pages", {})
             for page_id2, page_data2 in pages2.items():
                 if "thumbnail" in page_data2:
                     return page_data2["thumbnail"]["source"]
    except Exception as e:
        return None
    return None

def fill_images():
    with app.app_context():
        # Drivers
        drivers = Driver.query.all()
        for d in drivers:
            if not d.image_url or "fallback" in d.image_url or "placeholder" in d.image_url:
                print(f"Fetching image for Driver: {d.name}")
                img = get_wiki_image(d.name + " racing driver")
                if not img:
                    img = get_wiki_image(d.name)
                
                if img:
                    d.image_url = img
                    print(f" -> Found: {img}")
                else:
                    print(f" -> Not found")
                time.sleep(0.5)
        
        # Circuits
        races = Race.query.all()
        for r in races:
            if not r.circuit_image_url or "fallback" in r.circuit_image_url or "placeholder" in r.circuit_image_url:
                print(f"Fetching image for Circuit: {r.circuit_name}")
                img = get_wiki_image(r.circuit_name + " circuit map")
                if not img:
                    img = get_wiki_image(r.circuit_name)
                    
                if img:
                    # Update all races with this circuit name to avoid repeated calls
                    similar_races = Race.query.filter_by(circuit_name=r.circuit_name).all()
                    for sr in similar_races:
                         sr.circuit_image_url = img
                    print(f" -> Found: {img}")
                else:
                    print(f" -> Not found")
                time.sleep(0.5)
        
        db.session.commit()
        print("Images updated")

if __name__ == '__main__':
    fill_images()
