import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# Récupération de l'URL Webhook Discord depuis GitHub Secrets
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 🎯 LISTE DE MOTS-CLÉS (laissez vide [] si vous voulez tout recevoir)
KEYWORDS = ["wordpress", "python", "design", "react", "shopify", "seo", "mobile"]

def matches_keywords(text):
    if not KEYWORDS:
        return True
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)

def send_discord(title, link, description):
    if not WEBHOOK_URL:
        print("Erreur : Secret DISCORD_WEBHOOK_URL non trouvé dans GitHub Secrets.")
        return
    
    # Nettoyage du titre pour générer les liens de recherche
    search_query = quote(title.replace("🚨", "").strip())
    
    google_search = f"https://www.google.com/search?q={search_query}"
    linkedin_search = f"https://www.linkedin.com/search/results/all/?keywords={search_query}"
    facebook_search = f"https://www.facebook.com/search/top?q={search_query}"
    instagram_search = f"https://www.google.com/search?q=site:instagram.com+{search_query}"
    tiktok_search = f"https://www.google.com/search?q=site:tiktok.com+{search_query}"
    snapchat_search = f"https://www.google.com/search?q=site:snapchat.com+{search_query}"

    payload = {
        "embeds": [{
            "title": f"🚨 Nouveau projet : {title}",
            "url": link,
            "description": description[:250] + "..." if len(description) > 250 else description,
            "color": 3066993,
            "fields": [
                {
                    "name": "🔍 Chercher le client sur les réseaux",
                    "value": (
                        f"🌐 [Google]({google_search}) • "
                        f"💼 [LinkedIn]({linkedin_search}) • "
                        f"📘 [Facebook]({facebook_search})\n"
                        f"📸 [Instagram]({instagram_search}) • "
                        f"🎵 [TikTok]({tiktok_search}) • "
                        f"👻 [Snapchat]({snapchat_search})"
                    ),
                    "inline": False
                }
            ],
            "footer": {"text": "Bot Codeur.com • Discord Alerts"}
        }]
    }
    
    r = requests.post(WEBHOOK_URL, json=payload)
    print(f"Statut envoi Discord : {r.status_code}")

def main():
    print("Vérification des projets sur Codeur.com via RSS...")
    rss_url = "https://www.codeur.com/projets.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(rss_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur HTTP : {response.status_code}")
        return

    root = ET.fromstring(response.content)
    items = root.findall("./channel/item")
    print(f"{len(items)} projets trouvés au total.")

    count = 0
    for item in items:
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        desc = item.find("description").text if item.find("description") is not None else ""
        
        full_text = f"{title} {desc}"
        if matches_keywords(full_text):
            print(f"Projet retenu : {title}")
            send_discord(title, link, desc)
            count += 1
            if count >= 3:
                break

if __name__ == "__main__":
    main()
