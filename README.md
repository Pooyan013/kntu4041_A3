# WebGIS Final Project (Flask + OpenLayers + GeoServer WMS)

WebGIS application with:

- Flask backend
- Login & registration (cookie-based session)
- Protected map page
- GeoServer WMS layer on OpenLayers map
- GetFeatureInfo (click WMS → show attributes)

## Made By

- Soroush Soltanzadeh
- Hossein Ahmadi
- Barbod Alamian

## Quick Start (Windows)

```powershell
cd Web_gIS/final
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`, register, then go to the Map page.

## WMS / GeoServer configuration

Defaults (works without any local GeoServer):

- `WMS_BASE_URL`: `https://ahocevar.com/geoserver/wms`
- `WMS_LAYER`: `topp:states`

Using our own geoserver :

```powershell
$env:WMS_BASE_URL="http://localhost:8080/geoserver/wms"
$env:WMS_LAYER="workspace:layername"
python app.py
```


## How it was built


## 1) Flask backend structure

- Single Flask app entrypoint: `app.py`
- Templates in `templates/`
- Static assets in `static/`
- SQLite database stored in `instance/webgis.sqlite3` (auto-created)

## 2) Cookie-based authentication

- Uses Flask's signed session cookie (`flask.session`) to store `user_id`.
- Passwords are hashed with Werkzeug (`generate_password_hash` / `check_password_hash`).
- Protected pages use a `login_required` decorator.

Routes:

- `GET/POST /register` → create user in SQLite, log in
- `GET/POST /login` → authenticate, set session cookie
- `POST/GET /logout` → clear session
- `GET /map` → protected map page

## 3) Map + WMS layer (OpenLayers)

Implemented in:

- `templates/map.html` (layout + config injection)
- `static/js/map.js` (OpenLayers map logic)

The map contains:

- OSM base layer
- TileWMS overlay layer pointing to `WMS_BASE_URL` and `WMS_LAYER`

## 4) GetFeatureInfo

What happens on click:

1. OpenLayers generates a standard WMS GetFeatureInfo URL via `getFeatureInfoUrl(...)`.
2. The browser calls Flask: `GET /api/feature-info?url=...`
3. Flask validates the URL host against `WMS_BASE_URL` and fetches the response server-side.
4. The frontend renders the returned GeoJSON properties as an HTML table in the right panel.

Why a Flask proxy endpoint is used:

- Many GeoServer instances don’t enable CORS for `GetFeatureInfo`.
- Fetching from Flask avoids browser CORS issues while keeping the frontend simple.

## 5) “Made by who” tab

- A public About page: `GET /about`
- Linked in the navbar so it behaves like a tab.

