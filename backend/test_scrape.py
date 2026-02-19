import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Test pisos.com
print("=== PISOS.COM ===")
r = requests.get("https://www.pisos.com/venta/pisos-murcia/", headers=HEADERS, timeout=15)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.text, "html.parser")
items = soup.select(".ad-preview")[:3]
print(f"Items found: {len(items)}")
for i, item in enumerate(items):
    price = item.select_one("[class*=price]")
    title = item.select_one("[class*=title]")
    img = item.select_one("img")
    img_src = ""
    if img:
        img_src = img.get("src") or img.get("data-src") or img.get("data-lazy") or ""
    text = item.get_text(" ", strip=True)
    print(f"\n--- Item {i} ---")
    print(f"PRICE: {price.get_text(strip=True) if price else 'NONE'}")
    print(f"TITLE: {title.get_text(strip=True)[:120] if title else 'NONE'}")
    print(f"IMG: {img_src[:100]}")
    print(f"TEXT (first 200): {text[:200]}")

# Test fotocasa
print("\n\n=== FOTOCASA ===")
r2 = requests.get("https://www.fotocasa.es/es/comprar/viviendas/murcia-provincia/todas-las-zonas/l", headers=HEADERS, timeout=15)
print(f"Status: {r2.status_code}, Length: {len(r2.text)}")
soup2 = BeautifulSoup(r2.text, "html.parser")
# Check what elements exist
for sel in ["article", "[class*=card]", "[class*=Card]", "[class*=property]", "[class*=listing]", "[class*=result]", "[class*=annonce]"]:
    found = soup2.select(sel)
    if found:
        print(f"  Selector '{sel}': {len(found)} items")

# Test habitaclia with different URLs
print("\n\n=== HABITACLIA ===")
hab_urls = [
    "https://www.habitaclia.com/comprar/vivienda-en-murcia.htm",
    "https://www.habitaclia.com/comprar-murcia.htm",
    "https://www.habitaclia.com/viviendas-en-murcia.htm",
]
for url in hab_urls:
    try:
        r3 = requests.get(url, headers=HEADERS, timeout=10)
        print(f"  {url} -> {r3.status_code}")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")

# Test donpiso
print("\n\n=== DONPISO ===")
don_urls = [
    "https://www.donpiso.com/venta/viviendas/murcia/",
    "https://www.donpiso.com/comprar/murcia/",
    "https://www.donpiso.com/venta/pisos/murcia/",
]
for url in don_urls:
    try:
        r4 = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"  {url} -> {r4.status_code} (len={len(r4.text)})")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")

# Test solvia
print("\n\n=== SOLVIA ===")
sol_urls = [
    "https://www.solvia.es/es/venta/viviendas/murcia/",
    "https://www.solvia.es/venta/viviendas/murcia/",
]
for url in sol_urls:
    try:
        r5 = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"  {url} -> {r5.status_code} (len={len(r5.text)})")
    except Exception as e:
        print(f"  {url} -> ERROR: {e}")
