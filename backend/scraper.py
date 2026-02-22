import re
import requests
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


def get_session():
    s = cloudscraper.create_scraper()
    s.headers.update(HEADERS)
    return s


def fetch(url):
    session = get_session()
    print(f"  Fetching: {url}")
    r = session.get(url, timeout=20)
    print(f"  Status: {r.status_code}, Length: {len(r.text)}")
    return r


def get_first_link(item, base_url):
    link_el = item.select_one("a[href]")
    if link_el:
        href = link_el.get("href", "")
        if href and href != "#":
            if href.startswith("http"):
                return href
            return urljoin(base_url, href)
    return ""


def scrape_inmobiliaria(nombre, web, regiones, precio_max=None):
    nombre_lower = nombre.lower().strip()

    scrapers = {
        "pisos.com": scrape_pisos_com,
        "fotocasa": scrape_fotocasa,
        "idealista": scrape_idealista,
        "habitaclia": scrape_habitaclia,
        "redpiso": scrape_redpiso,
        "donpiso": scrape_donpiso,
        "solvia": scrape_solvia,
        "tecnocasa": scrape_tecnocasa,
        "servihabitat": scrape_generic,
        "haya": scrape_generic,
        "aliseda": scrape_generic,
        "altamira": scrape_generic,
        "remax": scrape_generic,
        "re/max": scrape_generic,
        "century": scrape_generic,
        "engel": scrape_generic,
    }

    scraper_fn = scrape_generic
    for key, fn in scrapers.items():
        if key in nombre_lower:
            scraper_fn = fn
            break

    if precio_max:
        print(f"[{nombre}] Iniciando scraping (precio max: {precio_max})...")
    else:
        print(f"[{nombre}] Iniciando scraping...")
    resultados = scraper_fn(nombre, web, regiones, precio_max=precio_max)
    return filter_by_price(resultados, precio_max)


def check_elevator(text):
    if not text:
        return "NO"
    text_lower = text.lower()
    if "ascensor" in text_lower:
        if "sin ascensor" in text_lower or "no ascensor" in text_lower:
            return "NO"
        return "SI"
    return "NO"


def parse_property_from_text(text):
    habitaciones = ""
    hab_match = re.search(r'(\d+)\s*hab', text.lower())
    if hab_match:
        habitaciones = hab_match.group(1)

    banos = ""
    ban_match = re.search(r'(\d+)\s*baño', text.lower())
    if ban_match:
        banos = ban_match.group(1)

    ascensor = check_elevator(text)
    return habitaciones, banos, ascensor


def extract_price(text):
    match = re.search(r'[\d.,]+\s*€', text)
    return match.group(0).strip() if match else ""


def parse_price_number(precio_str):
    if not precio_str:
        return None
    cleaned = re.sub(r'[^\d]', '', precio_str)
    if cleaned:
        return int(cleaned)
    return None


def filter_by_price(resultados, precio_max):
    if not precio_max:
        return resultados
    filtered = []
    for r in resultados:
        num = parse_price_number(r.get("precio", ""))
        if num is None or num <= precio_max:
            filtered.append(r)
    before = len(resultados)
    after = len(filtered)
    if before != after:
        print(f"  Filtro precio (<= {precio_max}): {before} -> {after} resultados")
    return filtered


# ---------------------------------------------------------------------------
# PISOS.COM  (verified working with requests)
# ---------------------------------------------------------------------------
def scrape_pisos_com(nombre, base_url, regiones, precio_max=None):
    resultados = []
    for region in regiones:
        region_slug = region.lower().replace(" ", "-")
        if precio_max:
            url = f"{base_url}/venta/pisos-{region_slug}/0-{precio_max}/"
        else:
            url = f"{base_url}/venta/pisos-{region_slug}/"
        print(f"[Pisos.com] Scraping {region}...")
        try:
            r = fetch(url)
            if r.status_code != 200:
                print(f"[Pisos.com] Status {r.status_code} para {region}")
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select(".ad-preview")[:30]
            print(f"[Pisos.com] Encontrados {len(items)} anuncios en {region}")

            for item in items:
                try:
                    price_el = item.select_one("[class*=price]")
                    precio = price_el.get_text(strip=True) if price_el else ""

                    title_el = item.select_one("[class*=title]")
                    descripcion = title_el.get_text(strip=True) if title_el else ""

                    link = get_first_link(item, base_url)

                    text = item.get_text(" ", strip=True)
                    habitaciones, banos, ascensor = parse_property_from_text(text)

                    if precio or descripcion:
                        resultados.append({
                            "precio": precio,
                            "descripcion": descripcion[:500],
                            "link": link,
                            "habitaciones": habitaciones,
                            "banos": banos,
                            "ascensor": ascensor,
                            "region": region,
                        })
                except Exception as e:
                    print(f"[Pisos.com] Error item: {e}")
        except Exception as e:
            print(f"[Pisos.com] Error {region}: {e}")
    return resultados


# ---------------------------------------------------------------------------
# FOTOCASA  (verified working with requests, articles have data in text)
# ---------------------------------------------------------------------------
def scrape_fotocasa(nombre, base_url, regiones, precio_max=None):
    resultados = []
    for region in regiones:
        region_slug = region.lower().replace(" ", "-")
        url = f"{base_url}/es/comprar/viviendas/{region_slug}-provincia/todas-las-zonas/l"
        if precio_max:
            url += f"?maxPrice={precio_max}"
        print(f"[Fotocasa] Scraping {region}...")
        try:
            r = fetch(url)
            if r.status_code != 200:
                print(f"[Fotocasa] Status {r.status_code} para {region}")
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.select("article")[:30]
            print(f"[Fotocasa] Encontrados {len(articles)} articles en {region}")

            for art in articles:
                try:
                    text = art.get_text(" ", strip=True)
                    if len(text) < 20:
                        continue

                    precio = extract_price(text)

                    title_el = art.select_one("[class*=itle], h3, h2")
                    descripcion = title_el.get_text(strip=True) if title_el else ""
                    if not descripcion:
                        desc_match = re.search(r'(?:en|Calle|Avenida|Plaza|Paseo)\s+.{10,80}', text)
                        if desc_match:
                            descripcion = desc_match.group(0)

                    link = get_first_link(art, base_url)

                    habitaciones, banos, ascensor = parse_property_from_text(text)

                    if precio or descripcion:
                        resultados.append({
                            "precio": precio,
                            "descripcion": descripcion[:500],
                            "link": link,
                            "habitaciones": habitaciones,
                            "banos": banos,
                            "ascensor": ascensor,
                            "region": region,
                        })
                except Exception as e:
                    print(f"[Fotocasa] Error item: {e}")
        except Exception as e:
            print(f"[Fotocasa] Error {region}: {e}")
    return resultados


# ---------------------------------------------------------------------------
# IDEALISTA  (uses Playwright to bypass Cloudflare)
# ---------------------------------------------------------------------------
def scrape_idealista(nombre, base_url, regiones, precio_max=None):
    resultados = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[Idealista] Playwright no instalado. Ejecuta: pip install playwright && python -m playwright install chromium")
        return resultados

    print("[Idealista] Usando Playwright para evitar protección anti-bot...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="es-ES",
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            for region in regiones:
                region_slug = region.lower().replace(" ", "-")
                if precio_max:
                    urls_to_try = [
                        f"{base_url}/venta-viviendas/{region_slug}-provincia/con-precio-hasta_{precio_max}/",
                        f"{base_url}/venta-viviendas/{region_slug}/con-precio-hasta_{precio_max}/",
                    ]
                else:
                    urls_to_try = [
                        f"{base_url}/venta-viviendas/{region_slug}-provincia/",
                        f"{base_url}/venta-viviendas/{region_slug}/",
                    ]
                print(f"[Idealista] Scraping {region}...")
                for url in urls_to_try:
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(6000)

                        html = page.content()
                        if len(html) < 5000:
                            print(f"[Idealista] Página muy corta ({len(html)}), posible bloqueo")
                            continue

                        soup = BeautifulSoup(html, "html.parser")
                        items = soup.select("article.item, article")[:30]
                        print(f"[Idealista] Encontrados {len(items)} items en {region}")

                        if not items:
                            continue

                        for item in items:
                            try:
                                price_el = item.select_one(".item-price, [class*=price]")
                                precio = price_el.get_text(strip=True) if price_el else ""

                                desc_el = item.select_one(".item-description, [class*=title]")
                                descripcion = desc_el.get_text(strip=True) if desc_el else ""

                                link_el = item.select_one("a.item-link, a[href*='/inmueble/']")
                                link = ""
                                if link_el:
                                    href = link_el.get("href", "")
                                    link = urljoin(base_url, href) if href else ""
                                if not link:
                                    link = get_first_link(item, base_url)

                                text = item.get_text(" ", strip=True)
                                habitaciones, banos, ascensor = parse_property_from_text(text)

                                if precio or descripcion:
                                    resultados.append({
                                        "precio": precio,
                                        "descripcion": descripcion[:500],
                                        "link": link,
                                        "habitaciones": habitaciones,
                                        "banos": banos,
                                        "ascensor": ascensor,
                                        "region": region,
                                    })
                            except Exception as e:
                                print(f"[Idealista] Error item: {e}")
                        if resultados:
                            break
                    except Exception as e:
                        print(f"[Idealista] Error URL {url}: {e}")

            browser.close()
    except Exception as e:
        print(f"[Idealista] Error Playwright: {e}")

    return resultados


# ---------------------------------------------------------------------------
# HABITACLIA  (verified URL pattern: viviendas-{region}.htm)
# ---------------------------------------------------------------------------
def scrape_habitaclia(nombre, base_url, regiones, precio_max=None):
    resultados = []
    for region in regiones:
        region_slug = region.lower().replace(" ", "-")
        price_param = f"?maxp={precio_max}" if precio_max else ""
        urls_to_try = [
            f"{base_url}/comprar-{region_slug}.htm{price_param}",
            f"{base_url}/viviendas-{region_slug}.htm{price_param}",
            f"{base_url}/pisos-{region_slug}.htm{price_param}",
        ]
        print(f"[Habitaclia] Scraping {region}...")
        for url in urls_to_try:
            try:
                r = fetch(url)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                items = soup.select("article, [class*=list-item], [class*=Card]")[:30]
                print(f"[Habitaclia] Encontrados {len(items)} items en {region}")

                for item in items:
                    try:
                        text = item.get_text(" ", strip=True)
                        if len(text) < 15:
                            continue

                        price_el = item.select_one("[class*=price]")
                        precio = price_el.get_text(strip=True) if price_el else extract_price(text)

                        title_el = item.select_one("[class*=title], h3, a")
                        descripcion = title_el.get_text(strip=True) if title_el else ""

                        link = get_first_link(item, base_url)

                        habitaciones, banos, ascensor = parse_property_from_text(text)

                        if precio or descripcion:
                            resultados.append({
                                "precio": precio,
                                "descripcion": descripcion[:500],
                                "link": link,
                                "habitaciones": habitaciones,
                                "banos": banos,
                                "ascensor": ascensor,
                                "region": region,
                            })
                    except Exception as e:
                        print(f"[Habitaclia] Error item: {e}")
                if resultados:
                    break
            except Exception as e:
                print(f"[Habitaclia] Error {region}: {e}")
    return resultados


# ---------------------------------------------------------------------------
# REDPISO
# ---------------------------------------------------------------------------
def scrape_redpiso(nombre, base_url, regiones, precio_max=None):
    resultados = []
    for region in regiones:
        region_slug = region.lower().replace(" ", "-")
        urls_to_try = [
            f"{base_url}/venta/pisos/{region_slug}",
            f"{base_url}/venta-pisos/{region_slug}",
        ]
        print(f"[Redpiso] Scraping {region}...")
        for url in urls_to_try:
            try:
                r = fetch(url)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                items = soup.select("article, [class*=card], [class*=Card], [class*=property], [class*=listing], [class*=result]")[:30]
                print(f"[Redpiso] Encontrados {len(items)} items en {region}")

                for item in items:
                    try:
                        text = item.get_text(" ", strip=True)
                        if len(text) < 15:
                            continue

                        price_el = item.select_one("[class*=price], [class*=precio]")
                        precio = price_el.get_text(strip=True) if price_el else extract_price(text)

                        title_el = item.select_one("[class*=title], [class*=direccion], h2, h3, a")
                        descripcion = title_el.get_text(strip=True) if title_el else ""

                        link = get_first_link(item, base_url)

                        habitaciones, banos, ascensor = parse_property_from_text(text)

                        if precio or descripcion:
                            resultados.append({
                                "precio": precio,
                                "descripcion": descripcion[:500],
                                "link": link,
                                "habitaciones": habitaciones,
                                "banos": banos,
                                "ascensor": ascensor,
                                "region": region,
                            })
                    except Exception as e:
                        print(f"[Redpiso] Error item: {e}")
                if resultados:
                    break
            except Exception as e:
                print(f"[Redpiso] Error {region}: {e}")
    return resultados


# ---------------------------------------------------------------------------
# DONPISO
# ---------------------------------------------------------------------------
def scrape_donpiso(nombre, base_url, regiones, precio_max=None):
    return scrape_generic(nombre, base_url, regiones, precio_max=precio_max)


# ---------------------------------------------------------------------------
# SOLVIA
# ---------------------------------------------------------------------------
def scrape_solvia(nombre, base_url, regiones, precio_max=None):
    return scrape_generic(nombre, base_url, regiones, precio_max=precio_max)


# ---------------------------------------------------------------------------
# TECNOCASA
# ---------------------------------------------------------------------------
def scrape_tecnocasa(nombre, base_url, regiones, precio_max=None):
    return scrape_generic(nombre, base_url, regiones, precio_max=precio_max)


# ---------------------------------------------------------------------------
# GENERIC FALLBACK (requests + cloudscraper, multiple URL patterns)
# ---------------------------------------------------------------------------
def scrape_generic(nombre, base_url, regiones, precio_max=None):
    resultados = []
    for region in regiones:
        region_slug = region.lower().replace(" ", "-")
        possible_urls = [
            f"{base_url}/venta/viviendas/{region_slug}/",
            f"{base_url}/venta/pisos/{region_slug}/",
            f"{base_url}/comprar/{region_slug}/",
            f"{base_url}/viviendas/{region_slug}/",
            f"{base_url}/inmuebles/{region_slug}/",
            f"{base_url}/es/comprar/viviendas/{region_slug}/",
            f"{base_url}/venta-viviendas/{region_slug}/",
            f"{base_url}/es/venta/viviendas/{region_slug}/",
        ]

        print(f"[{nombre}] Scraping {region}...")
        found = False
        for url in possible_urls:
            try:
                r = fetch(url)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                items = soup.select(
                    "article, [class*=property-card], [class*=listing-item], "
                    "[class*=card], [class*=Card], "
                    "[class*=property], [class*=listing], "
                    "[class*=result], [class*=Result], "
                    "[class*=anunci]"
                )[:30]

                if not items:
                    continue

                print(f"[{nombre}] Encontrados {len(items)} items en {url}")

                for item in items:
                    try:
                        text = item.get_text(" ", strip=True)
                        if len(text) < 15:
                            continue

                        price_el = item.select_one("[class*=price], [class*=Price], [class*=precio], [class*=amount]")
                        precio = price_el.get_text(strip=True) if price_el else extract_price(text)

                        title_el = item.select_one("[class*=title], [class*=Title], [class*=description], h2, h3, a")
                        descripcion = title_el.get_text(strip=True) if title_el else ""

                        link = get_first_link(item, base_url)

                        habitaciones, banos, ascensor = parse_property_from_text(text)

                        if precio or descripcion:
                            resultados.append({
                                "precio": precio,
                                "descripcion": descripcion[:500],
                                "link": link,
                                "habitaciones": habitaciones,
                                "banos": banos,
                                "ascensor": ascensor,
                                "region": region,
                            })
                    except Exception as e:
                        print(f"[{nombre}] Error item: {e}")

                if resultados:
                    found = True
                    break
            except Exception as e:
                print(f"[{nombre}] Error {url}: {e}")

        if not found:
            print(f"[{nombre}] No se encontraron resultados para {region}. "
                  "El sitio puede requerir JavaScript o tener protección anti-bot.")

    return resultados
