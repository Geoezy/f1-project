import urllib.request
import json
import re

def get_image(query):
    # Using generic public searches or looking at wikipedia pages text to find raw urls
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={urllib.parse.quote(query)}&format=json&pithumbsize=1024"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        pages = data['query']['pages']
        for page_id in pages:
            if 'thumbnail' in pages[page_id]:
                return pages[page_id]['thumbnail']['source']
    except Exception as e:
        print(e)
    return None

import urllib.parse
print("Kimi:", get_image("Andrea_Kimi_Antonelli"))
print("Arvid:", get_image("Arvid_Lindblad"))
print("Audi:", get_image("Audi"))
print("Cadillac:", get_image("Cadillac"))
