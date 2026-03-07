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

let sitesData = [];
let currentSite = null;
let currentScenarioKey = null;
let currentScenarioConfig = null;

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

function createMarker(site) {
  const defaultLevel = site.default_alert_level || 'green';

  const marker = L.circleMarker([site.lat, site.lon], {
    radius: 9,
    color: markerColor(defaultLevel),
    fillColor: markerColor(defaultLevel),
    fillOpacity: 0.9,
    weight: 2
  });

  marker.bindPopup(`
    <strong>${escapeHtml(site.name)}</strong><br>
    Canton: ${escapeHtml(site.canton)}<br>
    Default scenario: ${escapeHtml(site.default_scenario)}
  `);

  marker.on('click', async () => {
    await loadSite(site);
  });

  return marker;
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

function renderPanel(site, scenarioKey, scenarioConfig, availableScenarioKeys) {
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

  panel.innerHTML = `
    <div class="${badgeClass(scenarioConfig.alert_level)}">${escapeHtml(scenarioConfig.alert_level)}</div>

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

    <div class="detail-block">
      <div class="detail-label">Available flood scenarios</div>
      <div class="scenario-buttons">
        ${buttonsHtml}
      </div>
    </div>

    <div class="detail-block">
      <div class="detail-label">Hazard map preview</div>
      <img
        class="hazard-image"
        src="${escapeHtml(scenarioConfig.image)}"
        alt="Hazard scenario ${escapeHtml(scenarioConfig.label)} for ${escapeHtml(site.name)}"
      >
    </div>

    ${renderLegend()}
  `;

  panel.querySelectorAll('.scenario-btn').forEach(button => {
    button.addEventListener('click', () => {
      const selectedKey = button.dataset.scenarioKey;
      updateScenario(selectedKey);
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

async function loadSite(site) {
  const scenarioPath = `./scenarios/${site.id}/scenarios.json`;
  const scenarioData = await fetchJson(scenarioPath);

  site.scenarioData = scenarioData;
  currentSite = site;

  const scenarioKeys = Object.keys(scenarioData.scenarios);
  const defaultScenario = site.default_scenario;

  const initialScenarioKey = scenarioKeys.includes(defaultScenario)
    ? defaultScenario
    : scenarioKeys[0];

  updateScenario(initialScenarioKey);
}

async function init() {
  const panel = document.getElementById('panel');

  try {
    const sitesJson = await fetchJson('./api/sites.json');
    sitesData = sitesJson.sites || [];

    if (sitesData.length === 0) {
      panel.innerHTML = '<div class="placeholder">No sites found in sites.json.</div>';
      return;
    }

    const bounds = [];

    sitesData.forEach(site => {
      const marker = createMarker(site);
      marker.addTo(map);
      bounds.push([site.lat, site.lon]);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [30, 30] });
    }

    await loadSite(sitesData[0]);
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
