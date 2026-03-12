import requests

def test_url(url):
    try:
        r = requests.head(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        return r.status_code == 200
    except:
        return False

# Real CDN links from motorsport news sites 
urls = {
    'Andrea Kimi Antonelli': 'https://cdn.racingnews365.com/Riders/Antonelli/_570x570_crop_center-center_none/f1_2024_aa_mer_base.png',
    'Arvid Lindblad': 'https://s3.eu-west-1.amazonaws.com/redbull-motorsports/drivers/Lindblad/Profile-Desktop.png',
    'Audi': 'https://cdn.motor1.com/images/mgl/p33mVP/s1/audi-f1-livery.jpg',
    'Cadillac F1 Team': 'https://cdn.motor1.com/images/mgl/LAAW6M/s1/andretti-cadillac-f1-entry.jpg',
    'Red Bull Racing': 'https://cdn.racingnews365.com/Cars/Red-Bull/_1024x576_crop_center-center_none/red-bull-rb20-1.jpg',
    'Aston Martin': 'https://cdn.racingnews365.com/Cars/Aston-Martin/_1024x576_crop_center-center_none/aston-martin-amr24.jpg'
}

for name, url in urls.items():
    print(f"{name}: {'OK' if test_url(url) else 'FAILED'} - {url}")

