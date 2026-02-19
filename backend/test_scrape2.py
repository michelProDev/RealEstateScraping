import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Fotocasa deeper analysis
print("=== FOTOCASA DEEP ===")
r = requests.get("https://www.fotocasa.es/es/comprar/viviendas/murcia-provincia/todas-las-zonas/l", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
articles = soup.select("article")[:2]
for i, art in enumerate(articles):
    print(f"\n--- Article {i} ---")
    price = art.select_one("[class*=rice]")
    print(f"PRICE: {price.get_text(strip=True) if price else 'NONE'}")
    title = art.select_one("[class*=itle], h3, h2")
    print(f"TITLE: {title.get_text(strip=True)[:120] if title else 'NONE'}")
    img = art.select_one("img")
    if img:
        print(f"IMG: {(img.get('src') or img.get('data-src') or '')[:100]}")
    text = art.get_text(" ", strip=True)[:300]
    print(f"TEXT: {text}")
    # Show all class names in article
    all_classes = set()
    for el in art.select("[class]"):
        for c in el.get("class", []):
            all_classes.add(c)
    print(f"CLASSES: {sorted(all_classes)[:20]}")

# Test more sites
print("\n\n=== TECNOCASA ===")
tec_urls = [
    "https://www.tecnocasa.es/venta/viviendas/murcia.html",
    "https://www.tecnocasa.es/venta/pisos/murcia.html",
    "https://www.tecnocasa.es/venta/inmueble/murcia.html",
]
for url in tec_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"  {url} -> {r.status_code}")
        if r.status_code == 200:
            s = BeautifulSoup(r.text, "html.parser")
            cards = s.select("[class*=card], [class*=Card], article, [class*=property], [class*=inmueble]")
            print(f"    Cards found: {len(cards)}")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")

print("\n\n=== REMAX ===")
rem_urls = [
    "https://www.remax.es/publiclistinglist.aspx#/q/Murcia",
    "https://www.remax.es/inmuebles-venta-murcia",
]
for url in rem_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"  {url} -> {r.status_code} (len={len(r.text)})")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")

print("\n\n=== REDPISO ===")
red_urls = [
    "https://www.redpiso.es/venta-pisos/murcia",
    "https://www.redpiso.es/pisos-venta/murcia",
    "https://www.redpiso.es/venta/pisos/murcia",
]
for url in red_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"  {url} -> {r.status_code} (len={len(r.text)})")
        if r.status_code == 200:
            s = BeautifulSoup(r.text, "html.parser")
            cards = s.select("article, [class*=card], [class*=Card], [class*=property]")
            print(f"    Cards found: {len(cards)}")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")

print("\n\n=== HABITACLIA ===")
hab_urls = [
    "https://www.habitaclia.com/viviendas-murcia.htm",
    "https://www.habitaclia.com/comprar-murcia.htm",
    "https://www.habitaclia.com/pisos-murcia.htm",
    "https://www.habitaclia.com/comprar/pisos-murcia.htm",
]
for url in hab_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"  {url} -> {r.status_code}")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")
