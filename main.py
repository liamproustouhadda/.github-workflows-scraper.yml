import os
import requests
import xml.etree.ElementTree as ET

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord(title, link, description):
    if not WEBHOOK_URL:
        print("Erreur : Secret DISCORD_WEBHOOK_URL non trouvé dans GitHub Secrets.")
        return
        
    payload = {
        "embeds": [{
            "title": f"🚨 Nouveau projet : {title}",
            "url": link,
            "description": description[:200] + "..." if len(description) > 200 else description,
            "color": 3066993,
            "footer": {"text": "Bot Codeur.com • Test RSS"}
        }]
    }
    r = requests.post(WEBHOOK_URL, json=payload)
    print(f"Statut Discord : {r.status_code}")

def main():
    print("Vérification des projets via le flux RSS...")
    rss_url = "https://www.codeur.com/projets.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(rss_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur HTTP : {response.status_code}")
        return

    root = ET.fromstring(response.content)
    items = root.findall("./channel/item")
    print(f"{len(items)} projets trouvés.")

    # Envoie les 3 derniers projets pour le test
    for item in items[:3]:
        title = item.find("title").text if item.find("title") is not None else "Sans titre"
        link = item.find("link").text if item.find("link") is not None else ""
        desc = item.find("description").text if item.find("description") is not None else ""
        send_discord(title, link, desc)

if __name__ == "__main__":
    main()
