import os
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_workshop.decorators import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from .playlist import create_playlist, fetch_article_urls

class Omroepbrabant(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        # Het pad naar het icoon van de skill
        skill_icon_path = os.path.join(
            os.path.dirname(__file__),
            "res",
            "logo.svg"  # Verwijs naar je skill icoon
        )
        
        super().__init__(
            supported_media=[MediaType.NEWS],
            skill_icon=skill_icon_path,
            *args,
            **kwargs
        )
        LOG.info("Omroep Brabant skill geladen!")

    @ocp_search()
    def search_omroep_brabant(self, phrase: str, media_type: MediaType):
        """Zoekt naar de omroep Brabant playlist met nieuwsberichten."""
        if media_type == MediaType.NEWS:  # Controleer specifiek op MediaType.NEWS
            LOG.info(f"Zoeken naar: {phrase}")
            score = 100  # Stel de match confidence in op 100 omdat het een specifieke bron is

            # Haal de artikelen op
            articles_info = fetch_article_urls()

            # Maak de playlist op basis van de artikelen
            playlist_data = create_playlist(articles_info)

            # Converteer elk item in de playlist naar het vereiste formaat
            playlist_results = [
                {
                    "uri": track["uri"],
                    "title": track["title"],
                    "media_type": MediaType.NEWS,
                    "playback": PlaybackType.AUDIO,
                    "match_confidence": score,
                    "artist": "Omroep Brabant",
                    "album": "Omroep Brabant News",
                    "image": track["image"],  # Afbeelding van het artikel
                    "bg_image": track["bg_image"],  # Achtergrondafbeelding
                    "skill_icon": self.skill_icon,  # Icoon van de skill
                    "length": -1  # Zet op -1 voor live streams of onbekende lengte
                }
                for track in playlist_data["playlist"]
            ]

            # Retourneer de volledige playlist als één resultaat
            yield {
                "match_confidence": score,
                "media_type": MediaType.NEWS,
                "playlist": playlist_results,  # Gebruik een playlist in plaats van een uri
                "playback": PlaybackType.AUDIO,
                "image": self.skill_icon,  # Gebruik het skill-icoon als afbeelding
                "bg_image": self.skill_icon,  # Achtergrondafbeelding is ook het skill-icoon
                "skill_icon": self.skill_icon,  # Icoon van de skill
                "title": "Omroep Brabant Nieuws",
                "length": -1  # Zet de lengte op -1 als het een stream of variabele duur is
            }
