import requests

urls = [
    # Red Bull
    "https://media.formula1.com/image/upload/f_auto,c_limit,w_1361,q_auto/f_auto/q_auto/fom-website/2024/Red%20Bull/2024-Car-Launch/F1%20Car%20launch%202024%20-%20Red%20Bull%204",
    # Aston Martin
    "https://media.formula1.com/image/upload/f_auto,c_limit,w_1361,q_auto/f_auto/q_auto/fom-website/2024/Aston%20Martin/Aston%20Martin%20Car%20Launch%202024%205",
    # Kimi
    "https://media.formula1.com/image/upload/f_auto,c_limit,w_960,q_auto/f_auto/q_auto/content/dam/fom-website/drivers/2024Classes/Antonelli",
    "https://media.formula1.com/image/upload/v1725091465/fom-website/2024/Mercedes/Antonelli-Mercedes-Monza-2024.jpg",
    # Arvid
    "https://media.formula1.com/image/upload/v1722606554/fom-website/2024/F3/F3_2024_Arvid_Lindblad_Portrait_helmet.jpg",
    # Cadillac
    "https://media.formula1.com/image/upload/v1732551469/fom-website/2024/Miscellaneous/Andretti-Cadillac-announcement-header.jpg",
    # Audi
    "https://media.formula1.com/image/upload/v1661499529/fom-website/2022/Audi%20announcement/Audi%20F1%20Car.jpg"
]

for url in urls:
    r = requests.head(url)
    print(f"{r.status_code} - {url}")

