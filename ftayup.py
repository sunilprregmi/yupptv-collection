import requests
import json
from typing import Dict, List

def format_url(url: str) -> str:
    """Format URL to use CDN base if not already absolute."""
    if not url:
        return ""
    cdn_base = "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/"
    if url.startswith('http'):
        return url
    path = url.replace(',', '/')
    return cdn_base + path

def format_slug(slug: str) -> str:
    """Extract first part of slug."""
    return slug.split('/')[0]

def get_headers() -> Dict:
    """Return headers for API requests."""
    return {
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "box-id": "7c03c72952b44aa4",
        "sec-ch-ua-mobile": "?0",
        "session-id": "YT-f86ef4ba-57ab-4c06-8552-245abc2c6541",
        "tenant-code": "yuppfast",
        "origin": "https://www.yupptv.com",
        "referer": "https://www.yupptv.com/",
        "accept-language": "en-US,en;q=0.9"
    }

def fetch_channels(genre: str) -> List:
    """Fetch channel data for a specific genre from the API."""
    base_url = "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels"
    params = f"filter=genreCode:{genre};langCode:ENG,HIN,MAR,BEN,TEL,KAN,GUA,PUN,BHO,URD,ASS,TAM,MAL,ORI,NEP"
    url = f"{base_url}?{params}"
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()["response"]["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching channels for genre {genre}: {e}")
        return []

def fetch_and_save_new_data(output_file: str) -> bool:
    """Fetch new channel data and replace existing file with new data."""
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

    try:
        with open(output_file, 'w', encoding="utf-8") as f:
            json.dump(new_format, f, indent=2)
        print(f"Successfully replaced old data with new data in {output_file}")
        return True
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")
        return False

if __name__ == "__main__":
    output_file = 'yupp-fta.json'
    success = fetch_and_save_new_data(output_file)
    exit(0 if success else 1)
