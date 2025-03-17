import json
import requests
from typing import Dict, List

def format_url(url):
    if not url:
        return ""
    cdn_base = "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/"
    if url.startswith('http'):
        return url
    path = url.replace(',', '/')
    return cdn_base + path

def format_slug(slug):
    # Just return the first part of the slug
    return slug.split('/')[0]

def get_headers() -> Dict:
    return {
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "box-id": "6daaea02854e441e",
        "sec-ch-ua-mobile": "?0",
        "session-id": "YT-583a47b7-b3b5-468e-953d-23991fb85a92",
        "tenant-code": "yuppfast",
        "origin": "https://www.yupptv.com",
        "referer": "https://www.yupptv.com/",
        "accept-language": "en-US,en;q=0.9"
    }

def fetch_channels(genre: str) -> List:
    base_url = "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels"
    params = f"filter=genreCode:{genre};langCode:ENG,HIN,MAR,BEN,TEL,KAN,GUA,PUN,BHO,URD,ASS,TAM,MAL,ORI,NEP"
    url = f"{base_url}?{params}"
    
    response = requests.get(url, headers=get_headers())
    return response.json()["response"]["data"]

def convert_json_format(output_file):
    genres = ["news", "entertainment", "music", "kids", 
              "spiritual", "movies", "lifestyle", "sports", 
              "educational", "others"]
    
    new_format = {"feeds": []}
    
    for index, genre in enumerate(genres, 1):
        category = {
            "category_id": index,
            "category_name": genre.title(),
            "category_slug": genre,
            "category_description": f"{genre.title()} Category",
            "category_priority": index,
            "channels": []
        }
        
        channels_data = fetch_channels(genre)
        for channel in channels_data:
            slug = channel["target"].get("path", channel["target"].get("slug", ""))
            new_channel = {
                "channel_id": channel["id"],
                "channel_number": channel["target"]["pageAttributes"]["remoteChannelId"],
                "channel_country": "IN",
                "channel_category": genre.title(),
                "channel_name": channel["display"]["title"],
                "channel_slug": format_slug(slug),
                "channel_logo": format_url(channel["display"]["imageUrl"]),
                "channel_poster": format_url(channel["display"]["loadingImageUrl"])
            }
            category["channels"].append(new_channel)
        
        new_format["feeds"].append(category)

    with open(output_file, 'w') as f:
        json.dump(new_format, f, indent=2)

if __name__ == "__main__":
    output_file = 'yupp-fta.json'
    convert_json_format(output_file)
