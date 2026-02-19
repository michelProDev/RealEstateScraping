from scraper import scrape_pisos_com

r = scrape_pisos_com("Pisos.com", "https://www.pisos.com", ["Murcia"])
print(f"Results: {len(r)}")
for x in r[:5]:
    print(f"  {x['precio']} | {x['descripcion'][:60]} | hab={x['habitaciones']} ban={x['banos']} asc={x['ascensor']}")
    print(f"  IMG: {x['imagen'][:80]}")
