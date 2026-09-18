import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_notification(title, url, budget, offers_count):
    if not WEBHOOK_URL:
        print("Erreur : URL Webhook Discord manquante dans les Secrets GitHub.")
        return
        
    payload = {
        "embeds": [
            {
                "title": f"🚨 Nouveau projet (< 10 offres) : {title}",
                "url": url,
                "color": 3066993,
                "fields": [
                    {"name": "Budget", "value": budget or "Non spécifié", "inline": True},
                    {"name": "Nombre d'offres", "value": str(offers_count), "inline": True}
                ],
                "footer": {"text": "Bot Codeur.com • GitHub Actions"}
            }
        ]
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Notification Discord envoyée pour : {title}")
    except Exception as e:
        print(f"Erreur d'envoi Discord : {e}")

def scrape_codeur():
    print("Démarrage du scraping...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.codeur.com/projets", timeout=60000)
        
        projects = page.query_selector_all(".project-list-item")
        print(f"{len(projects)} projets trouvés sur la page.")
        
        for project in projects:
            title_elem = project.query_selector(".project-title a")
            if not title_elem:
                continue
                
            title = title_elem.inner_text().strip()
            url = "https://www.codeur.com" + title_elem.get_attribute("href")
            
            offers_elem = project.query_selector(".project-offers-count")
            offers_text = offers_elem.inner_text().strip() if offers_elem else "0"
            
            # Extraction du nombre d'offres
            offers_count = int(''.join(filter(str.isdigit, offers_text)) or 0)
            
            budget_elem = project.query_selector(".project-budget")
            budget = budget_elem.inner_text().strip() if budget_elem else "Non spécifié"
            
            # CONDITION DE TEST DIRECT (envoie tout)
            if True:
                print(f"Projet retenu : {title} ({offers_count} offres)")
                send_discord_notification(title, url, budget, offers_count)
            else:
                print(f"Ignoré ({offers_count} offres) : {title}")
                
        browser.close()

if __name__ == "__main__":
    scrape_codeur()
