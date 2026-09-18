import os
import smtplib
import requests
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

# Identifiants Gmail récupérés depuis GitHub Secrets
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")

# 🎯 VOTRE LISTE DE MOTS-CLÉS (en minuscules)
KEYWORDS = ["wordpress", "python", "design", "react", "shopify", "seo", "mobile"]

def matches_keywords(text):
    if not KEYWORDS:
        return True
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)

def send_gmail(title, link, description):
    if not GMAIL_USER or not GMAIL_PASS:
        print("Erreur : Secrets GMAIL_USER ou GMAIL_PASS manquants.")
        return

    # Liens de recherche rapide du client
    search_query = quote(title.replace("🚨", "").strip())
    google_search = f"https://www.google.com/search?q={search_query}"
    linkedin_search = f"https://www.linkedin.com/search/results/all/?keywords={search_query}"
    facebook_search = f"https://www.facebook.com/search/top?q={search_query}"

    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"🚨 Nouveau projet : {title}"
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2b569a;">🚨 Nouveau projet trouvé sur Codeur.com</h2>
        <p><strong>Titre :</strong> <a href="{link}" style="font-size: 16px; font-weight: bold;">{title}</a></p>
        <p><strong>Description :</strong> {description}</p>
        <hr style="border: 0; border-top: 1px solid #eee;">
        <h3>🔍 Rechercher le client sur les réseaux :</h3>
        <p>
          🌐 <a href="{google_search}">Google</a> | 
          💼 <a href="{linkedin_search}">LinkedIn</a> | 
          📘 <a href="{facebook_search}">Facebook</a>
        </p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        server.close()
        print(f"E-mail envoyé avec succès pour : {title}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

def main():
    print("Vérification des projets...")
    rss_url = "https://www.codeur.com/projets.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(rss_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur HTTP : {response.status_code}")
        return

    root = ET.fromstring(response.content)
    items = root.findall("./channel/item")

    count = 0
    for item in items:
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        desc = item.find("description").text if item.find("description") is not None else ""
        
        full_text = f"{title} {desc}"
        if matches_keywords(full_text):
            send_gmail(title, link, desc)
            count += 1
            if count >= 3:
                break

if __name__ == "__main__":
    main()
