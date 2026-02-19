from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="es-ES",
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()

    # Remove webdriver flag
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    url = "https://www.idealista.com/venta-viviendas/murcia-provincia/"
    print(f"Navigating to {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    
    # Wait for Cloudflare challenge to resolve
    print("Waiting for page to load...")
    page.wait_for_timeout(8000)
    
    html = page.content()
    print(f"Page length: {len(html)}")
    
    soup = BeautifulSoup(html, "html.parser")
    
    articles = soup.select("article.item, article")
    print(f"Articles found: {len(articles)}")
    
    if articles:
        for i, art in enumerate(articles[:3]):
            text = art.get_text(" ", strip=True)[:200]
            print(f"\n--- Article {i} ---")
            print(text)
            links = art.select("a[href]")
            for link in links[:3]:
                href = link.get("href", "")
                print(f"  LINK: {href}")
    else:
        title = soup.select_one("title")
        print(f"Title: {title.get_text() if title else 'N/A'}")
        body = soup.get_text(' ', strip=True)[:800]
        print(f"Body: {body}")
        # Check if there's a captcha or challenge
        if "captcha" in html.lower() or "challenge" in html.lower():
            print("CAPTCHA/Challenge detected!")
        # Save HTML for inspection
        with open("idealista_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved debug HTML to idealista_debug.html")
    
    browser.close()
