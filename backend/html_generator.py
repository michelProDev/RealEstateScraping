from datetime import datetime


def generate_html(resultados, filepath, nombre_inmobiliaria):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    total = len(resultados)

    rows_html = ""
    for idx, prop in enumerate(resultados, 1):
        link = prop.get("link", "")
        link_cell = f'<a href="{link}" target="_blank">Ver inmueble</a>' if link else ""
        alt_class = ' class="alt"' if idx % 2 == 0 else ""
        rows_html += f"""        <tr{alt_class}>
            <td>{idx}</td>
            <td>{prop.get("region", "")}</td>
            <td class="precio">{prop.get("precio", "")}</td>
            <td>{prop.get("descripcion", "")}</td>
            <td class="center">{prop.get("habitaciones", "")}</td>
            <td class="center">{prop.get("banos", "")}</td>
            <td class="center">{prop.get("ascensor", "NO")}</td>
            <td>{link_cell}</td>
        </tr>
"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HouseHunt - {nombre_inmobiliaria}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2rem; margin-bottom: 6px; }}
        .header p {{ opacity: 0.8; font-size: 0.95rem; }}
        .container {{
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        .summary {{
            background: #fff;
            border-radius: 10px;
            padding: 20px 28px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .summary .stat {{
            font-size: 1.1rem;
        }}
        .summary .stat strong {{
            color: #0f3460;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        thead th {{
            background: #2C3E50;
            color: #fff;
            padding: 14px 12px;
            text-align: left;
            font-size: 0.9rem;
            font-weight: 600;
            white-space: nowrap;
        }}
        tbody td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
            font-size: 0.88rem;
            vertical-align: top;
        }}
        tbody tr:hover {{
            background: #e8f4fd !important;
        }}
        tbody tr.alt {{
            background: #f8f9fa;
        }}
        .precio {{
            font-weight: 700;
            color: #0f3460;
            white-space: nowrap;
        }}
        .center {{
            text-align: center;
        }}
        a {{
            color: #0563C1;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 0.8rem;
            margin-top: 30px;
        }}
        @media (max-width: 900px) {{
            table {{ font-size: 0.8rem; }}
            thead th, tbody td {{ padding: 8px 6px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>HouseHunt - {nombre_inmobiliaria}</h1>
        <p>Generado el {timestamp}</p>
    </div>
    <div class="container">
        <div class="summary">
            <div class="stat"><strong>{total}</strong> propiedades encontradas</div>
            <div class="stat">Inmobiliaria: <strong>{nombre_inmobiliaria}</strong></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Región</th>
                    <th>Precio</th>
                    <th>Descripción</th>
                    <th>Hab.</th>
                    <th>Baños</th>
                    <th>Ascensor</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
{rows_html}            </tbody>
        </table>
    </div>
    <div class="footer">
        HouseHunt &mdash; Herramienta de scraping inmobiliario
    </div>
</body>
</html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML generado: {filepath} ({total} propiedades)")
