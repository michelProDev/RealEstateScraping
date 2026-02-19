import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Habitaclia
print("=== HABITACLIA ===")
r = requests.get("https://www.habitaclia.com/viviendas-murcia.htm", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
print(f"Status: {r.status_code}")
for sel in ["article", "[class*=card]", "[class*=Card]", "[class*=list-item]", "[class*=property]", "[class*=anunci]", "section", ".list-item"]:
    found = soup.select(sel)
    if found:
        print(f"  '{sel}': {len(found)} items")
        if len(found) < 40:
            for f in found[:2]:
                text = f.get_text(" ", strip=True)[:150]
                print(f"    -> {text}")

# Redpiso
print("\n=== REDPISO ===")
r = requests.get("https://www.redpiso.es/venta/pisos/murcia", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
print(f"Status: {r.status_code}")
for sel in ["article", "[class*=card]", "[class*=Card]", "[class*=list]", "[class*=property]", "[class*=anunci]", "[class*=result]", "[class*=piso]", "[class*=inmueble]", ".item", "[class*=ficha]"]:
    found = soup.select(sel)
    if found:
        print(f"  '{sel}': {len(found)} items")
        if len(found) < 20:
            for f in found[:2]:
                text = f.get_text(" ", strip=True)[:150]
                classes = f.get("class", [])
                print(f"    classes={classes}")
                print(f"    -> {text}")

# Idealista with cloudscraper
print("\n=== IDEALISTA (trying requests session) ===")
s = requests.Session()
s.headers.update(HEADERS)
s.headers["Referer"] = "https://www.google.com/"
r = s.get("https://www.idealista.com/venta-viviendas/murcia-provincia/", timeout=15)
print(f"Status: {r.status_code}, len={len(r.text)}")
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("article.item, article")
    print(f"Articles: {len(items)}")
