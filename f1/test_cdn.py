import requests

urls = {
    'Kimi': "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg/800px-Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg",
    'Arvid': "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Arvid_Lindblad_at_the_Red_Bull_Fan_Zone_%E2%80%93_Crown_Riverwalk%2C_Melbourne_%28028A7869%29_%28cropped%29.jpg/800px-Arvid_Lindblad_at_the_Red_Bull_Fan_Zone_%E2%80%93_Crown_Riverwalk%2C_Melbourne_%28028A7869%29_%28cropped%29.jpg",
    'Audi': "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Das_Audi_Forum_Ingolstadt.JPG/800px-Das_Audi_Forum_Ingolstadt.JPG",
    'Cadillac': "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cadillac_emblem.svg/512px-Cadillac_emblem.svg.png"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for name, url in urls.items():
    try:
        r = requests.get(url, headers=headers)
        print(f"{name}: {r.status_code} ({len(r.content)} bytes)")
        if r.status_code == 200:
            with open(f"static/images/{name.lower()}.jpg", "wb") as f:
                f.write(r.content)
    except Exception as e:
        print(f"{name}: Failed - {e}")

