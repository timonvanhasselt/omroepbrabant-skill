import os
from ovos_utils.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_utils.parse import fuzzy_match
from ovos_workshop.decorators import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from .playlist import create_playlist, fetch_article_urls

class OmroepBrabant(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        # Verwijs naar het logo als skill icoon
        skill_icon_path = os.path.join(
            os.path.dirname(__file__),
            "res",
            "logo.svg"
        )
        
        super().__init__(
            supported_media=[MediaType.NEWS],
            skill_icon=skill_icon_path,
            *args,
            **kwargs
        )
        LOG.info("Omroep Brabant skill geladen!")

    @ocp_featured_media()
    def featured_media(self):
        """Standaard 'featured' artikelen als fallback."""
        articles_info = fetch_article_urls()
        playlist_data = create_playlist(articles_info)

        return [
            {
                "match_confidence": 80,
                "media_type": MediaType.NEWS,
                "uri": track["uri"],
                "playback": PlaybackType.AUDIO,
                "image": track["image"],
                "bg_image": track["bg_image"],
                "skill_icon": self.skill_icon,
                "title": track["title"],
                "artist": "Omroep Brabant",
                "album": "Omroep Brabant Nieuws",
                "length": -1
            }
            for track in playlist_data["playlist"]
        ]

    @ocp_search()
    def search_omroep_brabant(self, phrase: str, media_type: MediaType):
        """Zoekt naar Omroep Brabant nieuwsberichten."""
        base_score = 0
    
        # Score verhogen voor specifieke vermelding van Omroep Brabant of Brabant nieuws
        if "brabant" in phrase.lower() or "omroep brabant" in phrase.lower():
            base_score += 40
        else:
            base_score -= 50
    
        if "nieuws" in phrase.lower():
            base_score += 10
    
        LOG.info(f"Zoeken naar: {phrase}")
        score_threshold = 50
    
        # Haal artikelen op en maak de playlist
        articles_info = fetch_article_urls()
        playlist_data = create_playlist(articles_info)
        LOG.info(f"Fetched {len(articles_info)} articles")
        LOG.info(f"Created playlist with {len(playlist_data['playlist'])} items")
    
        playlist_results = []
        for track in playlist_data["playlist"]:
            title_match_score = fuzzy_match(track["title"].lower(), phrase.lower()) * 100
            score = round(base_score + title_match_score)
            LOG.info(f"Matching '{phrase}' with '{track['title']}' - Score: {score}")
    
            if score < score_threshold:
                LOG.info(f"Skipping '{track['title']}' due to low score")
                continue
    
            playlist_results.append({
                "uri": track["uri"],
                "title": track["title"],
                "media_type": MediaType.NEWS,
                "playback": PlaybackType.AUDIO,
                "match_confidence": 100,
                "artist": "Omroep Brabant",
                "album": "Omroep Brabant Nieuws",
                "image": track["image"],
                "bg_image": track["bg_image"],
                "skill_icon": self.skill_icon,
                "length": -1
            })
    
        if playlist_results:
            yield {
                "match_confidence": 100,
                "media_type": MediaType.NEWS,
                "playlist": playlist_results,
                "playback": PlaybackType.AUDIO,
                "image": self.skill_icon,
                "bg_image": self.skill_icon,
                "skill_icon": self.skill_icon,
                "title": "Omroep Brabant Nieuws",
                "length": -1
            }
        else:
            LOG.info("Geen resultaten gevonden voor Omroep Brabant.")
