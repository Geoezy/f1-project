import requests

def get_wiki_image(wiki_url):
    try:
        if not wiki_url:
            return None
            
        # Extract title from URL
        # Format: http://en.wikipedia.org/wiki/Bahrain_International_Circuit
        # or https://en.wikipedia.org/wiki/Bahrain_International_Circuit
        title = wiki_url.split("/")[-1]
        
        api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "pageimages",
            "format": "json",
            "piprop": "original",
            "titles": title
        }
        
        headers = {
            "User-Agent": "F1DataApp/1.0 (contact@example.com)"
        }
        
        print(f"Fetching image for {title}...")
        response = requests.get(api_url, params=params, headers=headers)
        data = response.json()
        
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            for page_id in pages:
                # Page ID -1 means missing
                if int(page_id) > 0 and 'original' in pages[page_id]:
                    return pages[page_id]['original']['source']
                
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test with Bahrain and a few others
    print("Bahrain:", get_wiki_image("http://en.wikipedia.org/wiki/Bahrain_International_Circuit"))
    print("Monaco:", get_wiki_image("http://en.wikipedia.org/wiki/Circuit_de_Monaco"))
    print("Silverstone:", get_wiki_image("http://en.wikipedia.org/wiki/Silverstone_Circuit"))
