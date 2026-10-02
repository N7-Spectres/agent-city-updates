let state = null;
let visitorPresence = null;
let selectedCitizen = null;
let focusedLocation = "seed_site";
let openControlView = "history";
let currentView = "home";
let sheetCitizenId = null;
let citizenDetailView = localStorage.getItem("agentCityCitizenDetailView") || "continuity";
let citizenSearchQuery = "";
let currentVisitAccessKey = null;
let chatSubmitting = false;
let spatialViewport = null;
let currentSharedActionProposals = [];
let currentVisitId = null;
let sharedActionBusyId = null;
let mapZoomLevel = 1;
let mapCenterOverride = null;
const MAP_ZOOM_MIN = 0.75;
const MAP_ZOOM_MAX = 8;
const citizenKnowledgeCache = new Map();
const locationKnowledgeCache = new Map();
const knowledgeLoading = new Set();
const KNOWLEDGE_REFRESH_MS = 12000;
const citizenContinuityCache = new Map();
const continuityLoading = new Set();
const CONTINUITY_REFRESH_MS = 12000;
const UPDATE_REFRESH_MS = 300000;

let historyRecords = null;
let historyRecordsLoading = false;
let historyConversationPage = 1;
let historyChronologyPage = 1;
const HISTORY_CONVERSATIONS_PER_PAGE = 8;
const HISTORY_CHRONOLOGY_PER_PAGE = 12;
const openConversationIds = new Set();

const LOCATION_PRESENTATION = {
  seed_site: {
    direction: { x: 0, y: 0 },
    label: "above",
    cluster: { x: 0, y: 38 },
    visitor: { x: -58, y: 0 },
  },
  northern_ridge: {
    direction: { x: 0, y: -1 },
    label: "below",
    cluster: { x: 54, y: 0 },
    visitor: { x: -54, y: 0 },
  },
  rocky_basin: {
    direction: { x: 1, y: -0.32 },
    label: "below",
    cluster: { x: -54, y: 0 },
    visitor: { x: 0, y: -46 },
  },
  southern_flats: {
    direction: { x: 0, y: 1 },
    label: "above",
    cluster: { x: 54, y: 0 },
    visitor: { x: -54, y: 0 },
  },
  resin_grove: {
    direction: { x: -1, y: -0.32 },
    label: "below",
    cluster: { x: 54, y: 0 },
    visitor: { x: 0, y: -46 },
  },
};

let locationPositions = {
  seed_site: { x: 50, y: 52 },
};

// v0.8 Stage 1 citizen visual profiles.
// These describe presentation canon only. They do not grant skills, equipment,
// physical paint, dimensions, inventory, or capability.
const CITIZEN_VISUAL_PROFILES = {
  aris: {
    accent_hue: 184,
    silhouette: "lean",
    canonical_aptitude: "extraction / prospecting",
    assets: {
      full: "/static/assets/citizens/aris/full.webp",
      bust: "/static/assets/citizens/aris/token.webp",
      token: "/static/assets/citizens/aris/token.webp",
      head: {
        neutral: null,
        blink: null,
        happy: null,
        focused: null,
        curious: null,
      },
    },
    equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] },
  },
  bex: {
    accent_hue: 28,
    silhouette: "compact",
    canonical_aptitude: "fabrication",
    assets: {
      full: "/static/assets/citizens/bex/full.webp",
      bust: "/static/assets/citizens/bex/token.webp",
      token: "/static/assets/citizens/bex/token.webp",
      head: {
        neutral: null,
        blink: null,
        happy: null,
        focused: null,
        curious: null,
      },
    },
    equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] },
  },
  cato: {
    accent_hue: 43,
    silhouette: "heavy",
    canonical_aptitude: "logistics / resource planning",
    assets: {
      full: "/static/assets/citizens/cato/full.webp",
      bust: "/static/assets/citizens/cato/token.webp",
      token: "/static/assets/citizens/cato/token.webp",
      head: {
        neutral: null,
        blink: null,
        happy: null,
        focused: null,
        curious: null,
      },
    },
    equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] },
  },
  iri: {
    accent_hue: 270,
    silhouette: "slim",
    canonical_aptitude: "construction",
    assets: {
      full: "/static/assets/citizens/iri/full.webp",
      bust: "/static/assets/citizens/iri/token.webp",
      token: "/static/assets/citizens/iri/token.webp",
      head: {
        neutral: null,
        blink: null,
        happy: null,
        focused: null,
        curious: null,
      },
    },
    equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] },
  },
  noma: {
    accent_hue: 92,
    silhouette: "soft",
    canonical_aptitude: "research / experimentation",
    assets: {
      full: "/static/assets/citizens/noma/full.webp",
      bust: "/static/assets/citizens/noma/token.webp",
      token: "/static/assets/citizens/noma/token.webp",
      head: {
        neutral: null,
        blink: null,
        happy: null,
        focused: null,
        curious: null,
      },
    },
    equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] },
  },
  vale: {
    accent_hue: 4,
    silhouette: "balanced",
    canonical_aptitude: "generalist / cooperation",
    assets: {
      full: "/static/assets/citizens/vale/full.webp",
      bust: "/static/assets/citizens/vale/token.webp",
      token: "/static/assets/citizens/vale/token.webp",
      head: {
        neutral: null,
        blink: null,
        happy: null,
        focused: null,
        curious: null,
      },
    },
    equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] },
  },
};

// Backward-compatible flat asset view used by Home/map/Citizens renderers.
// v0.8.1 supplies approved base-body + token art; optional gear stays separate.
const CITIZEN_AVATAR_ASSETS = Object.fromEntries(
  Object.entries(CITIZEN_VISUAL_PROFILES).map(([id, profile]) => [
    id,
    { full: profile.assets.full, token: profile.assets.token },
  ])
);

const els = {
  simTime: document.getElementById("sim-time"),
  pauseButton: document.getElementById("pause-button"),
  ollamaStatus: document.getElementById("ollama-status"),
  citizens: document.getElementById("citizens"),
  citizenSearch: document.getElementById("citizen-search"),
  recentActivity: document.getElementById("recent-activity"),
  maintenanceAlerts: document.getElementById("maintenance-alerts"),
  viewAllHistory: document.getElementById("view-all-history"),
  citizenDirectory: document.getElementById("citizen-directory"),
  citizenPortraitSlot: document.getElementById("citizen-portrait-slot"),
  citizenPortraitArt: document.getElementById("citizen-portrait-art"),
  citizenPortraitInitials: document.getElementById("citizen-portrait-initials"),
  citizenSheetName: document.getElementById("citizen-sheet-name"),
  citizenSheetRole: document.getElementById("citizen-sheet-role"),
  citizenSheetVisit: document.getElementById("citizen-sheet-visit"),
  citizenSheetBody: document.getElementById("citizen-sheet-body"),
  locationDirectory: document.getElementById("location-directory"),
  locationSceneName: document.getElementById("location-scene-name"),
  locationSheetName: document.getElementById("location-sheet-name"),
  locationSheetDescription: document.getElementById("location-sheet-description"),
  locationSheetFocus: document.getElementById("location-sheet-focus"),
  locationSheetBody: document.getElementById("location-sheet-body"),
  routeLayer: document.getElementById("route-layer"),
  mapLayer: document.getElementById("map-layer"),
  regionStrip: document.getElementById("region-strip"),
  worldFocus: document.getElementById("world-focus"),
  mapSpatialStatus: document.getElementById("map-spatial-status"),
  mapZoomIn: document.getElementById("map-zoom-in"),
  mapZoomOut: document.getElementById("map-zoom-out"),
  mapZoomReset: document.getElementById("map-zoom-reset"),
  mapZoomLabel: document.getElementById("map-zoom-label"),
  locations: document.getElementById("locations"),
  resourceBalance: document.getElementById("resource-balance"),
  citizenCargo: document.getElementById("citizen-cargo"),
  copyTroubleshootingSnapshot: document.getElementById("copy-troubleshooting-snapshot"),
  troubleshootingSnapshotStatus: document.getElementById("troubleshooting-snapshot-status"),
  projects: document.getElementById("projects"),
  equipment: document.getElementById("equipment"),
  structures: document.getElementById("structures"),
  maintenanceEvents: document.getElementById("maintenance-events"),
  history: document.getElementById("history"),
  citizenConversations: document.getElementById("citizen-conversations"),
  conversationPagination: document.getElementById("conversation-pagination"),
  chronologyPagination: document.getElementById("chronology-pagination"),
  conversationPageSummary: document.getElementById("conversation-page-summary"),
  chronologyPageSummary: document.getElementById("chronology-page-summary"),
  visitorStatus: document.getElementById("visitor-status"),
  selectedTitle: document.getElementById("selected-title"),
  selectedLabel: document.getElementById("selected-label"),
  visitorName: document.getElementById("visitor-name"),
  chatLog: document.getElementById("chat-log"),
  sharedActionPanel: document.getElementById("shared-action-panel"),
  chatForm: document.getElementById("chat-form"),
  chatInput: document.getElementById("chat-input"),
  sendButton: document.getElementById("send-button"),
  leaveVisit: document.getElementById("leave-visit"),
  previousVisits: document.getElementById("previous-visits"),
  visitHistoryPanel: document.getElementById("visit-history-panel"),
  controlRoom: document.getElementById("control-room"),
  detailEyebrow: document.getElementById("detail-eyebrow"),
  detailTitle: document.getElementById("detail-title"),
  versionLabel: document.getElementById("version-label"),
  updateFeed: document.getElementById("update-feed"),
  saveUpdateFeed: document.getElementById("save-update-feed"),
  checkUpdate: document.getElementById("check-update"),
  installUpdate: document.getElementById("install-update"),
  updateStatusTitle: document.getElementById("update-status-title"),
  updateStatusText: document.getElementById("update-status-text"),
  toggleRegion: document.getElementById("toggle-region"),
  toggleResources: document.getElementById("toggle-resources"),
  toggleStructures: document.getElementById("toggle-structures"),
  toggleHistory: document.getElementById("toggle-history"),
  toggleUpdates: document.getElementById("toggle-updates"),
  detailViews: {
    region: document.getElementById("detail-region"),
    resources: document.getElementById("detail-resources"),
    structures: document.getElementById("detail-structures"),
    history: document.getElementById("detail-history"),
    updates: document.getElementById("detail-updates"),
  }
};

function setView(name) {
  const valid = new Set(["home", "citizens", "locations", "records"]);
  currentView = valid.has(name) ? name : "home";

  document.querySelectorAll(".page-view").forEach(view => {
    view.classList.toggle("hidden", view.id !== `view-${currentView}`);
  });
  document.querySelectorAll(".primary-tab").forEach(button => {
    button.classList.toggle("active", button.dataset.view === currentView);
  });
  window.scrollTo({ top: 0, behavior: "instant" });
  if (currentView === "home" && state) {
    computeLocationPositions();
    renderMap();
  }
  if (currentView === "records" && openControlView === "history") {
    void loadHistoryRecords();
  }
}

function bindViewNavigation() {
  document.querySelectorAll("[data-view]").forEach(button => {
    button.addEventListener("click", () => setView(button.dataset.view));
  });
  document.querySelectorAll("[data-open-view]").forEach(button => {
    button.addEventListener("click", () => setView(button.dataset.openView));
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

let restoredVisit = false;

async function loadVisitorPresence() {
  const visitor = els.visitorName.value.trim() || "Visitor";
  try {
    const response = await fetch(`/api/visitor/presence?visitor=${encodeURIComponent(visitor)}`);
    const data = await response.json();
    if (response.ok) visitorPresence = data;
  } catch {
    visitorPresence = null;
  }
}

async function loadState() {
  if (!restoredVisit) {
    const savedVisitor = localStorage.getItem("agentCityVisitor");
    if (savedVisitor) els.visitorName.value = savedVisitor;
  }

  const response = await fetch("/api/state");
  state = await response.json();
  await loadVisitorPresence();
  render();
  if (currentView === "records" && openControlView === "history") {
    void loadHistoryRecords();
  }

  if (!restoredVisit) {
    restoredVisit = true;
    const savedCitizen = localStorage.getItem("agentCitySelectedCitizen");
    if (savedCitizen && state.citizens.some(c => c.id === savedCitizen)) {
      await selectCitizen(savedCitizen, { restore: true });
    }
  } else if (selectedCitizen) {
    const nextKey = visitAccessKey(selectedCitizen);
    if (nextKey !== currentVisitAccessKey) {
      currentVisitAccessKey = nextKey;
      await loadCurrentVisit(selectedCitizen);
    } else if (currentVisitId != null) {
      await refreshSharedActionProposals(selectedCitizen);
    }
  }
}

function inventoryFor(citizenId) {
  return state.inventory
    .filter(x => x.citizen_id === citizenId && x.amount > 0)
    .map(x => `${trimNumber(x.amount)} ${x.material}`)
    .join(", ");
}

function locationById(id) {
  return state.locations.find(x => x.id === id);
}

function citizenNameById(id) {
  return state?.citizens?.find(c => String(c.id) === String(id))?.name || String(id || "Unknown");
}

function depositsForLocation(locationId) {
  return state.deposits.filter(d => d.location_id === locationId && d.discovered);
}

function activeJobFor(citizenId) {
  const citizen = state.citizens.find(c => c.id === citizenId);
  if (citizen?.active_job_id != null) {
    const sharedJob = state.jobs.find(j => Number(j.id) === Number(citizen.active_job_id));
    if (sharedJob) return sharedJob;
  }
  return state.jobs.find(j => j.citizen_id === citizenId) || null;
}

function jobProgress(job) {
  if (!job) return null;
  const total = Math.max(1, Number(job.end_minute) - Number(job.start_minute));
  const elapsed = Math.min(total, Math.max(0, Number(state.sim_minute) - Number(job.start_minute)));
  const remaining = Math.max(0, Number(job.end_minute) - Number(state.sim_minute));
  return {
    total,
    elapsed,
    remaining,
    fraction: Math.min(1, Math.max(0, elapsed / total)),
    percent: Math.round(Math.min(1, Math.max(0, elapsed / total)) * 100),
  };
}

function isRouteTravelingCitizen(citizen) {
  return activeJobFor(citizen.id)?.action === "travel";
}

function localMovementForCitizen(citizen) {
  return citizen?.local_movement && typeof citizen.local_movement === "object"
    ? citizen.local_movement
    : null;
}

function isTravelingCitizen(citizen) {
  return isRouteTravelingCitizen(citizen) || Boolean(localMovementForCitizen(citizen));
}

function finiteNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function spatialDistanceMeters(ax, ay, bx, by) {
  const values = [ax, ay, bx, by].map(finiteNumber);
  if (values.some(value => value == null)) return null;
  return Math.hypot(values[0] - values[2], values[1] - values[3]);
}

function citizensAtLocation(locationId) {
  const loc = locationById(locationId);
  return (state?.citizens || []).filter(c => {
    if (isRouteTravelingCitizen(c)) return false;
    if (
      state?.spatial_frame &&
      finiteNumber(loc?.x_m) != null &&
      finiteNumber(loc?.y_m) != null &&
      finiteNumber(c.position_x_m) != null &&
      finiteNumber(c.position_y_m) != null
    ) {
      const distance = spatialDistanceMeters(c.position_x_m, c.position_y_m, loc.x_m, loc.y_m);
      return distance != null && distance <= 5;
    }
    return c.location_id === locationId && !localMovementForCitizen(c);
  });
}

function routeBetween(a, b) {
  return state.routes?.find(r =>
    (r.a === a && r.b === b) ||
    (r.a === b && r.b === a)
  ) || null;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function spatialFrameReady() {
  return Boolean(
    state?.spatial_frame &&
    String(state.spatial_frame.units || "").toLowerCase() === "meters" &&
    (state.locations || []).some(loc => finiteNumber(loc.x_m) != null && finiteNumber(loc.y_m) != null)
  );
}

function pointFromMeters(x, y, kind = "point", id = null) {
  const px = finiteNumber(x);
  const py = finiteNumber(y);
  return px == null || py == null ? null : { x_m: px, y_m: py, kind, id };
}

function nearestLocationToPoint(x, y, maxDistance = Infinity) {
  let best = null;
  for (const loc of state?.locations || []) {
    const distance = spatialDistanceMeters(x, y, loc.x_m, loc.y_m);
    if (distance == null || distance > maxDistance) continue;
    if (!best || distance < best.distance) best = { loc, distance };
  }
  return best;
}

function computeSpatialViewport() {
  if (!spatialFrameReady()) return null;

  const stage = els.mapLayer?.parentElement;
  const rect = stage?.getBoundingClientRect?.() || {};
  const width = Math.max(520, Number(rect.width) || 900);
  const height = Math.max(360, Number(rect.height) || 540);

  const selected = selectedCitizen
    ? (state.citizens || []).find(c => c.id === selectedCitizen)
    : null;
  const selectedMove = localMovementForCitizen(selected);
  const visitorMove = visitorPresence?.shared_activity?.movement || null;

  const focusPoints = [];
  let mode = "region";

  const add = point => {
    if (point) focusPoints.push(point);
  };

  if (selectedMove) {
    mode = "local";
    add(pointFromMeters(selectedMove.start_x_m, selectedMove.start_y_m, "movement-start"));
    add(pointFromMeters(selectedMove.target_x_m, selectedMove.target_y_m, "movement-target"));
    add(pointFromMeters(selected?.position_x_m, selected?.position_y_m, "citizen", selected?.id));
  } else if (visitorMove) {
    mode = "local";
    add(pointFromMeters(visitorMove.start_x_m, visitorMove.start_y_m, "movement-start"));
    add(pointFromMeters(visitorMove.target_x_m, visitorMove.target_y_m, "movement-target"));
    add(pointFromMeters(visitorPresence?.x_m, visitorPresence?.y_m, "visitor"));
  } else if (selected && finiteNumber(selected.position_x_m) != null && finiteNumber(selected.position_y_m) != null) {
    const anchor = locationById(selected.location_id);
    const offset = spatialDistanceMeters(selected.position_x_m, selected.position_y_m, anchor?.x_m, anchor?.y_m);
    if (offset != null && offset > 5) {
      mode = "local";
      add(pointFromMeters(selected.position_x_m, selected.position_y_m, "citizen", selected.id));
      add(pointFromMeters(anchor?.x_m, anchor?.y_m, "landmark", anchor?.id));
    }
  }

  if (mode === "local" && focusPoints.length) {
    const cx = focusPoints.reduce((sum, p) => sum + p.x_m, 0) / focusPoints.length;
    const cy = focusPoints.reduce((sum, p) => sum + p.y_m, 0) / focusPoints.length;
    const nearest = nearestLocationToPoint(cx, cy, 350);
    if (nearest) add(pointFromMeters(nearest.loc.x_m, nearest.loc.y_m, "landmark", nearest.loc.id));

    for (const observation of state?.spatial_observations || []) {
      const distance = spatialDistanceMeters(cx, cy, observation.x_m, observation.y_m);
      if (distance != null && distance <= 300) {
        add(pointFromMeters(observation.x_m, observation.y_m, "observation", observation.id));
      }
    }
    for (const citizen of state?.citizens || []) {
      const distance = spatialDistanceMeters(cx, cy, citizen.position_x_m, citizen.position_y_m);
      if (distance != null && distance <= 220) {
        add(pointFromMeters(citizen.position_x_m, citizen.position_y_m, "citizen", citizen.id));
      }
    }
    const visitorDistance = spatialDistanceMeters(cx, cy, visitorPresence?.x_m, visitorPresence?.y_m);
    if (visitorDistance != null && visitorDistance <= 220) {
      add(pointFromMeters(visitorPresence.x_m, visitorPresence.y_m, "visitor"));
    }
  } else {
    for (const loc of state?.locations || []) add(pointFromMeters(loc.x_m, loc.y_m, "landmark", loc.id));
    for (const observation of state?.spatial_observations || []) add(pointFromMeters(observation.x_m, observation.y_m, "observation", observation.id));
    for (const citizen of state?.citizens || []) {
      add(pointFromMeters(citizen.position_x_m, citizen.position_y_m, "citizen", citizen.id));
      const movement = localMovementForCitizen(citizen);
      if (movement) add(pointFromMeters(movement.target_x_m, movement.target_y_m, "movement-target", citizen.id));
    }
    add(pointFromMeters(visitorPresence?.x_m, visitorPresence?.y_m, "visitor"));
  }

  const points = focusPoints.filter(Boolean);
  if (!points.length) return null;

  let minX = Math.min(...points.map(p => p.x_m));
  let maxX = Math.max(...points.map(p => p.x_m));
  let minY = Math.min(...points.map(p => p.y_m));
  let maxY = Math.max(...points.map(p => p.y_m));

  const minimumSpan = mode === "local" ? 120 : 500;
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  let spanX = Math.max(minimumSpan, maxX - minX);
  let spanY = Math.max(minimumSpan, maxY - minY);
  spanX *= 1.28;
  spanY *= 1.28;

  const scale = Math.min((width * 0.80) / spanX, (height * 0.72) / spanY);

  const overrideX = finiteNumber(mapCenterOverride?.x_m);
  const overrideY = finiteNumber(mapCenterOverride?.y_m);
  const presentationCenterX = overrideX != null ? overrideX : cx;
  const presentationCenterY = overrideY != null ? overrideY : cy;

  return {
    mode: mapCenterOverride ? "focused" : mode,
    frameId: state.spatial_frame.id || "seed_site_local",
    units: "meters",
    centerX: presentationCenterX,
    centerY: presentationCenterY,
    width,
    height,
    scalePxPerMeter: Math.max(0.0001, scale * mapZoomLevel),
    zoomLevel: mapZoomLevel,
  };
}

function metersToMap(x, y) {
  const px = finiteNumber(x);
  const py = finiteNumber(y);
  if (!spatialViewport || px == null || py == null) return null;
  return {
    x: 50 + (((px - spatialViewport.centerX) * spatialViewport.scalePxPerMeter) / spatialViewport.width) * 100,
    y: 50 - (((py - spatialViewport.centerY) * spatialViewport.scalePxPerMeter) / spatialViewport.height) * 100,
  };
}

function computeLegacyLocationPositions() {
  const center = { x: 50, y: 52 };
  const locations = state?.locations || [];
  const routes = state?.routes || [];
  const directRoutes = routes.filter(r => r.a === "seed_site" || r.b === "seed_site");
  const distances = directRoutes.map(r => Number(r.distance_km)).filter(Number.isFinite);
  const minDistance = distances.length ? Math.min(...distances) : 0;
  const maxDistance = distances.length ? Math.max(...distances) : 1;
  locationPositions = {};

  let fallbackIndex = 0;
  for (const loc of locations) {
    if (loc.id === "seed_site") {
      locationPositions[loc.id] = center;
      continue;
    }
    const route = directRoutes.find(r => r.a === loc.id || r.b === loc.id);
    const distance = Number(route?.distance_km);
    const normalizedDistance = Number.isFinite(distance) && maxDistance > minDistance
      ? (distance - minDistance) / (maxDistance - minDistance)
      : 0.5;
    const radius = 29 + (normalizedDistance * 14);
    let direction = LOCATION_PRESENTATION[loc.id]?.direction;
    if (!direction) {
      const angle = ((fallbackIndex++ / Math.max(1, locations.length - 1)) * Math.PI * 2) - (Math.PI / 2);
      direction = { x: Math.cos(angle), y: Math.sin(angle) };
    }
    const magnitude = Math.hypot(direction.x, direction.y) || 1;
    locationPositions[loc.id] = {
      x: clamp(center.x + ((direction.x / magnitude) * radius), 8, 92),
      y: clamp(center.y + ((direction.y / magnitude) * radius), 10, 90),
    };
  }
}

function computeLocationPositions() {
  spatialViewport = computeSpatialViewport();
  if (!spatialViewport) {
    computeLegacyLocationPositions();
    return;
  }

  locationPositions = {};
  for (const loc of state?.locations || []) {
    const pos = metersToMap(loc.x_m, loc.y_m);
    if (pos) locationPositions[loc.id] = pos;
  }
}

function positionForLocation(id) {
  return locationPositions[id] || { x: 50, y: 52 };
}

function interpolatedPosition(a, b, fraction) {
  const from = positionForLocation(a);
  const to = positionForLocation(b);
  return {
    x: from.x + (to.x - from.x) * fraction,
    y: from.y + (to.y - from.y) * fraction,
  };
}

function sameRoute(a, b, c, d) {
  return (a === c && b === d) || (a === d && b === c);
}

function initialsFor(name) {
  return String(name || "?")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(part => part[0] || "")
    .join("")
    .toUpperCase();
}

// UI-only interface accent, not physical paint or authoritative citizen appearance.
function citizenVisualProfile(citizenId) {
  return CITIZEN_VISUAL_PROFILES[String(citizenId)] || null;
}

function avatarHueFor(citizenId) {
  const profile = citizenVisualProfile(citizenId);
  if (profile?.accent_hue != null) return Number(profile.accent_hue);

  const text = String(citizenId || "");
  let hash = 0;
  for (const char of text) hash = ((hash * 31) + char.charCodeAt(0)) % 360;
  return hash;
}

function citizenSilhouetteClass(citizenId) {
  const silhouette = citizenVisualProfile(citizenId)?.silhouette || "balanced";
  return `silhouette-${silhouette}`;
}

function citizenVisualState(citizen) {
  const action = activeJobFor(citizen.id)?.action;
  if (localMovementForCitizen(citizen) || action === "travel" || action === "local_move" || action === "shared_local_activity") return "traveling";
  if (action === "charge") return "charging";
  if (action === "talk") return "talking";
  if (action) return "working";
  return "idle";
}

function citizenAvatarAsset(citizenId, variant) {
  const record = CITIZEN_AVATAR_ASSETS[String(citizenId)] || {};
  return record[variant] || null;
}

function citizenAvatarMarkup(citizen, variant = "token") {
  const stateClass = citizenVisualState(citizen);
  const assetVariant = variant === "full" ? "full" : "token";
  const asset = citizenAvatarAsset(citizen.id, assetVariant);
  const hue = avatarHueFor(citizen.id);
  const classes = [
    "citizen-avatar",
    `avatar-${variant}`,
    `state-${stateClass}`,
    asset ? "has-image" : "fallback-avatar",
    citizenSilhouetteClass(citizen.id),
  ].join(" ");

  if (asset) {
    return `
      <span class="${classes}" style="--avatar-hue:${hue};">
        <img class="avatar-image" src="${escapeHtml(asset)}" alt="" />
      </span>
    `;
  }

  if (variant === "full") {
    return `
      <span class="${classes}" style="--avatar-hue:${hue};">
        <span class="avatar-fallback-figure">
          <i class="avatar-head"></i>
          <i class="avatar-body"></i>
        </span>
        <span class="avatar-initials">${escapeHtml(initialsFor(citizen.name))}</span>
      </span>
    `;
  }

  return `
    <span class="${classes}" style="--avatar-hue:${hue};" aria-hidden="true">
      <span class="avatar-initials">${escapeHtml(initialsFor(citizen.name))}</span>
    </span>
  `;
}

function applyCitizenPortrait(citizen) {
  const stateClass = citizenVisualState(citizen);
  const asset = citizenAvatarAsset(citizen.id, "full");
  const hue = avatarHueFor(citizen.id);

  els.citizenPortraitArt.className = `citizen-avatar avatar-full state-${stateClass} ${asset ? "has-image" : "fallback-avatar"} ${citizenSilhouetteClass(citizen.id)}`;
  els.citizenPortraitArt.style.setProperty("--avatar-hue", String(hue));
  els.citizenPortraitArt.style.removeProperty("--avatar-image");

  if (asset) {
    els.citizenPortraitArt.innerHTML = `<img class="avatar-image" src="${escapeHtml(asset)}" alt="" />`;
  } else {
    els.citizenPortraitArt.innerHTML = `
      <span class="avatar-fallback-figure">
        <i class="avatar-head"></i>
        <i class="avatar-body"></i>
      </span>
      <span id="citizen-portrait-initials" class="avatar-initials">${escapeHtml(initialsFor(citizen.name))}</span>
    `;
    els.citizenPortraitInitials = document.getElementById("citizen-portrait-initials");
  }
}

function clusterOffset(index, total) {
  const row = Math.floor(index / 3);
  const firstInRow = row * 3;
  const rowCount = Math.min(3, total - firstInRow);
  const column = index - firstInRow;
  return {
    x: (column - ((rowCount - 1) / 2)) * 28,
    y: row * 30,
  };
}

function visitAccessKey(citizenId) {
  const c = state?.citizens.find(x => x.id === citizenId);
  const job = c ? activeJobFor(c.id) : null;
  return [
    citizenId,
    visitorPresence?.location_id || "",
    visitorPresence?.travel_end_minute || "",
    c?.location_id || "",
    job?.action || "",
    job?.target || "",
  ].join("|");
}

function trimNumber(value) {
  const n = Number(value);
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

function conditionStateLabel(value) {
  return String(value || "unknown").replaceAll("_", " ");
}

function maintenanceSeverityRank(severity) {
  const ranks = { critical: 0, degraded: 1, service_due: 2, nominal: 3 };
  return ranks[severity] ?? 4;
}

function maintenanceAlertsForHome(limit = 4) {
  const alerts = [];

  for (const citizen of state?.citizens || []) {
    if (citizen.battery_replacement_due) {
      alerts.push({
        key: `citizen-battery:${citizen.id}`,
        severity: citizen.battery_state || "service_due",
        title: `${citizen.name} battery service`,
        text: `${trimNumber(citizen.battery_health)}% health • ${conditionStateLabel(citizen.battery_state)}`,
      });
    }
    if (citizen.chassis_service_due) {
      alerts.push({
        key: `citizen-chassis:${citizen.id}`,
        severity: citizen.chassis_service_state || "service_due",
        title: `${citizen.name} chassis service`,
        text: `Joint wear ${trimNumber(citizen.joint_wear)} • ${conditionStateLabel(citizen.chassis_service_state)}`,
      });
    }
  }

  for (const item of state?.equipment || []) {
    if (!item.service_due && item.operational !== false) continue;
    alerts.push({
      key: `equipment:${item.id}`,
      severity: item.condition_state || (item.operational === false ? "critical" : "service_due"),
      title: item.name || `Equipment #${item.id}`,
      text: item.operational === false
        ? `Non-operational • ${trimNumber(item.condition)}%`
        : `Service due • ${trimNumber(item.condition)}% • ${conditionStateLabel(item.condition_state)}`,
    });
  }

  for (const structure of state?.structures || []) {
    if (!structure.service_due && structure.operational !== false) continue;
    alerts.push({
      key: `structure:${structure.id}`,
      severity: structure.condition_state || (structure.operational === false ? "critical" : "service_due"),
      title: structure.name || `Structure #${structure.id}`,
      text: structure.operational === false
        ? `Non-operational • ${trimNumber(structure.condition)}%`
        : `Service due • ${trimNumber(structure.condition)}% • ${conditionStateLabel(structure.condition_state)}`,
    });
  }

  alerts.sort((a, b) =>
    maintenanceSeverityRank(a.severity) - maintenanceSeverityRank(b.severity)
    || a.title.localeCompare(b.title)
  );

  return {
    visible: alerts.slice(0, Math.max(1, limit)),
    total: alerts.length,
  };
}

function renderMaintenanceAlerts() {
  const { visible, total } = maintenanceAlertsForHome(4);
  if (!visible.length) {
    els.maintenanceAlerts.classList.add("hidden");
    els.maintenanceAlerts.innerHTML = "";
    return;
  }

  const extra = Math.max(0, total - visible.length);
  els.maintenanceAlerts.innerHTML = `
    <div class="maintenance-alerts-head">
      <strong>Maintenance attention</strong>
      ${extra ? `<span>+${extra} more in Records</span>` : "<span>Authoritative physical state</span>"}
    </div>
    <div class="maintenance-alert-list">
      ${visible.map(alert => `
        <div class="maintenance-alert severity-${escapeHtml(alert.severity)}">
          <span class="maintenance-alert-dot"></span>
          <div>
            <strong>${escapeHtml(alert.title)}</strong>
            <p>${escapeHtml(alert.text)}</p>
          </div>
        </div>
      `).join("")}
    </div>
  `;
  els.maintenanceAlerts.classList.remove("hidden");
}

function parseMaterialsJson(value) {
  if (!value) return {};
  try {
    const parsed = typeof value === "string" ? JSON.parse(value) : value;
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch {
    return {};
  }
}

function maintenanceTargetLabel(event) {
  const targetType = String(event?.target_type || "");
  const targetId = event?.target_id;
  if (targetType === "citizen") return citizenNameById(targetId);
  if (targetType === "equipment") {
    return state?.equipment?.find(item => String(item.id) === String(targetId))?.name || `Equipment #${targetId}`;
  }
  if (targetType === "structure") {
    return state?.structures?.find(item => String(item.id) === String(targetId))?.name || `Structure #${targetId}`;
  }
  return targetId != null ? `${targetType || "target"} #${targetId}` : "Target unavailable";
}

function renderMaintenanceHistory() {
  const events = (state?.maintenance_events || []).slice(0, 16);
  els.maintenanceEvents.innerHTML = events.length ? events.map(event => {
    const materials = parseMaterialsJson(event.materials_json);
    const materialsText = Object.entries(materials)
      .map(([name, amount]) => `${trimNumber(amount)} ${name}`)
      .join(", ");
    const before = Number(event.before_value);
    const after = Number(event.after_value);
    const delta = Number.isFinite(before) && Number.isFinite(after)
      ? `${trimNumber(before)} → ${trimNumber(after)}`
      : "";

    return `
      <article class="maintenance-event-card" data-maintenance-event-id="${escapeHtml(String(event.id))}">
        <div class="maintenance-event-head">
          <div>
            <strong>${escapeHtml(String(event.event_type || "maintenance").replaceAll("_", " "))}</strong>
            <span>${escapeHtml(maintenanceTargetLabel(event))}</span>
          </div>
          <time>${escapeHtml(formatMinute(event.sim_minute))}</time>
        </div>
        <p>${escapeHtml(event.summary || "Maintenance event recorded.")}</p>
        <div class="maintenance-event-meta">
          <span>Event #${escapeHtml(String(event.id))}</span>
          ${event.job_id != null ? `<span>Job #${escapeHtml(String(event.job_id))}</span>` : ""}
          <span>${escapeHtml(event.outcome || "recorded")}</span>
          ${delta ? `<span>${escapeHtml(delta)}</span>` : ""}
          ${materialsText ? `<span>${escapeHtml(materialsText)}</span>` : ""}
        </div>
      </article>
    `;
  }).join("") : '<div class="muted making-empty">No completed maintenance events recorded yet.</div>';
}

function isMeaningfulHistoryRow(row) {
  const message = String(row?.message || "").trim();
  if (!message) return false;
  if (row.category === "diagnostic") return false;

  // Stored conversation summaries are rendered separately from real conversation rows.
  if (row.category === "conversation") return false;
  if (/\(conversation #\d+\)/i.test(message)) return false;
  if (/\bbegan:\s*Talking with\b/i.test(message)) return false;

  // Routine observe/wait churn does not deserve Home at-a-glance space.
  if (/\bobserving surroundings\b/i.test(message)) return false;
  if (/\bfinished observing\b/i.test(message)) return false;

  // Failed conversation attempts intentionally remain ordinary events.
  return true;
}

function recentActivityItems(limit = 5) {
  const items = [];
  const maintenanceSummaryKeys = new Set();

  for (const event of state?.maintenance_events || []) {
    const summary = String(event.summary || "").trim();
    if (!summary) continue;
    const simMinute = Number(event.sim_minute) || 0;
    maintenanceSummaryKeys.add(`${simMinute}::${summary}`);
    items.push({
      key: `maintenance:${event.id}`,
      kind: "maintenance",
      simMinute,
      title: `Maintenance • ${maintenanceTargetLabel(event)}`,
      text: summary,
      meta: "",
    });
  }

  for (const conversation of state?.citizen_conversations || []) {
    const summary = String(conversation.summary || "").trim();
    if (!summary) continue;
    items.push({
      key: `conversation:${conversation.id}`,
      kind: "conversation",
      simMinute: Number(conversation.sim_minute) || 0,
      title: `${conversation.initiator_name} ↔ ${conversation.target_name}`,
      text: summary,
      meta: conversation.location_name || "",
    });
  }

  for (const row of state?.history || []) {
    if (!isMeaningfulHistoryRow(row)) continue;
    const simMinute = Number(row.sim_minute) || 0;
    const message = String(row.message || "").trim();
    if (maintenanceSummaryKeys.has(`${simMinute}::${message}`)) continue;

    items.push({
      key: `history:${row.id ?? row.sim_minute}:${row.message}`,
      kind: row.category === "maintenance" ? "maintenance" : "event",
      simMinute,
      title: row.category === "visitor"
        ? "Visitor"
        : row.category === "maintenance"
          ? "Maintenance"
          : "City event",
      text: message,
      meta: "",
    });
  }

  items.sort((a, b) => {
    if (b.simMinute !== a.simMinute) return b.simMinute - a.simMinute;
    if (a.kind === b.kind) return 0;
    if (a.kind === "maintenance") return -1;
    return a.kind === "conversation" ? -1 : 1;
  });

  return items.slice(0, Math.max(1, limit));
}

function renderRecentActivity() {
  const items = recentActivityItems(5);
  els.recentActivity.innerHTML = items.length ? items.map(item => `
    <article class="recent-activity-item ${item.kind}">
      <div class="recent-activity-time">${escapeHtml(formatMinute(item.simMinute))}</div>
      <div class="recent-activity-copy">
        <strong>${escapeHtml(item.title)}</strong>
        <p>${escapeHtml(item.text)}</p>
        ${item.meta ? `<span>${escapeHtml(item.meta)}</span>` : ""}
      </div>
    </article>
  `).join("") : '<div class="muted recent-activity-empty">No meaningful recent activity yet.</div>';
}

function visualDayPhase(simMinute) {
  const minute = ((Number(simMinute) % 1440) + 1440) % 1440;
  if (minute >= 300 && minute < 420) return "dawn";
  if (minute >= 420 && minute < 1080) return "day";
  if (minute >= 1080 && minute < 1320) return "dusk";
  return "night";
}

function visualDayPhaseLabel(phase) {
  return {
    dawn: "Dawn",
    day: "Daylight",
    dusk: "Dusk",
    night: "Night",
  }[phase] || "Daylight";
}

function render() {
  const dayPhase = visualDayPhase(state.sim_minute);
  document.body.dataset.dayPhase = dayPhase;
  els.simTime.textContent = `${state.sim_label} • ${visualDayPhaseLabel(dayPhase)} • ${state.paused ? "Paused" : "Running"}`;
  els.pauseButton.textContent = state.paused ? "Resume" : "Pause";
  computeLocationPositions();
  renderVisitorStatus();

  renderCitizens();
  renderMaintenanceAlerts();
  renderRecentActivity();
  renderCitizenDirectory();
  renderCitizenSheet();
  renderLocationDirectory();
  renderLocationSheet();
  renderMap();
  updateMapZoomLabel();
  renderRegionStrip();
  renderDrawerLists();
}

function renderVisitorStatus() {
  if (!visitorPresence) {
    els.visitorStatus.textContent = "Visitor: unavailable";
    return;
  }
  const visitor = els.visitorName.value.trim() || "Visitor";
  if (visitorPresence.shared_activity?.movement) {
    const p = Math.round(clamp(Number(visitorPresence.shared_activity.movement.progress) || 0, 0, 1) * 100);
    els.visitorStatus.textContent = `${visitor}: shared local activity • ${p}%`;
  } else if (visitorPresence.traveling) {
    els.visitorStatus.textContent = `${visitor}: traveling to ${visitorPresence.to_location_name} • ${visitorPresence.remaining_minutes}m left`;
  } else if (spatialViewport && finiteNumber(visitorPresence.x_m) != null && finiteNumber(visitorPresence.y_m) != null) {
    els.visitorStatus.textContent = `${visitor}: ${visitorPresence.location_name} • x ${trimNumber(visitorPresence.x_m)}m / y ${trimNumber(visitorPresence.y_m)}m`;
  } else {
    els.visitorStatus.textContent = `${visitor}: ${visitorPresence.location_name}`;
  }
}

function normalizedVitalPercent(value) {
  const n = Number(value);
  return Math.round(clamp(Number.isFinite(n) ? n : 0, 0, 100));
}

function citizenLiveVitalsMarkup(citizen, { compact = false } = {}) {
  const energy = normalizedVitalPercent(citizen?.energy);
  const integrity = normalizedVitalPercent(citizen?.integrity);

  if (compact) {
    return `
      <div class="compact-vitals" aria-label="Energy ${energy} percent, integrity ${integrity} percent">
        <span class="compact-vital vital-energy" title="Current energy ${energy}%">
          <span class="vital-icon" aria-hidden="true">⚡</span>
          <span class="vital-meter-track" aria-hidden="true"><i style="width:${energy}%"></i></span>
          <b>${energy}%</b>
        </span>
        <span class="compact-vital vital-integrity" title="Current integrity ${integrity}%">
          <span class="vital-icon" aria-hidden="true">⛭</span>
          <span class="vital-meter-track" aria-hidden="true"><i style="width:${integrity}%"></i></span>
          <b>${integrity}%</b>
        </span>
      </div>
    `;
  }

  return `
    <div class="sheet-live-vitals" aria-label="Live operational state">
      <div class="sheet-live-vital vital-energy">
        <span class="sheet-live-vital-label"><span aria-hidden="true">⚡</span> Current energy</span>
        <span class="vital-meter-track sheet-vital-track" aria-hidden="true"><i style="width:${energy}%"></i></span>
        <b>${energy}%</b>
      </div>
      <div class="sheet-live-vital vital-integrity">
        <span class="sheet-live-vital-label"><span aria-hidden="true">⛭</span> Integrity</span>
        <span class="vital-meter-track sheet-vital-track" aria-hidden="true"><i style="width:${integrity}%"></i></span>
        <b>${integrity}%</b>
      </div>
    </div>
  `;
}

function renderCitizens() {
  const query = citizenSearchQuery.trim().toLowerCase();
  const visible = (state.citizens || []).filter(c =>
    !query || String(c.name || "").toLowerCase().includes(query)
  );

  els.citizens.innerHTML = visible.length ? visible.map(c => {
    const cargo = inventoryFor(c.id);
    const job = activeJobFor(c.id);
    const progress = job ? jobProgress(job) : null;
    const destination = job?.action === "travel" ? locationById(job.target)?.name : null;
    const localMove = localMovementForCitizen(c);
    const where = destination
      ? `${c.location} → ${destination}`
      : localMove
        ? `${c.location} • local ${trimNumber(localMove.path_distance_m || 0)} m`
        : c.location;
    const progressMarkup = job && progress ? `
      <div class="citizen-job-progress" aria-label="${escapeHtml(c.current_activity)} progress ${progress.percent}%">
        <div class="citizen-job-progress-meta">
          <span>${progress.elapsed} / ${progress.total} sim min</span>
          <span>${progress.remaining} remaining • ETA ${escapeHtml(formatMinute(job.end_minute))}</span>
        </div>
        <div class="citizen-job-progress-track">
          <span style="width:${progress.percent}%"></span>
        </div>
      </div>
    ` : "";

    return `
      <button class="citizen-row compact-citizen-row ${selectedCitizen === c.id ? "selected" : ""}" onclick="selectCitizen('${c.id}')">
        <div class="compact-citizen-main">
          ${citizenAvatarMarkup(c, "token")}
          <div>
            <div class="citizen-name">${escapeHtml(c.name)}</div>
            <div class="activity">${escapeHtml(c.current_activity)}</div>
            <div class="location-line">${escapeHtml(where)}${cargo ? ` • ${escapeHtml(cargo)}` : ""}</div>
          </div>
        </div>
        ${progressMarkup}
        ${citizenLiveVitalsMarkup(c, { compact: true })}
      </button>
    `;
  }).join("") : `
    <div class="citizen-search-empty">
      <strong>No citizen matches “${escapeHtml(citizenSearchQuery)}”.</strong>
      <span>Try a shorter name.</span>
    </div>
  `;
}

function cargoRowsForCitizen(citizenId) {
  return (state.inventory || []).filter(row =>
    String(row.citizen_id) === String(citizenId) && Number(row.amount) > 0
  );
}

function equipmentForCitizen(citizenId) {
  return (state.equipment || []).filter(item =>
    String(item.owner_citizen_id || "") === String(citizenId)
  );
}

function projectsForCitizen(citizenId) {
  return (state.projects || []).filter(project =>
    String(project.created_by || "") === String(citizenId)
  );
}

function personalDiscoveriesForCitizen(citizenId) {
  return (state.deposits || []).filter(dep =>
    dep.discovered && String(dep.discoverer_id || "") === String(citizenId)
  );
}

function knowledgeCacheFresh(entry) {
  return entry && (Date.now() - entry.loadedAt) < KNOWLEDGE_REFRESH_MS;
}

async function loadCitizenKnowledge(citizenId, { force = false } = {}) {
  const key = `citizen:${citizenId}`;
  const cached = citizenKnowledgeCache.get(citizenId);
  if (!force && knowledgeCacheFresh(cached)) return cached.data;
  if (knowledgeLoading.has(key)) return cached?.data || null;

  knowledgeLoading.add(key);
  try {
    const response = await fetch(`/api/knowledge/citizens/${encodeURIComponent(citizenId)}?limit=12`);
    if (!response.ok) throw new Error("knowledge endpoint unavailable");
    const data = await response.json();
    citizenKnowledgeCache.set(citizenId, { data, loadedAt: Date.now(), unavailable: false });
    if (sheetCitizenId === citizenId) renderCitizenSheet();
    return data;
  } catch {
    citizenKnowledgeCache.set(citizenId, {
      data: null,
      loadedAt: Date.now(),
      unavailable: true,
    });
    if (sheetCitizenId === citizenId) renderCitizenSheet();
    return null;
  } finally {
    knowledgeLoading.delete(key);
  }
}

async function loadLocationKnowledge(locationId, { force = false } = {}) {
  const key = `location:${locationId}`;
  const cached = locationKnowledgeCache.get(locationId);
  if (!force && knowledgeCacheFresh(cached)) return cached.data;
  if (knowledgeLoading.has(key)) return cached?.data || null;

  knowledgeLoading.add(key);
  try {
    const response = await fetch(`/api/knowledge/locations/${encodeURIComponent(locationId)}`);
    if (!response.ok) throw new Error("knowledge endpoint unavailable");
    const data = await response.json();
    locationKnowledgeCache.set(locationId, { data, loadedAt: Date.now(), unavailable: false });
    if (focusedLocation === locationId) renderLocationSheet();
    return data;
  } catch {
    locationKnowledgeCache.set(locationId, {
      data: null,
      loadedAt: Date.now(),
      unavailable: true,
    });
    if (focusedLocation === locationId) renderLocationSheet();
    return null;
  } finally {
    knowledgeLoading.delete(key);
  }
}

function continuityCacheFresh(entry) {
  return entry && (Date.now() - entry.loadedAt) < CONTINUITY_REFRESH_MS;
}

async function loadCitizenContinuity(citizenId, { force = false } = {}) {
  const cached = citizenContinuityCache.get(citizenId);
  if (!force && continuityCacheFresh(cached)) return cached.data;
  if (continuityLoading.has(citizenId)) return cached?.data || null;

  continuityLoading.add(citizenId);
  try {
    const objectiveResponse = await fetch(`/api/continuity/${encodeURIComponent(citizenId)}`);
    if (!objectiveResponse.ok) throw new Error("continuity endpoint unavailable");
    const objective = await objectiveResponse.json();

    const memoryResponse = await fetch(`/api/memory/continuity/${encodeURIComponent(citizenId)}?limit=8`);
    if (!memoryResponse.ok) throw new Error("continuity memory endpoint unavailable");
    const memory = await memoryResponse.json();

    const competenceResponse = await fetch(`/api/competence/${encodeURIComponent(citizenId)}`);
    if (!competenceResponse.ok) throw new Error("competence endpoint unavailable");
    const competence = await competenceResponse.json();

    const patternsResponse = await fetch(`/api/memory/patterns/${encodeURIComponent(citizenId)}`);
    if (!patternsResponse.ok) throw new Error("history-pattern endpoint unavailable");
    const patterns = await patternsResponse.json();

    const openPlans = (objective.plans || [])
      .filter(plan => ["active", "paused"].includes(String(plan.status)))
      .slice(0, 4);
    const planMemories = {};
    await Promise.all(openPlans.map(async plan => {
      try {
        const response = await fetch(
          `/api/memory/continuity/${encodeURIComponent(citizenId)}?plan_id=${encodeURIComponent(plan.id)}&limit=6`
        );
        if (!response.ok) return;
        const payload = await response.json();
        planMemories[String(plan.id)] = payload.events || [];
      } catch {
        // Plan-specific remembered perspective is optional presentation data.
      }
    }));

    const data = { objective, memory, competence, patterns, planMemories };
    citizenContinuityCache.set(citizenId, { data, loadedAt: Date.now(), unavailable: false });
    if (sheetCitizenId === citizenId) renderCitizenSheet();
    return data;
  } catch {
    citizenContinuityCache.set(citizenId, {
      data: null,
      loadedAt: Date.now(),
      unavailable: true,
    });
    if (sheetCitizenId === citizenId) renderCitizenSheet();
    return null;
  } finally {
    continuityLoading.delete(citizenId);
  }
}

function continuityMemoryRow(event) {
  const verification = String(event?.verification || event?.status || "remembered");
  const source = event?.source_type && event?.source_id != null
    ? `${event.source_type} #${event.source_id}`
    : "source unavailable";
  const planLinked = event?.pinned_by_plan ? "<em>Plan-linked</em>" : "";
  const role = String(event?.source_role || "").trim();
  const facets = Array.isArray(event?.facets) ? event.facets : [];
  const counterpartyId = facets.find(f => String(f?.kind) === "counterparty")?.value;
  const family = facets.find(f => String(f?.kind) === "competence_family")?.value;
  const perspectiveBits = [
    role && role !== "actor" ? role.replaceAll("_", " ") : "",
    counterpartyId ? `with ${citizenNameById(counterpartyId)}` : "",
    family ? String(family).replaceAll("_", " ") : "",
  ].filter(Boolean);

  return `
    <div class="continuity-memory-row">
      <div class="continuity-row-head">
        <span class="knowledge-status">${escapeHtml(verification)}</span>
        <time>${escapeHtml(event?.sim_label || formatMinute(event?.sim_minute || 0))}</time>
      </div>
      <p>${escapeHtml(event?.summary || "Remembered event")}</p>
      ${perspectiveBits.length ? `<div class="continuity-memory-context">${perspectiveBits.map(bit => `<span>${escapeHtml(bit)}</span>`).join("")}</div>` : ""}
      <div class="knowledge-source">
        <span>${escapeHtml(source)}</span>
        ${planLinked}
      </div>
    </div>
  `;
}

function citizenContinuityMarkup(citizenId, section = "continuity") {
  const entry = citizenContinuityCache.get(citizenId);
  if (!entry) {
    loadCitizenContinuity(citizenId);
    return '<div class="sheet-empty muted">Loading continuity…</div>';
  }
  if (!continuityCacheFresh(entry)) loadCitizenContinuity(citizenId);
  if (!entry.data) {
    return '<div class="sheet-empty muted">Continuity read models are not available in this runtime.</div>';
  }

  const objective = entry.data.objective || {};
  const generalMemory = entry.data.memory?.events || [];
  const competence = entry.data.competence || {};
  const competenceFamilies = Array.isArray(competence.families) ? competence.families : [];
  const guidedSessions = Array.isArray(competence.guided_practice_sessions) ? competence.guided_practice_sessions : [];
  const patterns = entry.data.patterns || {};
  const recurringChoices = Array.isArray(patterns.habits) ? patterns.habits : [];
  const placeContinuity = Array.isArray(patterns.places) ? patterns.places : [];
  const socialPatterns = Array.isArray(patterns.customs) ? patterns.customs : [];
  const planMemories = entry.data.planMemories || {};
  const plans = objective.plans || [];
  const openPlans = plans.filter(plan => ["active", "paused"].includes(String(plan.status)));
  const practice = objective.practice_events || [];

  const planMarkup = openPlans.length ? openPlans.map(plan => {
    const memories = planMemories[String(plan.id)] || [];
    const transitions = (plan.transitions || []).slice(0, 5);
    const whyMarkup = memories.length
      ? memories.map(continuityMemoryRow).join("")
      : '<div class="sheet-empty muted">No currently recalled source details are available for this plan.</div>';
    const transitionMarkup = transitions.length
      ? transitions.map(row => `
          <div class="sheet-note">
            <time>${escapeHtml(formatMinute(row.sim_minute))}</time>
            <span>${escapeHtml(row.summary || row.transition_type || "Plan changed")}</span>
          </div>
        `).join("")
      : '<div class="sheet-empty muted">No recorded plan transitions.</div>';

    return `
      <div class="continuity-plan">
        <div class="continuity-plan-head">
          <strong>${escapeHtml(plan.current_intent || `Plan #${plan.id}`)}</strong>
          <em class="status-chip status-${escapeHtml(plan.status)}">${escapeHtml(statusLabel(plan.status))}</em>
        </div>
        <p><b>Next known step:</b> ${escapeHtml(plan.next_step || "Not specified")}</p>
        ${plan.unresolved_question ? `<p><b>Open question:</b> ${escapeHtml(plan.unresolved_question)}</p>` : ""}
        <small>Plan #${escapeHtml(String(plan.id))} • created ${escapeHtml(formatMinute(plan.created_minute))} • last changed ${escapeHtml(formatMinute(plan.updated_minute))}</small>
        <details>
          <summary>Why this exists</summary>
          <div class="continuity-memory-list">${whyMarkup}</div>
        </details>
        <details>
          <summary>Plan history</summary>
          <div class="sheet-notes">${transitionMarkup}</div>
        </details>
      </div>
    `;
  }).join("") : '<div class="sheet-empty muted">No active or paused persistent plans.</div>';

  const counts = new Map();
  for (const event of practice) {
    const activity = String(event.activity_type || "other").replaceAll("_", " ");
    counts.set(activity, (counts.get(activity) || 0) + 1);
  }
  const countMarkup = [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 8)
    .map(([activity, count]) => `
      <div class="sheet-list-row">
        <span>${escapeHtml(activity)}</span>
        <strong>${count} recorded event${count === 1 ? "" : "s"}</strong>
      </div>
    `).join("") || '<div class="sheet-empty muted">No recorded physical practice yet.</div>';

  const practiceRows = practice.slice(0, 6).map(event => `
    <div class="sheet-list-row">
      <span>
        <strong>${escapeHtml(String(event.activity_type || "work").replaceAll("_", " "))}</strong>
        <small>${event.location_id ? `${escapeHtml(locationNameById(event.location_id))} • ` : ""}${escapeHtml(formatMinute(event.completed_minute))}</small>
      </span>
      <em>${escapeHtml(event.outcome || event.job_status || "recorded")}</em>
    </div>
  `).join("") || '<div class="sheet-empty muted">No recent practice events.</div>';

  const competenceMarkup = competenceFamilies
    .filter(row => Number(row.practice_count || 0) > 0)
    .sort((a, b) => Number(b.practice_count || 0) - Number(a.practice_count || 0) || String(a.family).localeCompare(String(b.family)))
    .map(row => {
      const family = String(row.family || "work").replaceAll("_", " ");
      const practiceCount = Number(row.practice_count || 0);
      const completedCount = Number(row.completed_count || 0);
      const failedCount = Number(row.failed_count || 0);
      const reduction = Math.max(0, Number(row.duration_reduction_percent || 0));
      return `
        <div class="continuity-practice-family">
          <div class="continuity-practice-head">
            <strong>${escapeHtml(family)}</strong>
            <span>${practiceCount} recorded event${practiceCount === 1 ? "" : "s"}</span>
          </div>
          <small>${completedCount} completed${failedCount ? ` • ${failedCount} failed` : ""}</small>
          ${reduction > 0 ? `<p class="continuity-measured-effect"><b>Measured work effect:</b> comparable ${escapeHtml(family)} tasks are currently ${escapeHtml(trimNumber(reduction))}% shorter from prior practice.</p>` : ""}
        </div>
      `;
    }).join("") || '<div class="sheet-empty muted">No recorded practice families yet.</div>';

  const guidedMarkup = guidedSessions.slice(0, 8).map(session => {
    const isGuide = String(session.teacher_id) === String(citizenId);
    const counterpartId = isGuide ? session.learner_id : session.teacher_id;
    const counterpart = citizenNameById(counterpartId);
    const family = String(session.activity_family || "guided practice").replaceAll("_", " ");
    const minute = session.completed_minute ?? session.started_minute;
    const roleLine = isGuide
      ? `Guided ${counterpart}`
      : `Practiced with ${counterpart}`;
    return `
      <div class="continuity-guided-row">
        <span>
          <strong>${escapeHtml(family)}</strong>
          <small>${escapeHtml(roleLine)} • ${escapeHtml(formatMinute(minute))}</small>
        </span>
        <em class="status-chip status-${escapeHtml(String(session.status || "recorded"))}">${escapeHtml(statusLabel(session.status || "recorded"))}</em>
      </div>
    `;
  }).join("") || '<div class="sheet-empty muted">No guided-practice sessions recorded.</div>';

  const memoryMarkup = generalMemory.length
    ? generalMemory.map(continuityMemoryRow).join("")
    : '<div class="sheet-empty muted">No relevant active memories are available right now.</div>';

  const recurringChoiceMarkup = recurringChoices.slice(0, 8).map(item => {
    const action = String(item.action_key || "choice").replaceAll("_", " ");
    const evidenceState = String(item.state || "recorded").replaceAll("_", " ");
    const supportSources = Array.isArray(item.support_sources) ? item.support_sources : [];
    const contrarySources = Array.isArray(item.recent_contrary_sources) ? item.recent_contrary_sources : [];
    const sourceMarkup = supportSources.map(source => `
      <span class="continuity-source-chip">${escapeHtml(source.type || "source")} #${escapeHtml(String(source.id ?? "?"))}</span>
    `).join("");
    const contraryMarkup = contrarySources.map(source => `
      <span class="continuity-source-chip contrary">${escapeHtml(String(source.action_key || "other choice").replaceAll("_", " "))} • ${escapeHtml(source.type || "source")} #${escapeHtml(String(source.id ?? "?"))}</span>
    `).join("");
    return `
      <div class="continuity-pattern-row">
        <div class="continuity-pattern-head">
          <strong>${escapeHtml(action)}</strong>
          <span class="continuity-evidence-state">${escapeHtml(evidenceState)} evidence</span>
        </div>
        <small>${Number(item.support_count || 0)} source-backed choice${Number(item.support_count || 0) === 1 ? "" : "s"} across ${Number(item.distinct_days || 0)} simulation day${Number(item.distinct_days || 0) === 1 ? "" : "s"} • latest ${escapeHtml(item.latest_support_label || formatMinute(item.latest_support_minute || 0))}</small>
        <p><b>Context:</b> ${escapeHtml(String(item.context_key || "source context unavailable").replaceAll("_", " "))}</p>
        <details>
          <summary>Evidence trail</summary>
          <div class="continuity-source-list">
            ${sourceMarkup || '<span class="muted">No source rows exposed.</span>'}
            ${contraryMarkup ? `<div class="continuity-contrary"><small>Recent contrary choices</small>${contraryMarkup}</div>` : ""}
          </div>
        </details>
      </div>
    `;
  }).join("") || '<div class="sheet-empty muted">No recurring voluntary-choice evidence currently qualifies.</div>';

  const placeContinuityMarkup = placeContinuity.slice(0, 8).map(item => {
    const evidence = Array.isArray(item.evidence) ? item.evidence : [];
    const evidenceMarkup = evidence.slice(-6).map(row => `
      <div class="continuity-place-event">
        <time>${escapeHtml(formatMinute(row.sim_minute || 0))}</time>
        <span>${escapeHtml(row.summary || row.event_kind || "Remembered place event")}</span>
        <small>${escapeHtml(row.source_type || "source")} #${escapeHtml(String(row.source_id ?? "?"))}</small>
      </div>
    `).join("");
    return `
      <div class="continuity-pattern-row">
        <div class="continuity-pattern-head">
          <strong>${escapeHtml(locationNameById(item.location_id || ""))}</strong>
          <span>${Number(item.evidence_count || 0)} retained source${Number(item.evidence_count || 0) === 1 ? "" : "s"}</span>
        </div>
        <small>Latest retained evidence ${escapeHtml(item.latest_label || formatMinute(item.latest_minute || 0))}</small>
        <p class="muted">Personal continuity evidence only. This does not mark a favorite, home, safe, or sacred place.</p>
        <details>
          <summary>Place evidence trail</summary>
          <div class="continuity-place-events">${evidenceMarkup || '<div class="muted">No place source rows exposed.</div>'}</div>
        </details>
      </div>
    `;
  }).join("") || '<div class="sheet-empty muted">No place continuity evidence currently qualifies.</div>';

  const socialPatternMarkup = socialPatterns.slice(0, 8).map(item => {
    const actors = Array.isArray(item.distinct_actors) ? item.distinct_actors : [];
    const modes = Array.isArray(item.transmission_modes) ? item.transmission_modes : [];
    const verifications = Array.isArray(item.verification_states) ? item.verification_states : [];
    const sources = Array.isArray(item.sources) ? item.sources : [];
    const sourceMarkup = sources.map(source => `
      <div class="continuity-social-source">
        <span>${escapeHtml(citizenNameById(source.actor_id || ""))} • ${escapeHtml(String(source.mode || "observed").replaceAll("_", " "))}</span>
        <small>${escapeHtml(source.verification || "unverified")} • ${escapeHtml(source.type || "source")} #${escapeHtml(String(source.id ?? "?"))}</small>
      </div>
    `).join("");
    return `
      <div class="continuity-pattern-row">
        <div class="continuity-pattern-head">
          <strong>${escapeHtml(String(item.pattern_key || "recurring social pattern").replaceAll("_", " "))}</strong>
          <span>${Number(item.evidence_count || 0)} source event${Number(item.evidence_count || 0) === 1 ? "" : "s"}</span>
        </div>
        <small>${actors.length} actor${actors.length === 1 ? "" : "s"} • ${modes.map(mode => String(mode).replaceAll("_", " ")).join(", ") || "transmission recorded"} • latest ${escapeHtml(item.latest_label || formatMinute(item.latest_minute || 0))}</small>
        <p class="muted">Owner-perspective social evidence only. It is not an authoritative tradition or culture fact.</p>
        ${verifications.length ? `<div class="continuity-verification-line">Verification represented: ${verifications.map(value => escapeHtml(value)).join(", ")}</div>` : ""}
        <details>
          <summary>Social source trail</summary>
          <div class="continuity-social-sources">${sourceMarkup || '<div class="muted">No social source rows exposed.</div>'}</div>
        </details>
      </div>
    `;
  }).join("") || '<div class="sheet-empty muted">No socially transmitted recurring pattern evidence currently qualifies.</div>';

  if (section === "memories") {
    return `
      <div class="continuity-layer remembered">
        <div class="continuity-layer-head">
          <span>Remembered Perspective</span>
          <small>Citizen-scoped active recall</small>
        </div>
        <h4>Relevant memories</h4>
        <div class="continuity-memory-list">${memoryMarkup}</div>
      </div>
    `;
  }

  if (section === "experience") {
    return `
      <div class="continuity-layer">
        <div class="continuity-layer-head">
          <span>Experience / Practice</span>
          <small>Simulation-owned evidence</small>
        </div>
        <h4>Recorded practice</h4>
        <div class="sheet-list">${countMarkup}</div>
        <div class="continuity-practice-families">${competenceMarkup}</div>
        <details>
          <summary>Recent practice events</summary>
          <div class="sheet-list">${practiceRows}</div>
        </details>
        <h4>Guided practice history</h4>
        <div class="continuity-guided-list">${guidedMarkup}</div>
      </div>
    `;
  }

  if (section === "patterns") {
    return `
      <div class="continuity-layer remembered">
        <div class="continuity-layer-head">
          <span>Patterns & Place</span>
          <small>Revisable historical evidence</small>
        </div>
        <h4>Recurring choice evidence</h4>
        <p class="continuity-layer-note">Repeated voluntary choices are shown as source-backed evidence states, not traits or preferences.</p>
        <div class="continuity-pattern-list">${recurringChoiceMarkup}</div>
        <h4>Place continuity</h4>
        <div class="continuity-pattern-list">${placeContinuityMarkup}</div>
        <h4>Social pattern evidence</h4>
        <div class="continuity-pattern-list">${socialPatternMarkup}</div>
      </div>
    `;
  }

  return `
    <div class="continuity-layer">
      <div class="continuity-layer-head">
        <span>Evidence / Record</span>
        <small>Simulation-owned continuity</small>
      </div>
      <h4>Ongoing plans</h4>
      <div class="continuity-plan-list">${planMarkup}</div>
    </div>
    <div class="continuity-layer interpretation">
      <div class="continuity-layer-head">
        <span>Citizen Interpretation</span>
        <small>Not an objective stat</small>
      </div>
      <p class="muted">Source-backed self-reflection remains Communication-owned and attributed. Measured work effects and event counts are evidence, not personality or expertise. Agent City does not infer expertise, rank, friendship, preference, favorite places, or traditions from event counts. Recurring-choice, place, and social-pattern evidence remain revisable history, not identity. Guided-practice event roles do not create permanent guide identities.</p>
    </div>
  `;
}

function knowledgeFactMarkup(fact) {
  const metadata = fact?.metadata || {};
  const verification = String(fact?.verification || fact?.status || "unverified");
  const source = fact?.source_type && fact?.source_id != null
    ? `${fact.source_type} #${fact.source_id}`
    : "source unavailable";
  const channel = metadata.channel ? String(metadata.channel).replaceAll("_", " ") : "";
  const time = fact?.sim_label || (fact?.sim_minute != null ? formatMinute(fact.sim_minute) : "");

  return `
    <div class="knowledge-fact ${verification === "verified" ? "verified" : "unverified"}">
      <div class="knowledge-fact-head">
        <span class="knowledge-status">${escapeHtml(verification)}</span>
        ${time ? `<time>${escapeHtml(time)}</time>` : ""}
      </div>
      <p>${escapeHtml(fact?.summary || "Knowledge record")}</p>
      <div class="knowledge-source">
        <span>${escapeHtml(source)}</span>
        ${channel ? `<span>${escapeHtml(channel)}</span>` : ""}
      </div>
    </div>
  `;
}

function citizenKnowledgeMarkup(citizenId) {
  const entry = citizenKnowledgeCache.get(citizenId);
  if (!entry) {
    loadCitizenKnowledge(citizenId);
    return '<div class="sheet-empty muted">Loading bounded knowledge…</div>';
  }
  if (!knowledgeCacheFresh(entry)) loadCitizenKnowledge(citizenId);
  if (!entry.data) {
    const fallback = personalDiscoveriesForCitizen(citizenId);
    return fallback.length
      ? fallback.map(dep => `
          <div class="knowledge-fact verified">
            <div class="knowledge-fact-head"><span class="knowledge-status">verified</span></div>
            <p>Personally confirmed ${escapeHtml(dep.material)} at ${escapeHtml(locationNameById(dep.location_id))}.</p>
            <div class="knowledge-source"><span>legacy physical discovery record</span></div>
          </div>
        `).join("")
      : '<div class="sheet-empty muted">No bounded knowledge records are available in this runtime.</div>';
  }

  const facts = entry.data.facts || [];
  return facts.length
    ? facts.map(knowledgeFactMarkup).join("")
    : '<div class="sheet-empty muted">No retained knowledge matching this citizen yet.</div>';
}

function locationKnowledgeMarkup(locationId) {
  const entry = locationKnowledgeCache.get(locationId);
  if (!entry) {
    loadLocationKnowledge(locationId);
    return '<div class="sheet-empty muted">Loading citizen knowledge for this location…</div>';
  }
  if (!knowledgeCacheFresh(entry)) loadLocationKnowledge(locationId);
  if (!entry.data) {
    return '<div class="sheet-empty muted">The bounded location-knowledge read model is not available in this runtime.</div>';
  }

  const citizenViews = (entry.data.citizens || []).filter(view => (view.facts || []).length);
  if (!citizenViews.length) {
    return '<div class="sheet-empty muted">No citizen has retained location knowledge here yet.</div>';
  }

  return citizenViews.map(view => `
    <section class="location-knowledge-citizen">
      <div class="location-knowledge-citizen-head">
        <strong>${escapeHtml(view.citizen_name)}</strong>
        <span>${view.facts.length} known fact${view.facts.length === 1 ? "" : "s"}</span>
      </div>
      <div class="knowledge-facts">
        ${view.facts.map(knowledgeFactMarkup).join("")}
      </div>
    </section>
  `).join("");
}

function renderCitizenDirectory() {
  if (!state?.citizens?.length) {
    els.citizenDirectory.innerHTML = '<div class="muted">No citizens available.</div>';
    return;
  }
  if (!sheetCitizenId || !state.citizens.some(c => c.id === sheetCitizenId)) {
    sheetCitizenId = selectedCitizen || state.citizens[0].id;
  }

  els.citizenDirectory.innerHTML = state.citizens.map(c => {
    const job = activeJobFor(c.id);
    const destination = job?.action === "travel" ? locationById(job.target)?.name : null;
    const where = destination ? `Traveling to ${destination}` : c.location;
    return `
      <button class="directory-row ${sheetCitizenId === c.id ? "selected" : ""}" onclick="openCitizenSheet('${c.id}')">
        ${citizenAvatarMarkup(c, "directory")}
        <span>
          <strong>${escapeHtml(c.name)}</strong>
          <small>${escapeHtml(c.current_activity)} • ${escapeHtml(where)}</small>
        </span>
      </button>
    `;
  }).join("");
}

window.openCitizenSheet = function(id) {
  if (!state?.citizens?.some(c => c.id === id)) return;
  sheetCitizenId = id;
  renderCitizenDirectory();
  renderCitizenSheet();
  loadCitizenKnowledge(id);
  loadCitizenContinuity(id);
};

window.openCitizenDetail = function(view) {
  const valid = new Set(["continuity", "memories", "experience", "patterns", "social", "knowledge"]);
  citizenDetailView = valid.has(view) ? view : "continuity";
  localStorage.setItem("agentCityCitizenDetailView", citizenDetailView);
  renderCitizenSheet();
};

function renderCitizenSheet() {
  const citizen = state?.citizens?.find(c => c.id === sheetCitizenId);
  if (!citizen) return;

  const job = activeJobFor(citizen.id);
  const progress = jobProgress(job);
  const destination = job?.action === "travel" ? locationById(job.target)?.name : null;
  const locationText = destination ? `Traveling: ${citizen.location} → ${destination}` : citizen.location;
  const cargo = cargoRowsForCitizen(citizen.id);
  const cargoTotal = cargo.reduce((sum, row) => sum + Number(row.amount || 0), 0);
  const gear = equipmentForCitizen(citizen.id);
  const projects = projectsForCitizen(citizen.id).slice(0, 6);
  const recentHistory = (state.history || [])
    .filter(row => String(row.message || "").startsWith(citizen.name))
    .slice(0, 5);
  const experimentResults = (state.experiment_results || [])
    .filter(row => String(row.citizen_id) === String(citizen.id))
    .slice(0, 6);
  const learnedProcesses = (state.learned_processes || [])
    .filter(row => String(row.citizen_id) === String(citizen.id))
    .slice(0, 6);
  const cargoCapacity = Number(citizen.cargo_capacity);
  const batteryHealth = Number(citizen.battery_health);
  const usableEnergyCapacity = Number(citizen.usable_energy_capacity);
  const jointWear = Number(citizen.joint_wear);

  applyCitizenPortrait(citizen);
  els.citizenSheetName.textContent = citizen.name;
  els.citizenSheetRole.textContent = citizen.aptitude;
  els.citizenSheetVisit.disabled = false;
  els.citizenSheetVisit.dataset.citizenId = citizen.id;

  const activeJobMarkup = job ? `
    <div class="sheet-card">
      <span class="sheet-label">Current work</span>
      <strong>${escapeHtml(citizen.current_activity)}</strong>
      <p>${escapeHtml(job.action)}${job.target ? ` • ${escapeHtml(String(job.target))}` : ""}</p>
      ${progress ? `<div class="job-progress-track"><span style="width:${progress.percent}%"></span></div><small>${progress.percent}% • ETA ${escapeHtml(formatMinute(job.end_minute))}</small>` : ""}
    </div>
  ` : `
    <div class="sheet-card">
      <span class="sheet-label">Current work</span>
      <strong>${escapeHtml(citizen.current_activity)}</strong>
      <p>No active physical job.</p>
    </div>
  `;

  const gearMarkup = gear.length ? gear.map(item => {
    const effectiveCargo = Number(item.effective_cargo_bonus || 0);
    const effectiveExtraction = Number(item.effective_extraction_speed_multiplier || 1);
    const stateLabel = conditionStateLabel(item.condition_state);
    return `
      <div class="sheet-list-row maintenance-row ${item.operational === false ? "non-operational" : ""}">
        <span>
          <strong>${escapeHtml(item.name)}</strong>
          <small>${escapeHtml(item.kind || "equipment")} • ${trimNumber(item.condition)}% • ${escapeHtml(stateLabel)}</small>
        </span>
        <span class="sheet-badges">
          ${item.operational === false ? "<em class=\"maintenance-badge critical\">Non-operational</em>" : ""}
          ${item.service_due ? "<em class=\"maintenance-badge service\">Service due</em>" : ""}
          ${effectiveCargo !== 0 ? `<em>Cargo +${escapeHtml(trimNumber(effectiveCargo))}</em>` : ""}
          ${effectiveExtraction !== 1 ? `<em>${escapeHtml(trimNumber(effectiveExtraction))}× extract</em>` : ""}
        </span>
      </div>
    `;
  }).join("") : '<div class="sheet-empty muted">No validated personal equipment.</div>';

  const cargoMarkup = cargo.length ? cargo.map(row => `
    <div class="sheet-list-row"><span>${escapeHtml(row.material)}</span><strong>${escapeHtml(trimNumber(row.amount))}</strong></div>
  `).join("") : '<div class="sheet-empty muted">No cargo carried.</div>';

  const projectMarkup = projects.length ? projects.map(project => `
    <div class="sheet-list-row">
      <span><strong>${escapeHtml(project.name)}</strong><small>Project #${escapeHtml(String(project.id))}</small></span>
      <em class="status-chip status-${escapeHtml(project.status)}">${escapeHtml(statusLabel(project.status))}</em>
    </div>
  `).join("") : '<div class="sheet-empty muted">No created projects.</div>';

  const historyMarkup = recentHistory.length ? recentHistory.map(row => `
    <div class="sheet-note"><time>${escapeHtml(formatMinute(row.sim_minute))}</time><span>${escapeHtml(row.message)}</span></div>
  `).join("") : '<div class="sheet-empty muted">No recent personal chronology entries.</div>';

  const experimentMarkup = experimentResults.length ? experimentResults.map(row => `
    <div class="sheet-list-row">
      <span>
        <strong>${escapeHtml(String(row.method || "Experiment").replaceAll("_", " "))}</strong>
        <small>${escapeHtml(row.material || "unknown material")} • ${escapeHtml(formatMinute(row.completed_minute))}</small>
      </span>
      <em>${escapeHtml(row.outcome || "recorded")}</em>
    </div>
  `).join("") : '<div class="sheet-empty muted">No recorded experiments yet.</div>';

  const processMarkup = learnedProcesses.length ? learnedProcesses.map(row => `
    <div class="sheet-list-row">
      <span>
        <strong>${escapeHtml(row.name || row.process_key || "Learned process")}</strong>
        <small>Learned ${escapeHtml(formatMinute(row.learned_minute))}</small>
      </span>
      <em>${escapeHtml(row.process_kind || "process")}</em>
    </div>
  `).join("") : '<div class="sheet-empty muted">No reproducible learned processes yet.</div>';

  const continuityData = citizenContinuityCache.get(citizen.id)?.data || null;
  const objective = continuityData?.objective || {};
  const memoryEvents = continuityData?.memory?.events || [];
  const practiceEvents = objective.practice_events || [];
  const guidedSessions = continuityData?.competence?.guided_practice_sessions || [];
  const patterns = continuityData?.patterns || {};
  const patternCount =
    (patterns.habits || []).length +
    (patterns.places || []).length +
    (patterns.customs || []).length;
  const openPlans = (objective.plans || []).filter(plan =>
    ["active", "paused"].includes(String(plan.status))
  );
  const knowledgeFacts = citizenKnowledgeCache.get(citizen.id)?.data?.facts || [];
  const socialRows = (state.citizen_conversations || [])
    .filter(row =>
      String(row.initiator_id) === String(citizen.id) ||
      String(row.target_id) === String(citizen.id)
    )
    .slice(0, 8);

  const activePlanOverview = openPlans.length
    ? `
      <div class="sheet-list-row">
        <span>
          <strong>${escapeHtml(openPlans[0].current_intent || `Plan #${openPlans[0].id}`)}</strong>
          <small>${escapeHtml(statusLabel(openPlans[0].status))} • next: ${escapeHtml(openPlans[0].next_step || "Not specified")}</small>
        </span>
        ${openPlans.length > 1 ? `<em>${openPlans.length} open plans</em>` : ""}
      </div>
    `
    : continuityLoading.has(citizen.id)
      ? '<div class="sheet-empty muted">Loading plan continuity…</div>'
      : '<div class="sheet-empty muted">No active or paused persistent plan.</div>';

  const socialMarkup = socialRows.length ? socialRows.map(row => {
    const otherId = String(row.initiator_id) === String(citizen.id)
      ? row.target_id
      : row.initiator_id;
    return `
      <div class="citizen-social-row">
        <div>
          <strong>${escapeHtml(citizenNameById(otherId))}</strong>
          <small>${escapeHtml(row.location_name || locationNameById(row.location_id || ""))} • ${escapeHtml(formatMinute(row.sim_minute || 0))}</small>
        </div>
        <p>${escapeHtml(row.summary || "Conversation recorded.")}</p>
      </div>
    `;
  }).join("") : '<div class="sheet-empty muted">No recent citizen conversation records are in the current bounded snapshot.</div>';

  const knowledgePanelMarkup = `
    <div class="citizen-detail-stack">
      <section>
        <h4>Known discoveries & retained knowledge</h4>
        <div class="knowledge-facts">${citizenKnowledgeMarkup(citizen.id)}</div>
      </section>
      <section>
        <h4>Experiments</h4>
        <div class="sheet-list">${experimentMarkup}</div>
      </section>
      <section>
        <h4>Learned processes</h4>
        <div class="sheet-list">${processMarkup}</div>
      </section>
    </div>
  `;

  const detailViews = {
    continuity: {
      title: "Continuity",
      note: "Plans and interpretation remain traceable to source-backed history.",
      markup: citizenContinuityMarkup(citizen.id, "continuity"),
    },
    memories: {
      title: "Memories",
      note: "Active recall is citizen-scoped and may be smaller than the durable archive.",
      markup: citizenContinuityMarkup(citizen.id, "memories"),
    },
    experience: {
      title: "Experience",
      note: "Practice and guided-practice records are evidence, not levels or titles.",
      markup: citizenContinuityMarkup(citizen.id, "experience"),
    },
    patterns: {
      title: "Patterns & Places",
      note: "Recurring choices, place continuity, and social-pattern evidence stay revisable.",
      markup: citizenContinuityMarkup(citizen.id, "patterns"),
    },
    social: {
      title: "Social",
      note: "Recent face-to-face exchange history from the bounded civilization snapshot.",
      markup: `<div class="citizen-social-list">${socialMarkup}</div>`,
    },
    knowledge: {
      title: "Knowledge",
      note: "Verified discoveries, experiments, and learned processes available to this citizen.",
      markup: knowledgePanelMarkup,
    },
  };
  const detail = detailViews[citizenDetailView] || detailViews.continuity;

  const detailButtons = [
    ["continuity", "Continuity", openPlans.length],
    ["memories", "Memories", memoryEvents.length],
    ["experience", "Experience", practiceEvents.length + guidedSessions.length],
    ["patterns", "Patterns & Places", patternCount],
    ["social", "Social", socialRows.length],
    ["knowledge", "Knowledge", knowledgeFacts.length + experimentResults.length + learnedProcesses.length],
  ].map(([key, label, count]) => `
    <button
      type="button"
      class="citizen-detail-tab ${citizenDetailView === key ? "active" : ""}"
      onclick="openCitizenDetail('${key}')"
      aria-pressed="${citizenDetailView === key ? "true" : "false"}"
    >
      <span>${escapeHtml(label)}</span>
      <em>${Number(count) || 0}</em>
    </button>
  `).join("");

  els.citizenSheetBody.innerHTML = `
    <div class="citizen-sheet-dashboard">
      <section class="citizen-overview-column">
        <div class="citizen-overview-grid">
          <div class="sheet-card">
            <span class="sheet-label">Physical state</span>
            <strong>${escapeHtml(locationText)}</strong>
            ${citizenLiveVitalsMarkup(citizen)}
          </div>
          <div class="sheet-card">
            <span class="sheet-label">Long-term maintenance</span>
            <div class="maintenance-metric-grid">
              <div>
                <span>Battery health</span>
                <strong>${Number.isFinite(batteryHealth) ? `${escapeHtml(trimNumber(batteryHealth))}%` : "Unknown"}</strong>
                <small>${escapeHtml(conditionStateLabel(citizen.battery_state))}${citizen.battery_replacement_due ? " • replacement due" : ""} • not current charge</small>
              </div>
              <div>
                <span>Usable capacity</span>
                <strong>${Number.isFinite(usableEnergyCapacity) ? `${escapeHtml(trimNumber(usableEnergyCapacity))}%` : "Unknown"}</strong>
                <small>Long-term capacity, distinct from current charge</small>
              </div>
              <div>
                <span>Joint wear</span>
                <strong>${Number.isFinite(jointWear) ? escapeHtml(trimNumber(jointWear)) : "Unknown"}</strong>
                <small>${escapeHtml(conditionStateLabel(citizen.chassis_service_state))}${citizen.chassis_service_due ? " • service due" : ""}</small>
              </div>
              <div>
                <span>Last service</span>
                <strong>${citizen.last_service_minute != null ? escapeHtml(formatMinute(citizen.last_service_minute)) : "No recorded service"}</strong>
                <small>Validated physical service timestamp</small>
              </div>
            </div>
          </div>
          ${activeJobMarkup}
          <div class="sheet-card">
            <span class="sheet-label">Cargo</span>
            <strong>${Number.isFinite(cargoCapacity) ? `${escapeHtml(trimNumber(cargoTotal))} / ${escapeHtml(trimNumber(cargoCapacity))} units` : `${escapeHtml(trimNumber(cargoTotal))} units carried`}</strong>
            <div class="sheet-list">${cargoMarkup}</div>
          </div>
          <div class="sheet-card overview-wide">
            <span class="sheet-label">Equipped gear</span>
            <div class="sheet-list">${gearMarkup}</div>
          </div>
          <div class="sheet-card overview-wide">
            <span class="sheet-label">Projects</span>
            <div class="sheet-list">${projectMarkup}</div>
          </div>
          <div class="sheet-card overview-wide">
            <span class="sheet-label">Active plan</span>
            <div class="sheet-list">${activePlanOverview}</div>
          </div>
        </div>
      </section>

      <aside class="citizen-info-column">
        <div class="citizen-detail-nav" aria-label="Citizen information views">
          ${detailButtons}
        </div>
        <section class="citizen-detail-panel">
          <div class="citizen-detail-panel-head">
            <div>
              <span class="sheet-label">More information</span>
              <h3>${escapeHtml(detail.title)}</h3>
            </div>
          </div>
          <p class="citizen-detail-note">${escapeHtml(detail.note)}</p>
          <div class="citizen-detail-content">${detail.markup}</div>
        </section>
      </aside>
    </div>
  `;
}

function renderLocationDirectory() {
  if (!state?.locations?.length) {
    els.locationDirectory.innerHTML = '<div class="muted">No known locations.</div>';
    return;
  }
  if (!focusedLocation || !state.locations.some(loc => loc.id === focusedLocation)) {
    focusedLocation = state.locations[0].id;
  }

  els.locationDirectory.innerHTML = state.locations.map(loc => {
    const known = depositsForLocation(loc.id);
    return `
      <button class="directory-row ${focusedLocation === loc.id ? "selected" : ""}" onclick="openLocationSheet('${loc.id}')">
        <span class="directory-token location-token">◎</span>
        <span>
          <strong>${escapeHtml(loc.name)}</strong>
          <small>${loc.surveyed ? "Surveyed" : "Not yet surveyed"}${known.length ? ` • ${known.length} known resource${known.length === 1 ? "" : "s"}` : ""}</small>
        </span>
      </button>
    `;
  }).join("");
}

window.openLocationSheet = function(id) {
  if (!state?.locations?.some(loc => loc.id === id)) return;
  focusedLocation = id;
  renderLocationDirectory();
  renderLocationSheet();
  loadLocationKnowledge(id);
};

function renderLocationSheet() {
  const loc = locationById(focusedLocation);
  if (!loc) return;

  const known = depositsForLocation(loc.id);
  const structures = (state.structures || []).filter(s => String(s.location_id || "") === String(loc.id));
  const projects = (state.projects || []).filter(p => String(p.location_id || "") === String(loc.id));
  const routes = (state.routes || []).filter(route => String(route.a) === String(loc.id));
  const present = citizensAtLocation(loc.id);
  const knownFacts = Array.isArray(loc.known_facts) ? loc.known_facts : [];
  const fieldFacts = knownFacts.filter(fact => fact.kind !== "deposit");

  els.locationSceneName.textContent = loc.name;
  els.locationSheetName.textContent = loc.name;
  els.locationSheetDescription.textContent = loc.description;
  els.locationSheetFocus.disabled = false;
  els.locationSheetFocus.dataset.locationId = loc.id;

  const resourcesMarkup = known.length ? known.map(dep => `
    <div class="sheet-list-row">
      <span><strong>${escapeHtml(dep.material)}</strong><small>Confirmed resource</small></span>
    </div>
  `).join("") : '<div class="sheet-empty muted">No resource discoveries are recorded here.</div>';

  const structureMarkup = structures.length ? structures.map(structure => `
    <div class="sheet-list-row">
      <span><strong>${escapeHtml(structure.name)}</strong><small>${escapeHtml(structure.kind || "structure")}</small></span>
      <span class="sheet-badges">${Number(structure.provides_charging || 0) === 1 ? "<em>Charging</em>" : ""}</span>
    </div>
  `).join("") : '<div class="sheet-empty muted">No validated structures at this location.</div>';

  const projectMarkup = projects.length ? projects.map(project => `
    <div class="sheet-list-row">
      <span><strong>${escapeHtml(project.name)}</strong><small>Project #${escapeHtml(String(project.id))}</small></span>
      <em class="status-chip status-${escapeHtml(project.status)}">${escapeHtml(statusLabel(project.status))}</em>
    </div>
  `).join("") : '<div class="sheet-empty muted">No projects at this location.</div>';

  const routeMarkup = routes.length ? routes.map(route => `
    <div class="sheet-list-row">
      <span>${escapeHtml(locationNameById(route.b))}</span>
      <strong>${escapeHtml(trimNumber(route.distance_km))} km</strong>
    </div>
  `).join("") : '<div class="sheet-empty muted">No known outgoing routes.</div>';

  const presentMarkup = present.length ? present.map(c => `
    <div class="sheet-list-row"><span><strong>${escapeHtml(c.name)}</strong><small>${escapeHtml(c.current_activity)}</small></span></div>
  `).join("") : '<div class="sheet-empty muted">No citizens currently present.</div>';

  const fieldFactsMarkup = fieldFacts.length ? fieldFacts.map(fact => {
    if (fact.kind === "property") {
      const unit = fact.unit ? ` ${fact.unit}` : "";
      return `<div class="sheet-list-row"><span><strong>${escapeHtml(String(fact.property_key || "property").replaceAll("_", " "))}</strong><small>Validated field property</small></span><strong>${escapeHtml(String(fact.value ?? ""))}${escapeHtml(unit)}</strong></div>`;
    }
    return `<div class="sheet-list-row"><span><strong>${escapeHtml(fact.label || "Validated field observation")}</strong></span></div>`;
  }).join("") : '<div class="sheet-empty muted">No additional validated field observations yet.</div>';

  els.locationSheetBody.innerHTML = `
    <div class="sheet-card">
      <span class="sheet-label">Survey state</span>
      <strong>${loc.surveyed ? "Surveyed" : "Not yet surveyed"}</strong>
      <p>Unknown resources and properties are omitted rather than shown as locked data.</p>
    </div>
    <div class="sheet-card">
      <span class="sheet-label">Present now</span>
      <div class="sheet-list">${presentMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Known field facts</span>
      <div class="sheet-list">${fieldFactsMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Known resources</span>
      <div class="sheet-list">${resourcesMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Structures</span>
      <div class="sheet-list">${structureMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Projects</span>
      <div class="sheet-list">${projectMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Known routes</span>
      <div class="sheet-list">${routeMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Citizen knowledge</span>
      <div class="location-knowledge-sections">${locationKnowledgeMarkup(loc.id)}</div>
    </div>
  `;
}

function renderRoutes() {
  const selected = selectedCitizen ? state.citizens.find(c => c.id === selectedCitizen) : null;
  const selectedJob = selected ? activeJobFor(selected.id) : null;
  const selectedTravel = selected && selectedJob?.action === "travel"
    ? { from: selected.location_id, to: selectedJob.target }
    : null;

  const labels = [];
  const routeLines = (state.routes || []).map(route => {
    const from = positionForLocation(route.a);
    const to = positionForLocation(route.b);
    const active = selectedTravel && sameRoute(route.a, route.b, selectedTravel.from, selectedTravel.to);
    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2;
    const distance = Number(route.distance_km);
    if (Number.isFinite(distance)) {
      labels.push(`
        <span class="route-distance ${active ? "active" : ""}" style="left:${midX}%; top:${midY}%;">
          ${escapeHtml(trimNumber(distance))} km
        </span>
      `);
    }
    return `<line class="${active ? "active-route" : ""}" x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" />`;
  });

  const localLines = [];
  if (spatialViewport) {
    for (const citizen of state.citizens || []) {
      const movement = localMovementForCitizen(citizen);
      if (!movement) continue;
      const start = metersToMap(movement.start_x_m, movement.start_y_m);
      const target = metersToMap(movement.target_x_m, movement.target_y_m);
      if (!start || !target) continue;
      localLines.push(`
        <line
          class="local-movement-route ${selectedCitizen === citizen.id ? "selected" : ""}"
          x1="${start.x}" y1="${start.y}" x2="${target.x}" y2="${target.y}"
        />
      `);
      if (selectedCitizen === citizen.id) {
        const midX = (start.x + target.x) / 2;
        const midY = (start.y + target.y) / 2;
        const distance = finiteNumber(movement.path_distance_m);
        labels.push(`
          <span class="local-movement-label" style="left:${midX}%; top:${midY}%;">
            ${distance != null ? `${escapeHtml(trimNumber(distance))} m` : "Local movement"}
          </span>
        `);
      }
    }
  }

  els.routeLayer.innerHTML = routeLines.join("") + localLines.join("");
  return labels.join("");
}

function physicalClusterOffset(citizen) {
  if (!spatialViewport || finiteNumber(citizen.position_x_m) == null || finiteNumber(citizen.position_y_m) == null) {
    return { x: 0, y: 0 };
  }
  const peers = (state.citizens || []).filter(peer => {
    const d = spatialDistanceMeters(citizen.position_x_m, citizen.position_y_m, peer.position_x_m, peer.position_y_m);
    return d != null && d <= 0.5;
  });
  if (peers.length <= 1) return { x: 0, y: 0 };
  const index = peers.findIndex(peer => peer.id === citizen.id);
  const offset = clusterOffset(Math.max(0, index), peers.length);
  const spread = 0.85 + (Math.min(mapZoomLevel, 4) * 0.18);
  return { x: offset.x * spread, y: offset.y * spread };
}

function citizenMapPlacement(citizen) {
  const movement = localMovementForCitizen(citizen);
  const job = activeJobFor(citizen.id);
  const x = finiteNumber(citizen.position_x_m);
  const y = finiteNumber(citizen.position_y_m);

  if (job?.action === "travel") {
    const progress = jobProgress(job);
    const fraction = progress?.fraction || 0;
    const route = (state.routes || []).find(r =>
      sameRoute(r.a, r.b, citizen.location_id, job.target)
    );
    const routeDistanceKm = Number(route?.distance_km);
    const remainingKm = Number.isFinite(routeDistanceKm)
      ? Math.max(0, routeDistanceKm * (1 - fraction))
      : null;
    const destination = locationById(job.target)?.name || job.target;
    return {
      pos: interpolatedPosition(citizen.location_id, job.target, fraction),
      offset: { x: 0, y: 0 },
      localMoving: false,
      routeTraveling: true,
      progress: progress?.percent || 0,
      remainingKm,
      label: remainingKm != null
        ? "traveling to " + destination + " • " + (progress?.percent || 0) + "% • " + trimNumber(remainingKm) + " km remaining"
        : "traveling to " + destination,
    };
  }

  if (spatialViewport && x != null && y != null) {
    const pos = metersToMap(x, y);
    const offset = physicalClusterOffset(citizen);
    return {
      pos,
      offset,
      localMoving: Boolean(movement),
      routeTraveling: false,
      progress: movement ? Math.round(clamp(Number(movement.progress) || 0, 0, 1) * 100) : null,
      label: movement
        ? `local ${String(movement.action || "movement").replaceAll("_", " ")}`
        : `x ${trimNumber(x)} m • y ${trimNumber(y)} m`,
    };
  }

  return {
    pos: positionForLocation(citizen.location_id),
    offset: { x: 0, y: 0 },
    localMoving: false,
    routeTraveling: false,
    progress: null,
    label: citizen.location || citizen.location_id,
  };
}

function renderSpatialObservations() {
  if (!spatialViewport) return "";

  const observations = [...(state.spatial_observations || [])]
    .filter(obs => finiteNumber(obs.x_m) != null && finiteNumber(obs.y_m) != null)
    .sort((a, b) => Number(a.observed_minute || 0) - Number(b.observed_minute || 0))
    .slice(-32);

  return observations.map(obs => {
    const pos = metersToMap(obs.x_m, obs.y_m);
    if (!pos) return "";
    const radius = Math.max(0.1, finiteNumber(obs.radius_m) || 0.1);
    const diameterPx = clamp(radius * 2 * spatialViewport.scalePxPerMeter, 2, 180);
    const baseline = String(obs.detail_level || "").toLowerCase() === "baseline";
    const material = !baseline && obs.material ? String(obs.material) : "";
    const geology = !baseline && obs.geology_class && obs.geology_class !== "unclassified"
      ? String(obs.geology_class)
      : "";
    const contact = obs.deposit_id ? (material || "Physical contact") : "";
    const label = contact || String(obs.terrain_class || "Observation");
    const titleBits = [
      `Observation #${obs.id}`,
      label,
      `uncertainty radius ${trimNumber(radius)} m`,
      geology ? `geology ${geology}` : "",
      obs.summary || "",
    ].filter(Boolean);

    return `
      <div
        class="map-observation ${baseline ? "baseline" : "detailed"}"
        data-observation-id="${escapeHtml(String(obs.id))}"
        style="left:${pos.x}%; top:${pos.y}%;"
        title="${escapeHtml(titleBits.join(" • "))}"
      >
        <span class="observation-radius" style="width:${diameterPx}px; height:${diameterPx}px;"></span>
        <span class="observation-dot"></span>
        <span class="observation-label">${escapeHtml(label)} <small>±${escapeHtml(trimNumber(radius))}m</small></span>
      </div>
    `;
  }).join("");
}

function renderMap() {
  const routeLabels = renderRoutes();
  const nodes = (state.locations || []).map(loc => renderLocationNode(loc)).join("");
  const observations = renderSpatialObservations();

  const citizenTokens = (state.citizens || []).map(citizen => {
    const placement = citizenMapPlacement(citizen);
    const pos = placement.pos;
    if (!pos) return "";
    const progressText = placement.progress != null ? ` • ${placement.progress}%` : "";
    const classes = [
      "map-citizen",
      placement.localMoving ? "local-moving" : "",
      placement.routeTraveling ? "traveling" : "",
      selectedCitizen === citizen.id ? "selected" : "",
    ].filter(Boolean).join(" ");

    return `
      <button
        class="${classes}"
        style="left:calc(${pos.x}% + ${placement.offset.x}px); top:calc(${pos.y}% + ${placement.offset.y}px);"
        title="${escapeHtml(citizen.name)} • ${escapeHtml(placement.label)}${progressText}"
        aria-label="${escapeHtml(citizen.name)} • ${escapeHtml(placement.label)}"
        onclick="selectCitizen('${citizen.id}')"
      >${citizenAvatarMarkup(citizen, "map")}
        ${placement.routeTraveling && placement.progress != null
          ? `<span class="map-travel-progress" aria-hidden="true">${placement.progress}%</span>`
          : ""}
      </button>
    `;
  }).join("");

  let visitorMarker = "";
  if (visitorPresence) {
    let pos = null;
    let label = "";
    let offset = { x: 16, y: -18 };
    const localShared = visitorPresence.shared_activity?.movement;

    if (
      spatialViewport &&
      finiteNumber(visitorPresence.x_m) != null &&
      finiteNumber(visitorPresence.y_m) != null &&
      localShared
    ) {
      pos = metersToMap(visitorPresence.x_m, visitorPresence.y_m);
      const p = Math.round(clamp(Number(localShared.progress) || 0, 0, 1) * 100);
      label = `${els.visitorName.value.trim() || "Visitor"} • shared local activity • ${p}%`;
    } else if (visitorPresence.traveling) {
      pos = interpolatedPosition(
        visitorPresence.from_location_id,
        visitorPresence.to_location_id,
        visitorPresence.progress || 0
      );
      offset = { x: 0, y: -26 };
      label = `${els.visitorName.value.trim() || "Visitor"} • traveling to ${visitorPresence.to_location_name}`;
    } else if (
      spatialViewport &&
      finiteNumber(visitorPresence.x_m) != null &&
      finiteNumber(visitorPresence.y_m) != null
    ) {
      pos = metersToMap(visitorPresence.x_m, visitorPresence.y_m);
      label = `${els.visitorName.value.trim() || "Visitor"} • x ${trimNumber(visitorPresence.x_m)} m • y ${trimNumber(visitorPresence.y_m)} m`;
    } else {
      pos = positionForLocation(visitorPresence.location_id);
      offset = LOCATION_PRESENTATION[visitorPresence.location_id]?.visitor || offset;
      label = `${els.visitorName.value.trim() || "Visitor"} • ${visitorPresence.location_name}`;
    }

    if (pos) {
      visitorMarker = `
        <button
          class="map-visitor ${localShared ? "local-moving" : ""} ${visitorPresence.traveling ? "traveling" : ""}"
          style="left:calc(${pos.x}% + ${offset.x}px); top:calc(${pos.y}% + ${offset.y}px);"
          title="${escapeHtml(label)}"
          onclick="focusLocation('${visitorPresence.location_id || "seed_site"}')"
        >YOU</button>
      `;
    }
  }

  if (els.mapSpatialStatus) {
    if (spatialViewport) {
      const modeLabel = spatialViewport.mode === "local"
        ? "Local meter view"
        : spatialViewport.mode === "focused"
          ? "Focused meter view"
          : "Meter-space region";
      els.mapSpatialStatus.textContent = `${modeLabel} • ${mapZoomLevel.toFixed(mapZoomLevel < 2 ? 1 : 0)}× • ${spatialViewport.frameId} • +x east / +y north`;
    } else {
      els.mapSpatialStatus.textContent = "Confirmed information only.";
    }
  }

  els.mapLayer.innerHTML = routeLabels + nodes + observations + citizenTokens + visitorMarker;
  updateWorldFocus();
}

function renderLocationNode(loc) {
  const pos = positionForLocation(loc.id);
  const deposits = depositsForLocation(loc.id);
  const presentation = LOCATION_PRESENTATION[loc.id] || { label: "below" };
  const selected = selectedCitizen ? state.citizens.find(c => c.id === selectedCitizen) : null;
  const selectedHere = selected && citizensAtLocation(loc.id).some(c => c.id === selected.id);
  const coords = spatialViewport && finiteNumber(loc.x_m) != null && finiteNumber(loc.y_m) != null
    ? ` • x ${trimNumber(loc.x_m)} m • y ${trimNumber(loc.y_m)} m`
    : "";
  const nodeTitle = `${loc.name} • ${loc.surveyed ? "Surveyed" : "Not yet surveyed"}${deposits.length ? ` • ${deposits.length} confirmed deposit${deposits.length > 1 ? "s" : ""}` : ""}${coords}`;

  return `
    <button
      class="map-node label-${presentation.label || "below"} ${focusedLocation === loc.id ? "focused" : ""} ${selectedHere ? "selected-location" : ""}"
      style="left:${pos.x}%; top:${pos.y}%;"
      title="${escapeHtml(nodeTitle)}"
      onclick="focusMapLocation('${loc.id}')"
    >
      <span class="node-dot"></span>
      <span class="node-label">${escapeHtml(loc.name)}</span>
    </button>
  `;
}

function updateWorldFocus() {
  const loc = locationById(focusedLocation) || locationById("seed_site");
  const deposits = depositsForLocation(loc.id);
  const people = citizensAtLocation(loc.id).map(c => c.name);

  let visitorAction = "";
  if (visitorPresence) {
    if (visitorPresence.shared_activity?.movement) {
      const movement = visitorPresence.shared_activity.movement;
      const p = Math.round(clamp(Number(movement.progress) || 0, 0, 1) * 100);
      visitorAction = `
        <div class="visitor-route-card shared-active">
          <strong>Shared local activity is physically active</strong>
          <span>${escapeHtml(String(visitorPresence.shared_activity.objective || visitorPresence.shared_activity.activity_type || "Local exploration"))}</span>
          <div class="job-progress-track"><span style="width:${p}%"></span></div>
          <small>${p}% • target x ${escapeHtml(trimNumber(movement.target_x_m))} m / y ${escapeHtml(trimNumber(movement.target_y_m))} m</small>
        </div>
      `;
    } else if (visitorPresence.traveling) {
      const p = Math.round((visitorPresence.progress || 0) * 100);
      visitorAction = `
        <div class="visitor-route-card">
          <strong>You are traveling</strong>
          <span>${escapeHtml(visitorPresence.from_location_name)} → ${escapeHtml(visitorPresence.to_location_name)}</span>
          <div class="job-progress-track"><span style="width:${p}%"></span></div>
          <small>${visitorPresence.elapsed_minutes} / ${visitorPresence.total_minutes} sim min • ${visitorPresence.remaining_minutes} remaining</small>
        </div>
      `;
    } else if (visitorPresence.location_id === loc.id) {
      visitorAction = `<div class="visitor-route-card here"><strong>You are here.</strong><span>Face-to-face visits are possible with available citizens at this location.</span></div>`;
    } else {
      const route = routeBetween(visitorPresence.location_id, loc.id);
      if (route) {
        const duration = Math.max(25, Math.floor(Number(route.distance_km) * 45));
        visitorAction = `
          <div class="visitor-route-card">
            <strong>Visit this location</strong>
            <span>${escapeHtml(visitorPresence.location_name)} → ${escapeHtml(loc.name)} • ${duration} sim min</span>
            <button class="travel-button" onclick="startVisitorTravel('${loc.id}')">Travel here</button>
          </div>
        `;
      } else {
        visitorAction = `<div class="visitor-route-card"><strong>No direct route from your current location.</strong><span>Travel through a connected location first.</span></div>`;
      }
    }
  }

  els.worldFocus.innerHTML = `
    <strong>${escapeHtml(loc.name)}</strong>
    <p>${escapeHtml(loc.description)}</p>
    <div class="focus-meta">
      <span>${loc.surveyed ? "Surveyed" : "Not yet surveyed"}</span>
      <span>${deposits.length ? `Deposits: ${deposits.map(d => escapeHtml(d.material)).join(", ")}` : "No confirmed deposits"}</span>
      <span>${people.length ? `Present: ${people.map(escapeHtml).join(", ")}` : "No citizens currently present"}</span>
    </div>
    ${visitorAction}
  `;
}

function renderRegionStrip() {
  els.regionStrip.innerHTML = state.locations.map(loc => {
    const deposits = depositsForLocation(loc.id);
    const people = citizensAtLocation(loc.id);
    const youAreHere = visitorPresence && !visitorPresence.traveling && visitorPresence.location_id === loc.id;
    return `
      <button class="region-mini ${focusedLocation === loc.id ? "focused" : ""} ${youAreHere ? "visitor-here" : ""}" onclick="focusLocation('${loc.id}')">
        <strong>${escapeHtml(loc.name)}</strong>
        <span>${loc.surveyed ? "Surveyed" : "Unsurveyed"}</span>
        <span>${deposits.length ? deposits.map(d => escapeHtml(d.material)).join(", ") : "No deposits"}</span>
        <span>${people.length ? `Present: ${people.length}` : "Empty"}</span>
        ${youAreHere ? '<span class="you-are-here">YOU ARE HERE</span>' : ""}
      </button>
    `;
  }).join("");
}

function citizenNameById(id) {
  return state?.citizens?.find(c => String(c.id) === String(id))?.name || id || "Unassigned";
}

function locationNameById(id) {
  return state?.locations?.find(loc => String(loc.id) === String(id))?.name || id || "Unknown location";
}

function projectMaterialsFor(projectId) {
  return (state?.project_materials || []).filter(row => String(row.project_id) === String(projectId));
}

function statusLabel(status) {
  const labels = {
    planned: "Planned",
    reserved: "Materials reserved",
    underway: "Underway",
    complete: "Complete",
  };
  return labels[status] || String(status || "Unknown");
}

function localCoordinateText(x, y) {
  const xNum = Number(x);
  const yNum = Number(y);
  if (!Number.isFinite(xNum) || !Number.isFinite(yNum)) return "";
  return `Local site ${trimNumber(xNum)} km x / ${trimNumber(yNum)} km y`;
}

function renderMakingBuilding() {
  const projects = state?.projects || [];
  const equipment = state?.equipment || [];
  const structures = state?.structures || [];

  els.projects.innerHTML = projects.length ? projects.map(project => {
    const materials = projectMaterialsFor(project.id);
    const coords = localCoordinateText(project.x_km, project.y_km);
    const creator = citizenNameById(project.created_by);
    const location = locationNameById(project.location_id);
    const status = String(project.status || "unknown");

    const materialMarkup = materials.length ? `
      <div class="project-materials">
        ${materials.map(row => `
          <div class="project-material-row">
            <span>${escapeHtml(row.material)}</span>
            <strong>${trimNumber(row.reserved_amount || 0)} / ${trimNumber(row.required_amount || 0)}</strong>
          </div>
        `).join("")}
      </div>
    ` : '<div class="making-empty-note">No material requirement rows are exposed for this project.</div>';

    const completion = status === "complete" && project.resulting_structure_id != null
      ? `<span>Structure #${escapeHtml(String(project.resulting_structure_id))}</span>`
      : "";

    const activeJob = project.active_job_id != null
      ? `<span>Active job #${escapeHtml(String(project.active_job_id))}</span>`
      : "";

    return `
      <article class="project-card status-${escapeHtml(status)}" data-project-id="${escapeHtml(String(project.id))}">
        <div class="making-card-head">
          <div>
            <strong>${escapeHtml(project.name || project.blueprint_id || "Project")}</strong>
            <span>Project #${escapeHtml(String(project.id))}</span>
          </div>
          <span class="status-chip status-${escapeHtml(status)}">${escapeHtml(statusLabel(status))}</span>
        </div>
        <div class="making-meta">
          <span>${escapeHtml(location)}</span>
          <span>Created by ${escapeHtml(creator)}</span>
          ${coords ? `<span>${escapeHtml(coords)}</span>` : ""}
          ${activeJob}
          ${completion}
        </div>
        ${materialMarkup}
      </article>
    `;
  }).join("") : '<div class="muted making-empty">No construction projects exist yet.</div>';

  els.equipment.innerHTML = equipment.length ? equipment.map(item => {
    const owner = item.owner_citizen_id
      ? citizenNameById(item.owner_citizen_id)
      : "Settlement equipment";
    const location = locationNameById(item.location_id);
    const effectiveCargoBonus = Number(item.effective_cargo_bonus || 0);
    const effectiveExtractionMultiplier = Number(item.effective_extraction_speed_multiplier || 1);
    const effects = [];
    if (effectiveCargoBonus !== 0) effects.push(`Current cargo capacity ${effectiveCargoBonus > 0 ? "+" : ""}${trimNumber(effectiveCargoBonus)}`);
    if (effectiveExtractionMultiplier !== 1) effects.push(`Current extraction speed ${trimNumber(effectiveExtractionMultiplier)}×`);

    return `
      <article class="equipment-card" data-equipment-id="${escapeHtml(String(item.id))}">
        <div class="making-card-head">
          <div>
            <strong>${escapeHtml(item.name || item.template_id || "Equipment")}</strong>
            <span>Equipment #${escapeHtml(String(item.id))} • ${escapeHtml(item.kind || "equipment")}</span>
          </div>
          <span class="condition-chip condition-${escapeHtml(item.condition_state || "unknown")}">${Math.round(Number(item.condition) || 0)}% • ${escapeHtml(conditionStateLabel(item.condition_state))}</span>
        </div>
        <div class="making-meta">
          <span>${escapeHtml(owner)}</span>
          <span>${escapeHtml(location)}</span>
          <span>${item.operational === false ? "Non-operational" : "Operational"}</span>
          ${item.service_due ? "<span>Service due</span>" : ""}
          ${item.last_service_minute != null ? `<span>Last service ${escapeHtml(formatMinute(item.last_service_minute))}</span>` : ""}
          ${item.use_count != null ? `<span>${escapeHtml(String(item.use_count))} uses</span>` : ""}
          ${item.created_job_id != null ? `<span>Created by job #${escapeHtml(String(item.created_job_id))}</span>` : ""}
        </div>
        <div class="effect-row">
          ${effects.length ? effects.map(effect => `<span>${escapeHtml(effect)}</span>`).join("") : '<span>No non-default modifier exposed.</span>'}
        </div>
      </article>
    `;
  }).join("") : '<div class="muted making-empty">No fabricated equipment exists yet.</div>';

  els.structures.innerHTML = structures.length ? structures.map(structure => {
    const location = locationNameById(structure.location_id);
    const coords = localCoordinateText(structure.x_km, structure.y_km);
    const charging = Number(structure.provides_charging || 0) === 1;
    return `
      <article class="structure-card" data-structure-id="${escapeHtml(String(structure.id))}">
        <div class="making-card-head">
          <div>
            <strong>${escapeHtml(structure.name)}</strong>
            <span>Structure #${escapeHtml(String(structure.id))} • ${escapeHtml(structure.kind || "structure")}</span>
          </div>
          <span class="condition-chip condition-${escapeHtml(structure.condition_state || "unknown")}">${Math.round(Number(structure.condition) || 0)}% • ${escapeHtml(conditionStateLabel(structure.condition_state))}</span>
        </div>
        <div class="making-meta">
          <span>${escapeHtml(location)}</span>
          ${coords ? `<span>${escapeHtml(coords)}</span>` : ""}
          <span>${structure.operational === false ? "Non-operational" : "Operational"}</span>
          ${structure.service_due ? "<span>Service due</span>" : ""}
          ${Number.isFinite(Number(structure.efficiency_multiplier)) ? `<span>Efficiency ${escapeHtml(trimNumber(Number(structure.efficiency_multiplier) * 100))}%</span>` : ""}
          ${structure.last_service_minute != null ? `<span>Last service ${escapeHtml(formatMinute(structure.last_service_minute))}</span>` : ""}
          ${structure.use_count != null ? `<span>${escapeHtml(String(structure.use_count))} uses</span>` : ""}
          ${charging ? "<span>Provides charging</span>" : ""}
          ${structure.project_id != null ? `<span>From project #${escapeHtml(String(structure.project_id))}</span>` : ""}
        </div>
      </article>
    `;
  }).join("") : '<div class="muted making-empty">No structures are currently exposed.</div>';

  renderMaintenanceHistory();
}

function normalizedConversationKey(simMinute, personA, personB, locationName) {
  const people = [String(personA || "").trim().toLowerCase(), String(personB || "").trim().toLowerCase()]
    .filter(Boolean)
    .sort()
    .join("|");
  return [
    Number(simMinute),
    people,
    String(locationName || "").trim().toLowerCase(),
  ].join("::");
}

function parseConversationHistoryMessage(message) {
  const text = String(message || "").trim();
  const match = text.match(/^(.+?) and (.+?) talked at (.+?)\.$/);
  if (!match) return null;
  return {
    personA: match[1].trim(),
    personB: match[2].trim(),
    locationName: match[3].trim(),
  };
}

function conversationIdFromChronology(message) {
  const match = String(message || "").match(/\(conversation #(\d+)\)/i);
  return match ? Number(match[1]) : null;
}

function captureOpenConversationTranscripts() {
  if (!els.citizenConversations) return;
  els.citizenConversations
    .querySelectorAll("details.conversation-transcript[data-conversation-id]")
    .forEach(details => {
      const id = String(details.dataset.conversationId || "");
      if (!id) return;
      if (details.open) openConversationIds.add(id);
      else openConversationIds.delete(id);
    });
}

function historyPaginationMarkup(page, totalPages, setterName) {
  if (totalPages <= 1) return "";
  return `
    <button type="button" onclick="${setterName}(${page - 1})" ${page <= 1 ? "disabled" : ""}>Previous</button>
    <span>Page ${page} of ${totalPages}</span>
    <button type="button" onclick="${setterName}(${page + 1})" ${page >= totalPages ? "disabled" : ""}>Next</button>
  `;
}

async function loadHistoryRecords() {
  if (historyRecordsLoading) return;
  historyRecordsLoading = true;

  try {
    const params = new URLSearchParams({
      conversation_page: String(historyConversationPage),
      chronology_page: String(historyChronologyPage),
      conversation_page_size: String(HISTORY_CONVERSATIONS_PER_PAGE),
      chronology_page_size: String(HISTORY_CHRONOLOGY_PER_PAGE),
    });
    const response = await fetch(`/api/records/history?${params.toString()}`, { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not load settlement history.");

    historyRecords = data;
    historyConversationPage = Number(data.conversations?.page) || 1;
    historyChronologyPage = Number(data.chronology?.page) || 1;
    renderHistoryRecords();
  } catch (error) {
    if (els.citizenConversations && !historyRecords) {
      els.citizenConversations.innerHTML = `<div class="muted conversation-empty">${escapeHtml(error.message)}</div>`;
    }
    if (els.history && !historyRecords) {
      els.history.innerHTML = '<div class="muted">Settlement chronology could not be loaded.</div>';
    }
  } finally {
    historyRecordsLoading = false;
  }
}

function renderHistoryRecords() {
  captureOpenConversationTranscripts();

  const conversationPage = historyRecords?.conversations;
  const chronologyPage = historyRecords?.chronology;

  if (!conversationPage || !chronologyPage) {
    els.citizenConversations.innerHTML = '<div class="muted conversation-empty">Loading conversation records…</div>';
    els.history.innerHTML = '<div class="muted">Loading settlement chronology…</div>';
    els.conversationPagination.innerHTML = "";
    els.chronologyPagination.innerHTML = "";
    els.conversationPageSummary.textContent = "Loading…";
    els.chronologyPageSummary.textContent = "Loading…";
    return;
  }

  const conversations = Array.isArray(conversationPage.items) ? conversationPage.items : [];
  els.citizenConversations.innerHTML = conversations.length ? conversations.map(c => {
    const conversationId = Number(c.id ?? c.source_id);
    const id = Number.isFinite(conversationId) ? String(conversationId) : "";
    const summary = String(c.summary || "").trim() || "No compact summary is available for this exchange.";
    const initiatorText = String(c.initiator_text || "").trim();
    const targetText = String(c.target_text || "").trim();
    const hasTranscript = Boolean(initiatorText || targetText);
    const sourceJobId = c.source_job_id != null ? String(c.source_job_id) : "";
    const idLabel = Number.isFinite(conversationId) ? `Conversation #${conversationId}` : "Conversation record";
    const completionMinute = Number(c.completed_minute);
    const isOpen = id && openConversationIds.has(id);

    return `
      <article class="conversation-card" data-conversation-id="${escapeHtml(id)}">
        <div class="conversation-card-head">
          <div class="conversation-people">
            <strong>${escapeHtml(c.initiator_name)}</strong>
            <span aria-hidden="true">↔</span>
            <strong>${escapeHtml(c.target_name)}</strong>
          </div>
          <time>${formatMinute(c.sim_minute)}</time>
        </div>
        <div class="conversation-location">At ${escapeHtml(c.location_name)}</div>
        <div class="conversation-record-meta">
          <span>${escapeHtml(idLabel)}</span>
          ${sourceJobId ? `<span>Talk job #${escapeHtml(sourceJobId)}</span>` : "<span>Legacy conversation</span>"}
          ${Number.isFinite(completionMinute) ? `<span>Completed ${escapeHtml(formatMinute(completionMinute))}</span>` : ""}
        </div>
        <div class="conversation-summary">
          <span>Summary</span>
          <p>${escapeHtml(summary)}</p>
        </div>
        ${hasTranscript ? `
          <details class="conversation-transcript" data-conversation-id="${escapeHtml(id)}" ${isOpen ? "open" : ""}>
            <summary>Read exchange</summary>
            ${initiatorText ? `<div><strong>${escapeHtml(c.initiator_name)}</strong><span>${escapeHtml(initiatorText)}</span></div>` : ""}
            ${targetText ? `<div><strong>${escapeHtml(c.target_name)}</strong><span>${escapeHtml(targetText)}</span></div>` : ""}
          </details>
        ` : '<div class="conversation-record-note">Exchange text is not available for this conversation record.</div>'}
      </article>
    `;
  }).join("") : '<div class="muted conversation-empty">No citizen-to-citizen conversations recorded yet.</div>';

  els.citizenConversations
    .querySelectorAll("details.conversation-transcript[data-conversation-id]")
    .forEach(details => {
      details.addEventListener("toggle", () => {
        const id = String(details.dataset.conversationId || "");
        if (!id) return;
        if (details.open) openConversationIds.add(id);
        else openConversationIds.delete(id);
      });
    });

  const conversationTotal = Number(conversationPage.total) || 0;
  const conversationPages = Number(conversationPage.total_pages) || 1;
  els.conversationPageSummary.textContent = conversationTotal
    ? `Page ${historyConversationPage} of ${conversationPages} • ${conversationTotal} conversations`
    : "No conversation records yet";
  els.conversationPagination.innerHTML = historyPaginationMarkup(
    historyConversationPage,
    conversationPages,
    "setConversationHistoryPage"
  );

  const chronology = Array.isArray(chronologyPage.items) ? chronologyPage.items : [];
  els.history.innerHTML = chronology.length ? chronology.map(h => `
    <div class="history-entry ${h.category === "diagnostic" ? "diagnostic" : ""}">
      <div class="history-dot"></div>
      <div>
        <strong>${formatMinute(h.sim_minute)}${h.category === "diagnostic" ? " • diagnostic" : ""}</strong>
        <p>${escapeHtml(h.message)}</p>
      </div>
    </div>
  `).join("") : '<div class="muted">No settlement chronology recorded yet.</div>';

  const chronologyTotal = Number(chronologyPage.total) || 0;
  const chronologyPages = Number(chronologyPage.total_pages) || 1;
  els.chronologyPageSummary.textContent = chronologyTotal
    ? `Page ${historyChronologyPage} of ${chronologyPages} • ${chronologyTotal} events`
    : "No chronology records yet";
  els.chronologyPagination.innerHTML = historyPaginationMarkup(
    historyChronologyPage,
    chronologyPages,
    "setChronologyHistoryPage"
  );
}

window.setConversationHistoryPage = function(page) {
  historyConversationPage = Math.max(1, Number(page) || 1);
  void loadHistoryRecords();
};

window.setChronologyHistoryPage = function(page) {
  historyChronologyPage = Math.max(1, Number(page) || 1);
  void loadHistoryRecords();
};

function renderDrawerLists() {
  els.locations.innerHTML = state.locations.map(loc => {
    const known = depositsForLocation(loc.id);
    const people = citizensAtLocation(loc.id).map(c => c.name);
    return `
      <button class="location-card ${focusedLocation === loc.id ? "focused" : ""}" onclick="focusLocation('${loc.id}')">
        <div class="location-name">${escapeHtml(loc.name)}</div>
        <div class="muted">${escapeHtml(loc.description)}</div>
        <div class="location-meta">${loc.surveyed ? "Surveyed" : "Not yet surveyed"}</div>
        <div class="small">${known.length ? `Confirmed: ${known.map(d => escapeHtml(d.material)).join(", ")}` : "No confirmed deposits"}</div>
        <div class="small">${people.length ? `Present: ${people.map(escapeHtml).join(", ")}` : "No citizens currently present"}</div>
      </button>
    `;
  }).join("");

  const stored = new Map(state.resources.map(r => [r.name, Number(r.amount) || 0]));
  const carried = new Map();
  for (const item of state.inventory) {
    if (Number(item.amount) <= 0) continue;
    carried.set(item.material, (carried.get(item.material) || 0) + Number(item.amount));
  }

  const materials = Array.from(new Set([...stored.keys(), ...carried.keys()]))
    .sort((a, b) => a.localeCompare(b));

  els.resourceBalance.innerHTML = `
    <div class="material-balance-head">
      <span>Material</span><span>Stored</span><span>Field</span>
    </div>
    ${materials.map(name => `
      <div class="material-balance-row">
        <span>${escapeHtml(name)}</span>
        <strong>${trimNumber(stored.get(name) || 0)}</strong>
        <strong class="${(carried.get(name) || 0) > 0 ? "field-positive" : ""}">${trimNumber(carried.get(name) || 0)}</strong>
      </div>
    `).join("")}
  `;

  const carriers = state.citizens.map(c => {
    const items = state.inventory.filter(i => i.citizen_id === c.id && Number(i.amount) > 0);
    if (!items.length) return "";
    const total = items.reduce((sum, i) => sum + Number(i.amount), 0);
    return `
      <div class="cargo-card">
        <div class="cargo-card-head">
          <strong>${escapeHtml(c.name)}</strong>
          <span>${trimNumber(total)} units carried</span>
        </div>
        <div class="cargo-items">${items.map(i => `
          <span>${escapeHtml(i.material)} <strong>${trimNumber(i.amount)}</strong></span>
        `).join("")}</div>
      </div>
    `;
  }).filter(Boolean);

  els.citizenCargo.innerHTML = carriers.length
    ? carriers.join("")
    : '<div class="muted cargo-empty">No materials are currently being carried in the field.</div>';

  renderMakingBuilding();

  renderHistoryRecords();
}

function formatMinute(minute) {
  const day = Math.floor(minute / 1440) + 1;
  const md = minute % 1440;
  const hour = String(Math.floor(md / 60)).padStart(2, "0");
  const min = String(md % 60).padStart(2, "0");
  return `Day ${day} • ${hour}:${min}`;
}

function openControlRoomView(name, title, eyebrow = "DETAILS") {
  openControlView = name;
  els.detailEyebrow.textContent = eyebrow;
  els.detailTitle.textContent = title;

  Object.entries(els.detailViews).forEach(([key, el]) => {
    el.classList.toggle("hidden", key !== name);
  });

  document.querySelectorAll(".control-tab").forEach(btn => {
    btn.classList.remove("active");
  });

  const activeMap = {
    region: els.toggleRegion,
    resources: els.toggleResources,
    structures: els.toggleStructures,
    history: els.toggleHistory,
    updates: els.toggleUpdates,
  };

  if (activeMap[name]) activeMap[name].classList.add("active");
  if (name === "history") void loadHistoryRecords();
}

function updateMapZoomLabel() {
  if (!els.mapZoomLabel) return;
  const rounded = mapZoomLevel >= 2
    ? Math.round(mapZoomLevel * 10) / 10
    : Math.round(mapZoomLevel * 100) / 100;
  els.mapZoomLabel.textContent = `${rounded}×`;
}

function rerenderMapPresentation() {
  if (!state) return;
  computeLocationPositions();
  renderMap();
  updateMapZoomLabel();
}

function setMapZoom(nextZoom) {
  mapZoomLevel = clamp(Number(nextZoom) || 1, MAP_ZOOM_MIN, MAP_ZOOM_MAX);
  rerenderMapPresentation();
}

window.focusMapLocation = function(id) {
  const loc = locationById(id);
  if (!loc) return;

  focusedLocation = id;
  const x = finiteNumber(loc.x_m);
  const y = finiteNumber(loc.y_m);
  mapCenterOverride = x != null && y != null ? { x_m: x, y_m: y } : null;
  mapZoomLevel = Math.max(mapZoomLevel, 3.5);

  renderLocationDirectory();
  renderLocationSheet();
  renderDrawerLists();
  rerenderMapPresentation();
};

window.focusLocation = function(id) {
  focusedLocation = id;
  renderMap();
  renderRegionStrip();
  renderLocationDirectory();
  renderLocationSheet();
  renderDrawerLists();
};

window.startVisitorTravel = async function(target) {
  if (!visitorPresence || visitorPresence.traveling) return;
  const visitor = els.visitorName.value.trim() || "Visitor";

  try {
    const response = await fetch("/api/visitor/travel", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ visitor, target }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Travel could not begin.");

    visitorPresence = data.presence;
    if (selectedCitizen) {
      clearVisitSelection(`You left ${visitorPresence.from_location_name || "the location"} and began traveling.`);
    }
    focusedLocation = target;
    render();
  } catch (error) {
    if (selectedCitizen) appendChat("System", error.message, "system");
    else alert(error.message);
  }
};

function sharedActionStatusLabel(proposal) {
  const status = String(proposal?.status || "proposed");
  const simulationStatus = String(proposal?.simulation_status || "").toLowerCase();
  if (simulationStatus === "rejected" || status === "rejected") return "Declined";
  if (status === "proposed") return "Proposal • not started";
  if (status === "accepted" && !proposal?.simulation_action_id) return "Accepted intent • not started";
  if (status === "started" && proposal?.simulation_action_id) return "Active physical activity";
  if (status === "completed") return "Completed";
  if (status === "failed") return "Failed";
  if (status === "cancelled") return "Cancelled";
  if (status === "expired") return "Expired";
  return status.replaceAll("_", " ");
}

function renderSharedActionPanel(proposals = currentSharedActionProposals) {
  if (!els.sharedActionPanel) return;
  const items = Array.isArray(proposals) ? proposals.slice(-3).reverse() : [];
  if (!items.length || !selectedCitizen) {
    els.sharedActionPanel.classList.add("hidden");
    els.sharedActionPanel.innerHTML = "";
    return;
  }

  els.sharedActionPanel.innerHTML = items.map(proposal => {
    const status = String(proposal.status || "proposed");
    const targetX = finiteNumber(proposal.target?.x_m);
    const targetY = finiteNumber(proposal.target?.y_m);
    const target = targetX != null && targetY != null
      ? `Target x ${trimNumber(targetX)} m • y ${trimNumber(targetY)} m`
      : "Validated target";
    const hasPhysicalJob = Boolean(proposal.simulation_action_id);
    const physicalActive = status === "started" && hasPhysicalJob;
    const progress = physicalActive && finiteNumber(proposal.progress) != null
      ? clamp(Number(proposal.progress), 0, 1)
      : null;
    const observationIds = Array.isArray(proposal.observation_ids) ? proposal.observation_ids : [];
    const pending = sharedActionBusyId === Number(proposal.id);
    const canAccept = status === "proposed" && proposal.acceptance_available === true && !pending;
    const canReject = status === "proposed" && !pending;

    return `
      <article class="shared-action-card status-${escapeHtml(status)} ${physicalActive ? "physical-active" : "intent-only"}">
        <div class="shared-action-head">
          <div>
            <span class="shared-action-status">${escapeHtml(sharedActionStatusLabel(proposal))}</span>
            <strong>${escapeHtml(proposal.label || proposal.objective || "Shared local activity")}</strong>
          </div>
          <small>#${escapeHtml(String(proposal.id))}</small>
        </div>
        ${proposal.objective ? `<p>${escapeHtml(proposal.objective)}</p>` : ""}
        <div class="shared-action-meta">
          <span>${escapeHtml(target)}</span>
          ${proposal.simulation_activity_id != null ? `<span>Activity #${escapeHtml(String(proposal.simulation_activity_id))}</span>` : ""}
          ${hasPhysicalJob ? `<span>Physical job #${escapeHtml(String(proposal.simulation_action_id))}</span>` : ""}
          ${observationIds.length ? `<span>Observation ${observationIds.map(id => "#" + escapeHtml(String(id))).join(", ")}</span>` : ""}
        </div>
        ${progress != null ? `
          <div class="shared-action-progress">
            <div class="job-progress-track"><span style="width:${Math.round(progress * 100)}%"></span></div>
            <small>${Math.round(progress * 100)}% • authoritative Simulation progress</small>
          </div>
        ` : ""}
        ${proposal.outcome ? `<div class="shared-action-outcome">${escapeHtml(proposal.outcome)}</div>` : ""}
        ${status === "proposed" ? `
          <div class="shared-action-actions">
            <button type="button" class="accent-button" ${canAccept ? "" : "disabled"} onclick="acceptSharedAction(${Number(proposal.id)})">
              ${pending ? "Working…" : "Accept & start"}
            </button>
            <button type="button" ${canReject ? "" : "disabled"} onclick="rejectSharedAction(${Number(proposal.id)})">Decline</button>
          </div>
          <small class="shared-action-truth">A proposal is not movement. Physical start requires Simulation to create a real job.</small>
        ` : ""}
      </article>
    `;
  }).join("");
  els.sharedActionPanel.classList.remove("hidden");
}

function upsertSharedActionProposal(proposal) {
  if (!proposal?.id) return;
  const index = currentSharedActionProposals.findIndex(item => Number(item.id) === Number(proposal.id));
  if (index >= 0) currentSharedActionProposals[index] = proposal;
  else currentSharedActionProposals.push(proposal);
  renderSharedActionPanel();
}

async function refreshSharedActionProposals(citizenId = selectedCitizen) {
  if (!citizenId || currentVisitId == null) return;
  const visitor = els.visitorName.value.trim() || "Visitor";
  try {
    const response = await fetch(
      `/api/visit/${encodeURIComponent(citizenId)}/shared-actions?visitor=${encodeURIComponent(visitor)}&visit_id=${encodeURIComponent(currentVisitId)}`,
      { cache: "no-store" }
    );
    if (!response.ok) return;
    const data = await response.json();
    currentSharedActionProposals = Array.isArray(data.proposals) ? data.proposals : [];
    renderSharedActionPanel();
  } catch {
    // Proposal UI is an enhancement. Visit/chat remains usable if refresh fails.
  }
}

window.acceptSharedAction = async function(proposalId) {
  if (sharedActionBusyId != null) return;
  const visitor = els.visitorName.value.trim() || "Visitor";
  sharedActionBusyId = Number(proposalId);
  renderSharedActionPanel();
  try {
    const response = await fetch(`/api/shared-actions/${encodeURIComponent(proposalId)}/accept`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ visitor }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || data.message || "Shared activity could not start.");
    if (data.proposal) upsertSharedActionProposal(data.proposal);
    appendChat("System", data.message || "Shared physical activity started.", "system");
    await loadState();
  } catch (error) {
    appendChat("System", error.message, "system");
  } finally {
    sharedActionBusyId = null;
    renderSharedActionPanel();
  }
};

window.rejectSharedAction = async function(proposalId) {
  if (sharedActionBusyId != null) return;
  const visitor = els.visitorName.value.trim() || "Visitor";
  sharedActionBusyId = Number(proposalId);
  renderSharedActionPanel();
  try {
    const response = await fetch(`/api/shared-actions/${encodeURIComponent(proposalId)}/reject`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ visitor }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || data.message || "Proposal could not be declined.");
    if (data.proposal) upsertSharedActionProposal(data.proposal);
    appendChat("System", data.message || "Proposal declined. No physical action started.", "system");
    await refreshSharedActionProposals();
  } catch (error) {
    appendChat("System", error.message, "system");
  } finally {
    sharedActionBusyId = null;
    renderSharedActionPanel();
  }
};

function renderVisitConversation(data) {
  els.chatLog.innerHTML = "";
  currentVisitId = data.visit?.id ?? data.visit_id ?? null;
  currentSharedActionProposals = Array.isArray(data.shared_action_proposals) ? data.shared_action_proposals : [];
  renderSharedActionPanel();
  els.visitHistoryPanel.classList.add("hidden");
  els.visitHistoryPanel.innerHTML = "";

  if (data.accessible === false) {
    const accessStatus = data.status || data.availability?.status || "unavailable";
    const counterpart = data.availability?.other_citizen_name;
    const statusLabels = {
      remote: "Not at the same location",
      visitor_traveling: "You are traveling",
      citizen_traveling: `${data.citizen.name} is traveling`,
      citizen_talking: counterpart ? `Busy talking with ${counterpart}` : "Currently talking",
      citizen_busy: `${data.citizen.name} is busy`,
      missing: "Unavailable",
    };
    els.selectedLabel.textContent = statusLabels[accessStatus] || data.reason || "Face-to-face visit unavailable";
    els.chatInput.disabled = true;
    els.sendButton.disabled = true;
    els.leaveVisit.hidden = true;

    const route = accessStatus === "remote" && visitorPresence && !visitorPresence.traveling
      ? routeBetween(visitorPresence.location_id, data.citizen.location_id)
      : null;
    const travelButton = route
      ? `<button class="travel-button" onclick="startVisitorTravel('${data.citizen.location_id}')">Travel to ${escapeHtml(data.citizen.location)}</button>`
      : "";

    els.chatLog.innerHTML = `
      <div class="remote-visit-notice">
        <strong>Face-to-face visit unavailable</strong>
        <p>${escapeHtml(data.reason || "You are not in the same place.")}</p>
        ${travelButton}
      </div>
    `;
    return;
  }

  els.selectedLabel.textContent = `Talking with ${data.citizen.name}`;
  els.leaveVisit.hidden = false;

  const summary = String(data.visit?.summary || "").trim();
  if (summary) {
    const banner = document.createElement("div");
    banner.className = "visit-summary";
    banner.innerHTML = `<strong>Earlier this visit, summarized</strong><p>${escapeHtml(summary)}</p>`;
    els.chatLog.appendChild(banner);
  } else if (data.has_earlier) {
    const banner = document.createElement("div");
    banner.className = "visit-summary muted";
    banner.textContent = "Earlier exchanges in this visit are archived locally.";
    els.chatLog.appendChild(banner);
  }

  if (!data.messages.length) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = `You are visiting ${data.citizen.name} at ${data.citizen.location}.`;
    els.chatLog.appendChild(empty);
  } else {
    for (const row of data.messages) {
      appendChat(data.visitor, row.visitor_text, "visitor", false);
      const citizenText = String(row.citizen_text || "").trim();
      if (citizenText) appendChat(data.citizen.name, citizenText, "citizen", false);
    }
  }

  els.chatLog.scrollTop = els.chatLog.scrollHeight;
}

async function loadCurrentVisit(id) {
  const visitor = els.visitorName.value.trim() || "Visitor";
  localStorage.setItem("agentCityVisitor", visitor);
  const response = await fetch(`/api/visit/${encodeURIComponent(id)}?visitor=${encodeURIComponent(visitor)}`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Could not load visit.");
  renderVisitConversation(data);
  els.previousVisits.hidden = !data.previous_visits?.length;
  currentVisitAccessKey = visitAccessKey(id);
  return data;
}

window.selectCitizen = async function(id, options = {}) {
  selectedCitizen = id;
  sheetCitizenId = id;
  const c = state.citizens.find(x => x.id === id);
  if (!c) return;

  focusedLocation = c.location_id;
  localStorage.setItem("agentCitySelectedCitizen", id);
  localStorage.setItem("agentCityVisitor", els.visitorName.value.trim() || "Visitor");

  els.selectedTitle.textContent = c.name;
  els.selectedLabel.textContent = `Talking with ${c.name}`;
  els.chatInput.disabled = true;
  els.sendButton.disabled = true;
  els.leaveVisit.hidden = false;
  els.previousVisits.hidden = true;
  els.chatLog.innerHTML = `<div class="muted">Loading your visit with ${escapeHtml(c.name)}…</div>`;
  render();

  try {
    const data = await loadCurrentVisit(id);
    els.chatInput.disabled = data.accessible === false;
    els.sendButton.disabled = data.accessible === false;
    if (data.accessible !== false && !options.restore) els.chatInput.focus();
  } catch (error) {
    els.chatLog.innerHTML = `<div class="chat-message system"><strong>System</strong><p>${escapeHtml(error.message)}</p></div>`;
  }
};

function clearVisitSelection(message = "Choose a citizen on the left or on the map, then start a conversation.") {
  selectedCitizen = null;
  localStorage.removeItem("agentCitySelectedCitizen");
  els.selectedTitle.textContent = "Conversation";
  els.selectedLabel.textContent = "Select a citizen.";
  els.chatInput.value = "";
  currentVisitId = null;
  currentSharedActionProposals = [];
  sharedActionBusyId = null;
  renderSharedActionPanel();
  els.chatInput.disabled = true;
  els.sendButton.disabled = true;
  els.leaveVisit.hidden = true;
  els.previousVisits.hidden = true;
  els.visitHistoryPanel.classList.add("hidden");
  els.visitHistoryPanel.innerHTML = "";
  els.chatLog.innerHTML = `<div class="muted">${escapeHtml(message)}</div>`;
  render();
}

els.leaveVisit.addEventListener("click", async () => {
  if (!selectedCitizen) return;
  const visitor = els.visitorName.value.trim() || "Visitor";
  els.leaveVisit.disabled = true;
  try {
    const response = await fetch(`/api/visit/${encodeURIComponent(selectedCitizen)}/leave`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ visitor }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not end visit.");
    clearVisitSelection("Visit ended. Choose someone when you want to visit again.");
  } catch (error) {
    appendChat("System", error.message, "system");
  } finally {
    els.leaveVisit.disabled = false;
  }
});

els.previousVisits.addEventListener("click", async () => {
  if (!selectedCitizen) return;
  const visitor = els.visitorName.value.trim() || "Visitor";
  try {
    const response = await fetch(`/api/visits/${encodeURIComponent(selectedCitizen)}?visitor=${encodeURIComponent(visitor)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not load previous visits.");

    if (!data.visits.length) {
      els.visitHistoryPanel.innerHTML = `<div class="muted">No previous visits yet.</div>`;
    } else {
      els.visitHistoryPanel.innerHTML = data.visits.map(v => `
        <div class="previous-visit-card">
          <strong>${formatMinute(v.started_minute)}${v.ended_minute ? ` → ${formatMinute(v.ended_minute)}` : ""}</strong>
          <p>${escapeHtml(v.summary || "Full transcript archived locally; no compact summary was created for this older visit.")}</p>
        </div>
      `).join("");
    }
    els.visitHistoryPanel.classList.toggle("hidden");
  } catch (error) {
    appendChat("System", error.message, "system");
  }
});

els.citizenSheetVisit.addEventListener("click", async () => {
  const id = els.citizenSheetVisit.dataset.citizenId;
  if (!id) return;
  setView("home");
  await selectCitizen(id);
});

els.locationSheetFocus.addEventListener("click", () => {
  const id = els.locationSheetFocus.dataset.locationId;
  if (!id) return;
  focusedLocation = id;
  setView("home");
  renderMap();
  renderRegionStrip();
});

els.visitorStatus.addEventListener("click", () => {
  if (!visitorPresence) return;
  const id = visitorPresence.traveling ? visitorPresence.to_location_id : visitorPresence.location_id;
  if (id) {
    focusedLocation = id;
    renderLocationDirectory();
    renderLocationSheet();
    setView("locations");
  }
});

els.citizenSearch.addEventListener("input", () => {
  citizenSearchQuery = els.citizenSearch.value;
  renderCitizens();
});

els.viewAllHistory.addEventListener("click", () => {
  setView("records");
  openControlRoomView("history", "Settlement history", "HISTORY");
});

els.visitorName.addEventListener("change", async () => {
  const visitor = els.visitorName.value.trim() || "Visitor";
  els.visitorName.value = visitor;
  localStorage.setItem("agentCityVisitor", visitor);
  await loadVisitorPresence();
  render();
  if (selectedCitizen) await selectCitizen(selectedCitizen, { restore: true });
});

els.toggleRegion.addEventListener("click", () => openControlRoomView("region", "Known region", "REGION"));
els.toggleResources.addEventListener("click", () => openControlRoomView("resources", "Seed Site stores", "STORES"));
els.toggleStructures.addEventListener("click", () => openControlRoomView("structures", "Making & building", "PHYSICAL STATE"));
els.toggleHistory.addEventListener("click", () => openControlRoomView("history", "Settlement history", "HISTORY"));
els.toggleUpdates.addEventListener("click", () => openControlRoomView("updates", "Admin • Updates", "ADMIN"));

async function writeClipboardText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  const ok = document.execCommand("copy");
  area.remove();
  if (!ok) throw new Error("Browser clipboard access is unavailable.");
}

els.copyTroubleshootingSnapshot.addEventListener("click", async () => {
  const button = els.copyTroubleshootingSnapshot;
  const status = els.troubleshootingSnapshotStatus;
  button.disabled = true;
  status.textContent = "Building current local snapshot…";

  try {
    const response = await fetch("/api/diagnostics/troubleshooting-snapshot", {
      cache: "no-store",
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Could not build troubleshooting snapshot.");
    }

    const text = [
      "AGENT CITY TROUBLESHOOTING SNAPSHOT",
      JSON.stringify(data, null, 2),
    ].join("\n");
    await writeClipboardText(text);
    button.textContent = "Copied!";
    status.textContent = "Current public physical state copied. Paste it into ChatGPT when troubleshooting.";
    window.setTimeout(() => {
      button.textContent = "Copy troubleshooting snapshot";
    }, 1800);
  } catch (error) {
    status.textContent = `Copy failed: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

els.mapZoomIn.addEventListener("click", () => {
  setMapZoom(mapZoomLevel * 1.5);
});

els.mapZoomOut.addEventListener("click", () => {
  setMapZoom(mapZoomLevel / 1.5);
});

els.mapZoomReset.addEventListener("click", () => {
  mapZoomLevel = 1;
  mapCenterOverride = null;
  rerenderMapPresentation();
});

els.pauseButton.addEventListener("click", async () => {
  await fetch("/api/pause", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ paused: !state.paused }),
  });
  await loadState();
});

els.chatInput.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" || event.shiftKey) return;
  if (event.isComposing || event.keyCode === 229) return;

  event.preventDefault();

  if (
    chatSubmitting ||
    els.chatInput.disabled ||
    els.sendButton.disabled ||
    !selectedCitizen
  ) return;

  els.chatForm.requestSubmit(els.sendButton);
});

els.chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedCitizen || chatSubmitting) return;

  const message = els.chatInput.value.trim();
  const visitor = els.visitorName.value.trim() || "Visitor";
  if (!message) return;

  chatSubmitting = true;
  appendChat(visitor, message, "visitor");
  els.chatInput.value = "";
  els.chatInput.disabled = true;
  els.sendButton.disabled = true;
  els.sendButton.textContent = "Thinking…";

  try {
    const response = await fetch("/api/talk", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ visitor, citizen_id: selectedCitizen, message }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Conversation failed.");
    appendChat(data.citizen, data.message, "citizen");
    if (data.shared_action_proposal) {
      upsertSharedActionProposal(data.shared_action_proposal);
    }
  } catch (error) {
    appendChat("System", error.message, "system");
  } finally {
    chatSubmitting = false;
    els.chatInput.disabled = false;
    els.sendButton.disabled = false;
    els.sendButton.textContent = "Talk";
    els.chatInput.focus();
  }
});

function appendChat(name, message, cls, scroll = true) {
  if (cls === "citizen" && !String(message || "").trim()) return;

  const empty = els.chatLog.querySelector(":scope > .muted");
  if (empty && els.chatLog.children.length === 1) empty.remove();

  const item = document.createElement("div");
  item.className = `chat-message ${cls}`;
  item.innerHTML = `<strong>${escapeHtml(name)}</strong><p>${escapeHtml(message)}</p>`;
  els.chatLog.appendChild(item);
  if (scroll) els.chatLog.scrollTop = els.chatLog.scrollHeight;
}

async function checkOllama() {
  try {
    const response = await fetch("/api/ollama");
    const data = await response.json();
    if (data.online) {
      const hasModel = data.models?.some(x => x.startsWith("qwen3.5:9b"));
      els.ollamaStatus.textContent = hasModel ? "Ollama: ready" : "Ollama: online, model missing";
      els.ollamaStatus.classList.toggle("good", hasModel);
    } else {
      els.ollamaStatus.textContent = "Ollama: offline";
      els.ollamaStatus.classList.remove("good");
    }
  } catch {
    els.ollamaStatus.textContent = "Ollama: unavailable";
    els.ollamaStatus.classList.remove("good");
  }
}

async function refreshUpdateStatus() {
  els.checkUpdate.disabled = true;
  els.updateStatusTitle.textContent = "Checking…";
  try {
    const response = await fetch("/api/update/status");
    const data = await response.json();

    els.versionLabel.textContent = `Version ${data.current_version || "unknown"}`;
    if (data.manifest_url !== undefined && document.activeElement !== els.updateFeed) {
      els.updateFeed.value = data.manifest_url || "";
    }

    if (data.error) {
      els.updateStatusTitle.textContent = "Update check failed";
      els.updateStatusText.textContent = data.error;
      els.installUpdate.hidden = true;
      return;
    }

    if (!data.configured) {
      els.updateStatusTitle.textContent = "Update feed not configured";
      els.updateStatusText.textContent = "Paste the Agent City update feed URL once, save it, then future releases can be installed here.";
      els.installUpdate.hidden = true;
      return;
    }

    if (data.update_available) {
      els.updateStatusTitle.textContent = `Agent City ${data.latest_version} is available`;
      els.updateStatusText.textContent = data.notes || "A newer version is ready.";
      els.installUpdate.hidden = false;
      els.installUpdate.dataset.version = data.latest_version;
    } else {
      els.updateStatusTitle.textContent = "Agent City is up to date";
      els.updateStatusText.textContent = `Current version: ${data.current_version}`;
      els.installUpdate.hidden = true;
    }
  } catch (error) {
    els.updateStatusTitle.textContent = "Update check unavailable";
    els.updateStatusText.textContent = error.message;
    els.installUpdate.hidden = true;
  } finally {
    els.checkUpdate.disabled = false;
  }
}

els.saveUpdateFeed.addEventListener("click", async () => {
  els.saveUpdateFeed.disabled = true;
  try {
    const response = await fetch("/api/update/settings", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ manifest_url: els.updateFeed.value.trim() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not save update feed.");
    await refreshUpdateStatus();
  } catch (error) {
    els.updateStatusTitle.textContent = "Could not save feed";
    els.updateStatusText.textContent = error.message;
  } finally {
    els.saveUpdateFeed.disabled = false;
  }
});

els.checkUpdate.addEventListener("click", refreshUpdateStatus);

els.installUpdate.addEventListener("click", async () => {
  const version = els.installUpdate.dataset.version || "the new version";
  if (!confirm(`Install Agent City ${version}? The city will pause, back up its data, update, and restart.`)) return;

  els.installUpdate.disabled = true;
  els.updateStatusTitle.textContent = "Preparing update…";
  els.updateStatusText.textContent = "Backing up the civilization and staging the new program files.";

  try {
    const response = await fetch("/api/update/install", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Update failed.");

    els.updateStatusTitle.textContent = "Restarting Agent City…";
    els.updateStatusText.textContent = "The civilization is backed up. This page will reconnect automatically.";

    const reconnect = setInterval(async () => {
      try {
        const ping = await fetch("/api/state", { cache: "no-store" });
        if (ping.ok) {
          clearInterval(reconnect);
          location.reload();
        }
      } catch {}
    }, 1500);
  } catch (error) {
    els.updateStatusTitle.textContent = "Update stopped safely";
    els.updateStatusText.textContent = error.message;
    els.installUpdate.disabled = false;
  }
});

bindViewNavigation();
loadState();
checkOllama();
refreshUpdateStatus();
setInterval(loadState, 4000);
setInterval(checkOllama, 15000);
setInterval(refreshUpdateStatus, UPDATE_REFRESH_MS);
