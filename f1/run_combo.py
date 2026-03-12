import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def get_wiki_thumb(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=800"
    r = requests.get(url, headers=headers).json()
    pages = r["query"]["pages"]
    for page_id in pages:
        if "thumbnail" in pages[page_id]:
            return pages[page_id]["thumbnail"]["source"]
    return None

def dl_img(url, filename):
    r = requests.get(url, headers=headers)
    print(f"{filename}: Status {r.status_code}, length {len(r.content)}")
    if r.status_code == 200:
        with open(f"static/images/assets/{filename}", "wb") as f:
            f.write(r.content)

kimi_url = get_wiki_thumb("Andrea_Kimi_Antonelli")
if kimi_url: dl_img(kimi_url, "kimi.jpg")
else: print("Kimi URL not found via API")

arvid_url = get_wiki_thumb("Arvid_Lindblad")
if arvid_url: dl_img(arvid_url, "arvid.jpg")
else: print("Arvid URL not found via API")

