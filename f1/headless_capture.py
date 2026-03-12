from playwright.sync_api import sync_playwright
import os
from app import app
from models import Driver, Constructor, db

assets = {
    'Andrea Kimi Antonelli': ('https://upload.wikimedia.org/wikipedia/commons/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg', 'kimi.jpg', 'Driver'),
    'Arvid Lindblad': ('https://upload.wikimedia.org/wikipedia/commons/c/c5/Arvid_Lindblad_in_2024.jpg', 'arvid.jpg', 'Driver'),
    'Audi': ('https://upload.wikimedia.org/wikipedia/commons/b/ba/Audi_show_car.jpg', 'audi.jpg', 'Constructor'),
    'Cadillac F1 Team': ('https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/512px-Cadillac_emblem.svg.png', 'cadillac.png', 'Constructor'),
    'Red Bull Racing': ('https://upload.wikimedia.org/wikipedia/commons/e/e0/Red_Bull_Racing_RB20_Verstappen.jpeg', 'redbull.jpg', 'Constructor'),
    'Aston Martin': ('https://upload.wikimedia.org/wikipedia/commons/5/52/Aston_Martin_AMR24_Alonso.jpeg', 'aston.jpg', 'Constructor')
}

dest = "static/images/assets"
os.makedirs(dest, exist_ok=True)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate a real desktop
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        with app.app_context():
            for name, (url, filename, type_) in assets.items():
                print(f"Visiting {name} via Playwright...")
                try:
                    # Load the direct image URL. The browser will render it as a single <img>
                    page.goto(url, wait_until='networkidle')
                    # Snip the <img> element exactly to get a perfect clean file
                    img_element = page.locator("img")
                    img_element.screenshot(path=os.path.join(dest, filename))
                    
                    local_url = f"/static/images/assets/{filename}?v=3"
                    
                    if type_ == 'Driver':
                        d = Driver.query.filter_by(name=name).first()
                        if d: d.image_url = local_url
                    else:
                        c = Constructor.query.filter_by(name=name).first()
                        if c: c.car_image_url = local_url
                        
                    print(f"✅ Success: {filename}")
                except Exception as e:
                    print(f"❌ Failed {name}: {e}")
            
            db.session.commit()
            print("Finished capturing & patching images.")
        browser.close()

if __name__ == "__main__":
    run()
