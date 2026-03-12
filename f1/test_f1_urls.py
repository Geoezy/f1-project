import requests

urls = {
    'RedBull': "https://media.formula1.com/image/upload/f_auto,c_limit,w_1361,q_auto/f_auto/q_auto/fom-website/2024/Red%20Bull/2024-Car-Launch/F1%20Car%20launch%202024%20-%20Red%20Bull%204",
    'Aston': "https://media.formula1.com/image/upload/f_auto,c_limit,w_1361,q_auto/f_auto/q_auto/fom-website/2024/Aston%20Martin/Aston%20Martin%20Car%20Launch%202024%205",
    'Kimi': "https://media.formula1.com/image/upload/f_auto,c_limit,q_auto,w_1320/content/dam/fom-website/drivers/2024Classes/Antonelli",
    'Arvid': "https://media.formula1.com/image/upload/f_auto,c_limit,q_auto,w_1320/content/dam/fom-website/drivers/2024Classes/Lindblad",
    'Cadillac': "https://media.formula1.com/image/upload/v1732549241/fom-website/2024/Miscellaneous/Andretti-Cadillac-announcement-header.jpg",
    'Audi': "https://media.formula1.com/image/upload/v1661499529/fom-website/2022/Audi%20announcement/Audi%20F1%20Car.jpg"
}

headers = {"User-Agent": "Mozilla/5.0"}
for name, url in urls.items():
    try:
        r = requests.head(url, headers=headers, allow_redirects=True)
        print(f"{name}: {r.status_code}")
    except Exception as e:
        print(f"{name}: Failed - {e}")
