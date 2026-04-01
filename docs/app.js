const map = L.map('map');
const swissCenter = [46.8182, 8.2275];
const swissBounds = [
  [45.6, 5.7],
  [47.95, 10.7]
];

map.setView(swissCenter, 8);
map.setMaxBounds(swissBounds);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let latestStatusBySiteId = {};
let sitesData = [];
let currentSite = null;
let currentScenarioKey = null;
let currentScenarioConfig = null;
let currentViewMode = 'hazard';
const markersBySiteId = {};

function buildLatestStatusIndex(latestJson) {
  latestStatusBySiteId = {};

  if (!latestJson) return;

  if (Array.isArray(latestJson.sites)) {
    latestJson.sites.forEach(siteStatus => {
      latestStatusBySiteId[siteStatus.id] = siteStatus;
    });
  }
}

function markerColor(level) {
  switch (level) {
    case 'green': return '#2e7d32';
    case 'yellow': return '#b58900';
    case 'orange': return '#d97706';
    case 'red': return '#c62828';
    default: return '#2563eb';
  }
}

function badgeClass(level) {
  return `alert-badge alert-${level}`;
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} while loading ${path}`);
  }
  return await response.json();
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, ch => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[ch]));
}

function renderLegend() {
  return `
    <div class="legend-box">
      <div class="detail-label">Legend</div>
      <div class="legend-row"><span class="legend-dot legend-green"></span> Green — No flooding expected</div>
      <div class="legend-row"><span class="legend-dot legend-yellow"></span> Yellow — Minor flooding</div>
      <div class="legend-row"><span class="legend-dot legend-orange"></span> Orange — Moderate flooding</div>
      <div class="legend-row"><span class="legend-dot legend-red"></span> Red — Severe flooding</div>
    </div>
  `;
}

function populateSiteDropdown(sites) {
  const select = document.getElementById('site-select');
  select.innerHTML = '';

  sites.forEach(site => {
    const option = document.createElement('option');
    option.value = site.id;
    option.textContent = `${site.name} (${site.canton})`;
    select.appendChild(option);
  });

  select.addEventListener('change', async (event) => {
    const selectedSiteId = event.target.value;
    const selectedSite = sitesData.find(site => site.id === selectedSiteId);
    if (!selectedSite) return;

    await loadSite(selectedSite, { recenterMap: true, openPopup: true });
  });
}

function syncDropdown(siteId) {
  const select = document.getElementById('site-select');
  if (select && select.value !== siteId) {
    select.value = siteId;
  }
}

function focusSiteOnMap(site, openPopup = false) {
  map.setView([site.lat, site.lon], 10, { animate: true });

  const marker = markersBySiteId[site.id];
  if (marker && openPopup) {
    marker.openPopup();
  }
}

function createMarker(site) {
  const latestStatus = latestStatusBySiteId[site.id];
  const markerLevel = latestStatus?.alert_level || site.default_alert_level || 'green';
  const popupScenario = latestStatus?.selected_scenario || site.default_scenario || 'n/a';

  const marker = L.circleMarker([site.lat, site.lon], {
    radius: 9,
    color: markerColor(markerLevel),
    fillColor: markerColor(markerLevel),
    fillOpacity: 0.9,
    weight: 2
  });

  marker.bindPopup(`
    <strong>${escapeHtml(site.name)}</strong><br>
    Canton: ${escapeHtml(site.canton)}<br>
    Alert: ${escapeHtml(String(markerLevel).toUpperCase())}<br>
    Scenario: ${escapeHtml(String(popupScenario).toUpperCase())}
  `);

  marker.on('click', async () => {
    await loadSite(site, { recenterMap: false, openPopup: false });
    syncDropdown(site.id);
  });

  markersBySiteId[site.id] = marker;
  return marker;
}

function renderImpactTable(impactMetrics) {
  if (!impactMetrics || typeof impactMetrics !== 'object') {
    return `
      <div class="no-content-box">
        No impact metrics are available for this scenario.
      </div>
    `;
  }

  const rows = Object.entries(impactMetrics).map(([key, value]) => {
    const count = value?.count ?? 'n/a';
    const percent = value?.percent ?? 'n/a';
    return `
      <tr>
        <td>${escapeHtml(key)}</td>
        <td class="metric-num">${escapeHtml(String(count))}</td>
        <td class="metric-num">${escapeHtml(String(percent))}</td>
      </tr>
    `;
  }).join('');

  return `
    <table class="impact-table">
      <thead>
        <tr>
          <th>Pitch type</th>
          <th>Count</th>
          <th>Percent (%)</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

function renderContentBlock(site, scenarioConfig) {
  const hazardImage = scenarioConfig.hazard_image ?? null;
  const impactImage = scenarioConfig.impact_image ?? null;
  const impactMetrics = scenarioConfig.impact_metrics ?? null;

  if (currentViewMode === 'hazard') {
    return `
      <div class="detail-block">
        <div class="detail-label">Hazard map preview</div>
        ${
          hazardImage
            ? `
              <img
                class="hazard-image"
                src="${escapeHtml(hazardImage)}"
                alt="Hazard scenario ${escapeHtml(scenarioConfig.label)} for ${escapeHtml(site.name)}"
              >
            `
            : `
              <div class="no-content-box">
                No hazard map is shown for this scenario because no flooding is expected.
              </div>
            `
        }
      </div>
    `;
  }

  return `
    <div class="detail-block">
      <div class="detail-label">Impact metrics</div>
      ${
        impactImage
          ? `
            <img
              class="hazard-image"
              src="${escapeHtml(impactImage)}"
              alt="Impact metrics for scenario ${escapeHtml(scenarioConfig.label)} at ${escapeHtml(site.name)}"
            >
          `
          : `
            <div class="no-content-box">
              No impact plot is shown for this scenario because no impacts are expected.
            </div>
          `
      }
      ${renderImpactTable(impactMetrics)}
    </div>
  `;
}

function renderPanel(site, scenarioKey, scenarioConfig, availableScenarioKeys) {
  const latestStatus = latestStatusBySiteId[site.id];
  const panel = document.getElementById('panel');

  const buttonsHtml = availableScenarioKeys.map(key => {
    const scenario = site.scenarioData.scenarios[key];
    const isActive = key === scenarioKey ? 'active' : '';
    return `
      <button
        class="scenario-btn ${isActive}"
        data-scenario-key="${escapeHtml(key)}"
        type="button"
      >
        ${escapeHtml(scenario.label)}
      </button>
    `;
  }).join('');

  const viewButtonsHtml = `
    <button class="view-btn ${currentViewMode === 'hazard' ? 'active' : ''}" data-view-mode="hazard" type="button">
      Hazard map preview
    </button>
    <button class="view-btn ${currentViewMode === 'impact' ? 'active' : ''}" data-view-mode="impact" type="button">
      Impact metrics
    </button>
  `;

  panel.innerHTML = `
    <div class="${badgeClass((latestStatus?.alert_level) || scenarioConfig.alert_level)}">
      ${escapeHtml((latestStatus?.alert_level) || scenarioConfig.alert_level)}
    </div>

    <div class="detail-block">
      <div class="detail-label">Camping site</div>
      <div class="detail-value"><strong>${escapeHtml(site.name)}</strong></div>
    </div>

    <div class="detail-block">
      <div class="detail-label">Canton</div>
      <div class="detail-value">${escapeHtml(site.canton)}</div>
    </div>

    <div class="detail-block">
      <div class="detail-label">Coordinates</div>
      <div class="detail-value">${site.lat.toFixed(3)}, ${site.lon.toFixed(3)}</div>
    </div>

    <div class="detail-block">
      <div class="detail-label">Scenario</div>
      <div class="detail-value">${escapeHtml(scenarioConfig.label)}</div>
    </div>

    <div class="detail-block">
      <div class="detail-label">Message</div>
      <div class="detail-value">${escapeHtml(scenarioConfig.message)}</div>
    </div>

    ${latestStatus ? `
      <div class="detail-block">
        <div class="detail-label">Operational status</div>
        <div class="detail-value">${escapeHtml(latestStatus.message || "No message available.")}</div>
      </div>

      <div class="detail-block">
        <div class="detail-label">Selected scenario from forecast</div>
        <div class="detail-value">${escapeHtml(String(latestStatus.selected_scenario).toUpperCase())}</div>
      </div>

      <div class="detail-block">
        <div class="detail-label">Decision metrics</div>
        <div class="detail-value">
          domain_p90_6h: ${latestStatus.decision_metrics?.domain_p90_6h ?? "n/a"}<br>
          domain_mean_6h: ${latestStatus.decision_metrics?.domain_mean_6h ?? "n/a"}
        </div>
      </div>
    ` : ""}

    <div class="detail-block">
      <div class="detail-label">Available flood scenarios</div>
      <div class="scenario-buttons">
        ${buttonsHtml}
      </div>
    </div>

    <div class="detail-block">
      <div class="detail-label">Available views</div>
      <div class="view-toggle">
        ${viewButtonsHtml}
      </div>
    </div>

    ${renderContentBlock(site, scenarioConfig)}

    ${renderLegend()}
  `;

  panel.querySelectorAll('.scenario-btn').forEach(button => {
    button.addEventListener('click', () => {
      const selectedKey = button.dataset.scenarioKey;
      updateScenario(selectedKey);
    });
  });

  panel.querySelectorAll('.view-btn').forEach(button => {
    button.addEventListener('click', () => {
      const selectedView = button.dataset.viewMode;
      if (!selectedView) return;
      currentViewMode = selectedView;
      renderPanel(
        currentSite,
        currentScenarioKey,
        currentScenarioConfig,
        Object.keys(currentSite.scenarioData.scenarios)
      );
    });
  });
}

function updateScenario(scenarioKey) {
  if (!currentSite || !currentSite.scenarioData) return;

  const scenarioConfig = currentSite.scenarioData.scenarios[scenarioKey];
  if (!scenarioConfig) return;

  currentScenarioKey = scenarioKey;
  currentScenarioConfig = scenarioConfig;

  renderPanel(
    currentSite,
    currentScenarioKey,
    currentScenarioConfig,
    Object.keys(currentSite.scenarioData.scenarios)
  );
}

async function loadSite(site, options = {}) {
  const {
    recenterMap = false,
    openPopup = false
  } = options;

  const scenarioPath = `./scenarios/${site.id}/scenarios.json`;
  const scenarioData = await fetchJson(scenarioPath);

  site.scenarioData = scenarioData;
  currentSite = site;

  const scenarioKeys = Object.keys(scenarioData.scenarios);
  const latestStatus = latestStatusBySiteId[site.id];
  const preferredScenario = latestStatus?.selected_scenario || site.default_scenario;

  const initialScenarioKey = scenarioKeys.includes(preferredScenario)
    ? preferredScenario
    : scenarioKeys[0];

  currentViewMode = 'hazard';
  updateScenario(initialScenarioKey);
  syncDropdown(site.id);

  if (recenterMap) {
    focusSiteOnMap(site, openPopup);
  }
}

async function init() {
  const panel = document.getElementById('panel');

  try {
    const [sitesJson, latestJson] = await Promise.all([
      fetchJson('./api/sites.json'),
      fetchJson('./api/latest.json').catch(() => ({ sites: [] }))
    ]);

    sitesData = sitesJson.sites || [];
    buildLatestStatusIndex(latestJson);

    if (sitesData.length === 0) {
      panel.innerHTML = '<div class="placeholder">No sites found in sites.json.</div>';
      return;
    }

    populateSiteDropdown(sitesData);

    const bounds = [];

    sitesData.forEach(site => {
      const marker = createMarker(site);
      marker.addTo(map);
      bounds.push([site.lat, site.lon]);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [30, 30] });
    }

    await loadSite(sitesData[0], { recenterMap: false, openPopup: false });
  } catch (error) {
    panel.innerHTML = `
      <div class="detail-value">
        Failed to load site data.<br>
        <code>${escapeHtml(error.message)}</code>
      </div>
    `;
    console.error(error);
  }
}

init();
