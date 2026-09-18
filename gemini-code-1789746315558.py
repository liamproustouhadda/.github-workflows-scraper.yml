import os
import requests
from playwright.sync_api import sync_playwright

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
CODEUR_URL = "https://www.codeur.com/projets"
MAX_OFFRES = 10

def envoyer_notification_discord(titre, lien, nb_offres, description):
    embed = {
        "title": f"🚨 Nouveau projet (< {MAX_OFFRES} offres)",
        "description": f"**[{titre}]({lien})**\n\n{description[:250]}...",
        "color": 3066993,
        "fields": [
            {"name": "Offres actuelles", "value": str(nb_offres), "inline": True},
            {"name": "Lien", "value": f"[Postuler ici]({lien})", "inline": True}
        ]
    }
    requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})

def analyser_projets():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(CODEUR_URL, wait_until="domcontentloaded")

        projets = page.query_selector_all(".project-list-item, article.project")

        for projet in projets:
            lien_elem = projet.query_selector("h2 a, a.project-title")
            if not lien_elem:
                continue
            
            titre = lien_elem.inner_text().strip()
            href = lien_elem.get_attribute("href")
            lien = f"https://www.codeur.com{href}" if href.startswith("/") else href

            offres_elem = projet.query_selector(".offers-count, .project-offers")
            nb_offres = 0
            if offres_elem:
                texte_offres = offres_elem.inner_text().strip()
                chiffres = [int(s) for s in texte_offres.split() if s.isdigit()]
                if chiffres:
                    nb_offres = chiffres[0]

            desc_elem = projet.query_selector(".project-description, p")
            description = desc_elem.inner_text().strip() if desc_elem else ""

            if nb_offres < MAX_OFFRES:
                envoyer_notification_discord(titre, lien, nb_offres, description)

        browser.close()

if __name__ == "__main__":
    analyser_projets()