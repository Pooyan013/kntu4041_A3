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

To use your own GeoServer, set environment variables before running:

```powershell
$env:WMS_BASE_URL="http://localhost:8080/geoserver/wms"
$env:WMS_LAYER="workspace:layername"
python app.py
```

Optional:

- `WMS_SERVER_TYPE` (default `geoserver`)
- `SECRET_KEY` (recommended to change)

## How it was built

See `HOW_IT_WAS_BUILT.md`.

The original course handout is preserved in `ASSIGNMENT_SPEC.md`.
