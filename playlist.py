import requests
from ovos_utils.ocp import MediaType, PlaybackType
import os

# De URL voor de Omroep Brabant API
feed_url = "https://api.omroepbrabant.nl/api/page/v2/home"

def fetch_article_urls():
    try:
        # Haal de gegevens op van de API
        response = requests.get(feed_url)
        response.raise_for_status()  # Controleer of de aanvraag succesvol was
        data = response.json()  # Zet de JSON om naar een Python-dict

        # Selecteer de eerste 3 "featured" artikelen
        featured_articles = [(article["externalId"], article["title"]) for article in data["articles"][:3]]

        # Selecteer de eerste 2 artikelen uit de "popular_articles" in de "sidebar"
        sidebar_section = next((section for section in data["sidebar"] if section["type"] == "popular_articles"), None)
        popular_articles = [(article["externalId"], article["title"]) for article in sidebar_section["articles"][:2]] if sidebar_section else []

        # Combineer de lijsten
        selected_articles = featured_articles + popular_articles

        return selected_articles  # Geeft een lijst met geselecteerde artikelen

    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return []  # Retourneer een lege lijst bij een fout
    except KeyError as e:
        print("Key error:", e)
        return []  # Retourneer een lege lijst bij een key error

def fetch_tts_url(article_url):
    try:
        # Haal de gegevens op van een specifiek artikel
        response = requests.get(article_url)
        response.raise_for_status()  # Controleer of de aanvraag succesvol was
        data = response.json()  # Zet de JSON om naar een Python-dict

        # Haal de TTS URL op uit het artikel
        return data['article'].get('ttsUrl')  # Geef de TTS URL terug als deze bestaat

    except requests.exceptions.RequestException as e:
        print("Error fetching article data:", e)
        return None  # Retourneer None bij een fout
    except KeyError as e:
        print("Key error:", e)
        return None  # Retourneer None bij een key error

def create_playlist(articles_info):
    results = []

    # Gebruik het pad naar logo.svg als standaardafbeelding en icoon
    default_image = os.path.join(os.path.dirname(__file__), "res", "logo.svg")  # Volledig pad naar logo.svg
    default_icon = default_image  # Hetzelfde icoon als de afbeelding gebruiken

    # Maak een afspeellijst met TTS URL's voor elk artikel
    for external_id, title in articles_info:
        article_url = f"https://api.omroepbrabant.nl/api/article/{external_id}"
        tts_url = fetch_tts_url(article_url)
        if tts_url:
            # Voeg een nieuw artikel toe aan de playlist
            results.append({
                "uri": tts_url,
                "title": title,
                "media_type": MediaType.NEWS,  # Het mediatype is NEWS
                "playback": PlaybackType.AUDIO,   # Het afspeeltype is AUDIO
                "match_confidence": 100,  # Maximale overeenkomst
                "artist": "Omroep Brabant",
                "album": "Omroep Brabant Nieuws",
                "image": default_image,  # Gebruik de standaardafbeelding
                "bg_image": default_image,  # Gebruik dezelfde afbeelding voor de achtergrond
                "skill_icon": default_icon  # Gebruik het standaardicoon
            })
        else:
            print(f"Skipping article '{title}' due to missing TTS URL.")  # Indien geen TTS URL beschikbaar is, sla het artikel over

    return {
        "match_confidence": 100,  # Totale overeenkomst voor de playlist
        "media_type": MediaType.NEWS,  # Het mediatype is NEWS
        "playlist": results,  # De lijst van nieuwsitems
        "playback": PlaybackType.AUDIO,  # Het afspeeltype is AUDIO
        "title": "Omroep Brabant Nieuws",  # Titel van de playlist
        "length": -1  # Zet de lengte op -1 omdat dit een dynamische nieuwsplaylist is
    }
