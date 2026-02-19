from scraper import scrape_pisos_com
from excel_generator import generate_excel
from html_generator import generate_html

r = scrape_pisos_com("Pisos.com", "https://www.pisos.com", ["Murcia"])
print(f"Results: {len(r)}")
for x in r[:3]:
    print(f"  {x['precio']} | {x['descripcion'][:50]} | hab={x['habitaciones']} ban={x['banos']} asc={x['ascensor']}")
    print(f"  LINK: {x['link']}")

if r:
    generate_excel(r, "output/test.xlsx", "Pisos.com")
    generate_html(r, "output/test.html", "Pisos.com")
    print("Files generated in output/")
