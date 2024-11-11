import os
import requests
from ovos_utils.ocp import MediaType, PlaybackType

feed_url = "https://api.omroepbrabant.nl/api/page/v2/home"

def fetch_article_urls():
    try:
        response = requests.get(feed_url)
        response.raise_for_status()
        data = response.json()
        
        featured_articles = [(article["externalId"], article["title"]) for article in data["articles"][:3]]
        
        sidebar_section = next((section for section in data["sidebar"] if section["type"] == "popular_articles"), None)
        popular_articles = [(article["externalId"], article["title"]) for article in sidebar_section["articles"][:2]] if sidebar_section else []
        
        selected_articles = featured_articles + popular_articles
        return selected_articles

    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return []
    except KeyError as e:
        print("Key error:", e)
        return []

def fetch_tts_url(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        data = response.json()
        
        return data['article'].get('ttsUrl')

    except requests.exceptions.RequestException as e:
        print("Error fetching article data:", e)
        return None
    except KeyError as e:
        print("Key error:", e)
        return None

def create_playlist(articles_info):
    results = []
    
    # Gebruik de `logo.svg` afbeelding als standaard
    default_image = os.path.join(os.path.dirname(__file__), "res", "logo.png")  # Gebruik de PNG als albumafbeelding
    default_icon = os.path.join(os.path.dirname(__file__), "res", "logo.svg")  # SVG blijft als skill-icoon

    for external_id, title in articles_info:
        article_url = f"https://api.omroepbrabant.nl/api/article/{external_id}"
        tts_url = fetch_tts_url(article_url)
        if tts_url:
            results.append({
                "uri": tts_url,
                "title": title,
                "media_type": MediaType.NEWS,
                "playback": PlaybackType.AUDIO,
                "match_confidence": 100,
                "artist": "Omroep Brabant",
                "album": "Omroep Brabant Nieuws",
                "image": default_image,
                "bg_image": default_image,
                "skill_icon": default_icon
            })
        else:
            print(f"Skipping article '{title}' due to missing TTS URL.")

    return {
        "match_confidence": 100,
        "media_type": MediaType.NEWS,
        "playlist": results,
        "playback": PlaybackType.AUDIO,
        "title": "Omroep Brabant Nieuws",
        "length": -1
    }
