(() => {
  const cfg = window.__WEBGIS__;
  if (!cfg || !window.ol) return;

  const infoEl = document.getElementById("info");
  const setInfoHtml = (html) => {
    if (!infoEl) return;
    infoEl.innerHTML = html;
  };

  const escapeHtml = (value) => {
    const text = value === null || value === undefined ? "" : String(value);
    return text
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  };

  const renderGeoJsonTable = (geojson) => {
    const features = Array.isArray(geojson?.features) ? geojson.features : [];
    if (!features.length) {
      setInfoHtml('<div class="muted">No feature found. Try clicking directly on the WMS layer.</div>');
      return;
    }

    const keys = Object.keys(features[0]?.properties || {});
    if (!keys.length) {
      setInfoHtml('<div class="muted">No properties in response.</div>');
      return;
    }

    let html = '<table class="table"><thead><tr>';
    for (const k of keys) html += `<th>${escapeHtml(k)}</th>`;
    html += "</tr></thead><tbody>";

    for (const f of features) {
      html += "<tr>";
      for (const k of keys) html += `<td>${escapeHtml(f?.properties?.[k])}</td>`;
      html += "</tr>";
    }

    html += "</tbody></table>";
    setInfoHtml(html);
  };

  const wmsSource = new ol.source.TileWMS({
    url: cfg.wmsBaseUrl,
    params: {
      LAYERS: cfg.wmsLayer,
      TILED: true,
    },
    serverType: cfg.wmsServerType || undefined,
    crossOrigin: "anonymous",
  });

  const wmsLayer = new ol.layer.Tile({ source: wmsSource });

  const map = new ol.Map({
    target: "map",
    layers: [new ol.layer.Tile({ source: new ol.source.OSM() }), wmsLayer],
    view: new ol.View({
      center: ol.proj.fromLonLat([-98.5, 39.8]),
      zoom: 4,
    }),
  });

  map.on("singleclick", async (evt) => {
    const view = map.getView();
    const resolution = view.getResolution();
    const projection = view.getProjection();

    const infoUrl = wmsSource.getFeatureInfoUrl(evt.coordinate, resolution, projection, {
      INFO_FORMAT: "application/json",
      FEATURE_COUNT: 10,
    });

    if (!infoUrl) {
      setInfoHtml('<div class="muted">No GetFeatureInfo URL generated for this click.</div>');
      return;
    }

    setInfoHtml('<div class="muted">Loading…</div>');

    try {
      const resp = await fetch(`${cfg.featureInfoEndpoint}?url=${encodeURIComponent(infoUrl)}`, {
        credentials: "same-origin",
      });
      const data = await resp.json();

      if (!resp.ok) {
        setInfoHtml(`<div class="muted">Error: ${escapeHtml(data?.error || "Request failed")}</div>`);
        return;
      }

      if (data?.features) {
        renderGeoJsonTable(data);
        return;
      }

      if (typeof data?.raw === "string") {
        setInfoHtml(`<pre>${escapeHtml(data.raw)}</pre>`);
        return;
      }

      setInfoHtml(`<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`);
    } catch (e) {
      setInfoHtml(`<div class="muted">Error: ${escapeHtml(e?.message || String(e))}</div>`);
    }
  });
})();

