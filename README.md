# 🏠 HouseHunt - Scraper de Inmobiliarias

Aplicación web con **Python (Flask)** + **React** que permite seleccionar inmobiliarias españolas y generar ficheros **Excel** y **HTML** con las propiedades en oferta mediante scraping.

## Requisitos

- **Python 3.9+**
- **Node.js 16+**
- **Google Chrome** (necesario para Playwright — usado en Idealista)

## Instalación

### 1. Backend (Python/Flask)

```bash
cd backend
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

El servidor se ejecutará en `http://localhost:5000`.

### 2. Frontend (React)

```bash
cd frontend
npm install
npm start
```

El frontend se ejecutará en `http://localhost:3000`.

## Uso

1. Abre `http://localhost:3000` en tu navegador.
2. Selecciona las **regiones** que te interesen (Murcia, Alicante, Valencia).
3. Haz clic en la **inmobiliaria** que quieras scrapear.
4. Espera a que termine el proceso (puede tardar unos minutos).
5. Descarga el fichero **Excel** o **HTML** con los resultados.

## Datos de salida

Se generan dos ficheros (Excel y HTML) con la misma información. Cada fila contiene:

| Campo         | Descripción                                |
|---------------|--------------------------------------------|
| Región        | Región de la propiedad                     |
| Precio        | Precio de la propiedad                     |
| Descripción   | Descripción del anuncio                    |
| Habitaciones  | Número de habitaciones                     |
| Baños         | Número de baños                            |
| Ascensor      | SI / NO                                    |
| Link          | Enlace directo al anuncio del inmueble     |

## Estructura del proyecto

```
houseHunt/
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── target.json        # Configuración de inmobiliarias y regiones
│   ├── app.py             # Servidor Flask (API REST)
│   ├── scraper.py         # Lógica de scraping (requests/cloudscraper/Playwright)
│   ├── excel_generator.py # Generación de Excel con openpyxl
│   ├── html_generator.py  # Generación de HTML
│   └── output/            # Ficheros Excel y HTML generados
└── frontend/
    ├── package.json
    └── src/
        ├── index.js
        ├── index.css
        └── App.js         # Componente principal React
```

## Tecnologías de scraping

| Inmobiliaria | Método                     | Estado        |
|--------------|----------------------------|---------------|
| Pisos.com    | requests + cloudscraper     | ✅ Funcional  |
| Fotocasa     | requests + cloudscraper     | ✅ Funcional  |
| Idealista    | Playwright (Chrome real)    | ✅ Funcional  |
| Habitaclia   | requests + cloudscraper     | ⚠️ Parcial    |
| Redpiso      | requests + cloudscraper     | ⚠️ Parcial    |
| Otros        | requests genérico           | ⚠️ Parcial    |

## Notas

- **Idealista** usa Playwright con Chrome visible (`headless=False`) para superar la protección Cloudflare. Se abrirá brevemente una ventana del navegador durante el scraping.
- **Pisos.com** y **Fotocasa** funcionan con `requests`/`cloudscraper` sin necesidad de navegador.
- Algunos sitios renderizan su contenido completamente con JavaScript, lo que puede limitar los resultados obtenidos solo con `requests`.
- Los ficheros generados se guardan en `backend/output/`.
