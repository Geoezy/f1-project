import requests
url = "https://upload.wikimedia.org/wikipedia/commons/4/4e/Andrea_Kimi_Antonelli_Monza_2024_%28cropped%29.jpg"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}
r = requests.get(url, headers=headers)
print("Status:", r.status_code)
print("Len:", len(r.content))
with open('static/images/assets/kimi.jpg', 'wb') as f:
    f.write(r.content)
