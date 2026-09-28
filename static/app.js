let state = null;
let visitorPresence = null;
let selectedCitizen = null;
let focusedLocation = "seed_site";
let openControlView = "history";
let currentView = "home";
let sheetCitizenId = null;
let citizenSearchQuery = "";
let currentVisitAccessKey = null;
const citizenKnowledgeCache = new Map();
const locationKnowledgeCache = new Map();
const knowledgeLoading = new Set();
const KNOWLEDGE_REFRESH_MS = 12000;

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

// Drop-in 2D art manifest. Keep values null until authoritative identity art exists.
// Later art can be added without changing the layout/rendering contract.
const CITIZEN_AVATAR_ASSETS = {
  aris: { full: null, token: null },
  bex: { full: null, token: null },
  cato: { full: null, token: null },
  iri: { full: null, token: null },
  noma: { full: null, token: null },
  vale: { full: null, token: null },
};

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
  locations: document.getElementById("locations"),
  resourceBalance: document.getElementById("resource-balance"),
  citizenCargo: document.getElementById("citizen-cargo"),
  projects: document.getElementById("projects"),
  equipment: document.getElementById("equipment"),
  structures: document.getElementById("structures"),
  maintenanceEvents: document.getElementById("maintenance-events"),
  history: document.getElementById("history"),
  citizenConversations: document.getElementById("citizen-conversations"),
  visitorStatus: document.getElementById("visitor-status"),
  selectedTitle: document.getElementById("selected-title"),
  selectedLabel: document.getElementById("selected-label"),
  visitorName: document.getElementById("visitor-name"),
  chatLog: document.getElementById("chat-log"),
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

function isTravelingCitizen(citizen) {
  return activeJobFor(citizen.id)?.action === "travel";
}

function citizensAtLocation(locationId) {
  return state.citizens.filter(c => c.location_id === locationId && !isTravelingCitizen(c));
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

function computeLocationPositions() {
  const center = { x: 50, y: 52 };
  const locations = state?.locations || [];
  const routes = state?.routes || [];
  const directRoutes = routes.filter(r => r.a === "seed_site" || r.b === "seed_site");
  const distances = directRoutes
    .map(r => Number(r.distance_km))
    .filter(Number.isFinite);

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
function avatarHueFor(citizenId) {
  const text = String(citizenId || "");
  let hash = 0;
  for (const char of text) hash = ((hash * 31) + char.charCodeAt(0)) % 360;
  return hash;
}

function citizenVisualState(citizen) {
  const action = activeJobFor(citizen.id)?.action;
  if (action === "travel") return "traveling";
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

  els.citizenPortraitArt.className = `citizen-avatar avatar-full state-${stateClass} ${asset ? "has-image" : "fallback-avatar"}`;
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

function render() {
  els.simTime.textContent = `${state.sim_label} • ${state.paused ? "Paused" : "Running"}`;
  els.pauseButton.textContent = state.paused ? "Resume" : "Pause";
  renderVisitorStatus();
  computeLocationPositions();

  renderCitizens();
  renderMaintenanceAlerts();
  renderRecentActivity();
  renderCitizenDirectory();
  renderCitizenSheet();
  renderLocationDirectory();
  renderLocationSheet();
  renderMap();
  renderRegionStrip();
  renderDrawerLists();
}

function renderVisitorStatus() {
  if (!visitorPresence) {
    els.visitorStatus.textContent = "Visitor: unavailable";
    return;
  }
  const visitor = els.visitorName.value.trim() || "Visitor";
  if (visitorPresence.traveling) {
    els.visitorStatus.textContent = `${visitor}: traveling to ${visitorPresence.to_location_name} • ${visitorPresence.remaining_minutes}m left`;
  } else {
    els.visitorStatus.textContent = `${visitor}: ${visitorPresence.location_name}`;
  }
}

function renderCitizens() {
  const query = citizenSearchQuery.trim().toLowerCase();
  const visible = (state.citizens || []).filter(c =>
    !query || String(c.name || "").toLowerCase().includes(query)
  );

  els.citizens.innerHTML = visible.length ? visible.map(c => {
    const cargo = inventoryFor(c.id);
    const job = activeJobFor(c.id);
    const destination = job?.action === "travel" ? locationById(job.target)?.name : null;
    const where = destination ? `${c.location} → ${destination}` : c.location;
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
        <div class="compact-vitals">
          <span>⚡ ${Math.round(c.energy)}%</span>
          <span>⛭ ${Math.round(c.integrity)}%</span>
        </div>
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

  els.citizenSheetBody.innerHTML = `
    <div class="sheet-card">
      <span class="sheet-label">Physical state</span>
      <strong>${escapeHtml(locationText)}</strong>
      <div class="vital-row"><span>Energy <b>${Math.round(citizen.energy)}%</b></span><span>Integrity <b>${Math.round(citizen.integrity)}%</b></span></div>
    </div>
    <div class="sheet-card">
      <span class="sheet-label">Maintenance state</span>
      <div class="maintenance-metric-grid">
        <div>
          <span>Battery health</span>
          <strong>${Number.isFinite(batteryHealth) ? `${escapeHtml(trimNumber(batteryHealth))}%` : "Unknown"}</strong>
          <small>${escapeHtml(conditionStateLabel(citizen.battery_state))}${citizen.battery_replacement_due ? " • replacement due" : ""}</small>
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
    <div class="sheet-card">
      <span class="sheet-label">Current configuration</span>
      <strong>Mechanical citizen</strong>
      <p>Visual identity art is not yet authoritative. Equipment below reflects validated physical state only.</p>
    </div>
    ${activeJobMarkup}
    <div class="sheet-card">
      <span class="sheet-label">Cargo</span>
      <strong>${Number.isFinite(cargoCapacity) ? `${escapeHtml(trimNumber(cargoTotal))} / ${escapeHtml(trimNumber(cargoCapacity))} units` : `${escapeHtml(trimNumber(cargoTotal))} units carried`}</strong>
      <div class="sheet-list">${cargoMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Equipped gear</span>
      <div class="sheet-list">${gearMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Projects</span>
      <div class="sheet-list">${projectMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Known discoveries & research</span>
      <div class="knowledge-facts">${citizenKnowledgeMarkup(citizen.id)}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Experiments</span>
      <div class="sheet-list">${experimentMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Learned processes</span>
      <div class="sheet-list">${processMarkup}</div>
    </div>
    <div class="sheet-card sheet-card-wide">
      <span class="sheet-label">Recent chronology</span>
      <div class="sheet-notes">${historyMarkup}</div>
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
  els.routeLayer.innerHTML = (state.routes || []).map(route => {
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
  }).join("");

  return labels.join("");
}

function renderMap() {
  const routeLabels = renderRoutes();
  const nodes = state.locations.map(loc => renderLocationNode(loc)).join("");
  const travelersList = state.citizens.filter(c => isTravelingCitizen(c));
  const travelers = travelersList.map(c => {
    const job = activeJobFor(c.id);
    const progress = jobProgress(job);
    const pos = interpolatedPosition(c.location_id, job.target, progress?.fraction || 0);
    const peers = travelersList.filter(peer => {
      const peerJob = activeJobFor(peer.id);
      return peerJob?.action === "travel" && sameRoute(c.location_id, job.target, peer.location_id, peerJob.target);
    });
    const laneIndex = peers.findIndex(peer => peer.id === c.id);
    const laneOffset = (laneIndex - ((peers.length - 1) / 2)) * 18;
    const from = positionForLocation(c.location_id);
    const to = positionForLocation(job.target);
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const magnitude = Math.hypot(dx, dy) || 1;
    const offsetX = (-dy / magnitude) * laneOffset;
    const offsetY = (dx / magnitude) * laneOffset;
    const targetName = locationById(job.target)?.name || job.target;

    return `
      <button
        class="map-citizen traveling ${selectedCitizen === c.id ? "selected" : ""}"
        style="left:calc(${pos.x}% + ${offsetX}px); top:calc(${pos.y}% + ${offsetY}px);"
        title="${escapeHtml(c.name)} • traveling to ${escapeHtml(targetName)} • ${progress?.percent || 0}%"
        aria-label="${escapeHtml(c.name)} traveling to ${escapeHtml(targetName)}"
        onclick="selectCitizen('${c.id}')"
      >${citizenAvatarMarkup(c, "map")}</button>
    `;
  }).join("");

  let visitorMarker = "";
  if (visitorPresence) {
    let pos;
    let label;
    let offset = { x: 0, y: -26 };
    let locationId;

    if (visitorPresence.traveling) {
      pos = interpolatedPosition(
        visitorPresence.from_location_id,
        visitorPresence.to_location_id,
        visitorPresence.progress || 0
      );
      locationId = visitorPresence.to_location_id;
      label = `${els.visitorName.value.trim() || "Visitor"} • traveling to ${visitorPresence.to_location_name}`;
    } else {
      locationId = visitorPresence.location_id;
      pos = positionForLocation(locationId);
      offset = LOCATION_PRESENTATION[locationId]?.visitor || offset;
      label = `${els.visitorName.value.trim() || "Visitor"} • ${visitorPresence.location_name}`;
    }

    visitorMarker = `
      <button
        class="map-visitor ${visitorPresence.traveling ? "traveling" : ""}"
        style="left:calc(${pos.x}% + ${offset.x}px); top:calc(${pos.y}% + ${offset.y}px);"
        title="${escapeHtml(label)}"
        onclick="focusLocation('${locationId}')"
      >YOU</button>
    `;
  }

  els.mapLayer.innerHTML = routeLabels + nodes + travelers + visitorMarker;
  updateWorldFocus();
}

function renderLocationNode(loc) {
  const pos = positionForLocation(loc.id);
  const people = citizensAtLocation(loc.id);
  const deposits = depositsForLocation(loc.id);
  const presentation = LOCATION_PRESENTATION[loc.id] || {
    label: "below",
    cluster: { x: 0, y: 38 },
  };
  const selected = selectedCitizen ? state.citizens.find(c => c.id === selectedCitizen) : null;
  const selectedHere = selected && !isTravelingCitizen(selected) && selected.location_id === loc.id;
  const nodeTitle = `${loc.name} • ${loc.surveyed ? "Surveyed" : "Not yet surveyed"}${deposits.length ? ` • ${deposits.length} confirmed deposit${deposits.length > 1 ? "s" : ""}` : ""}`;

  const citizenTokens = people.map((person, index) => {
    const cluster = presentation.cluster || { x: 0, y: 38 };
    const offset = clusterOffset(index, people.length);
    return `
      <button
        class="map-citizen ${selectedCitizen === person.id ? "selected" : ""}"
        style="left:calc(${pos.x}% + ${cluster.x + offset.x}px); top:calc(${pos.y}% + ${cluster.y + offset.y}px);"
        title="${escapeHtml(person.name)} • ${escapeHtml(person.current_activity || person.location)}"
        aria-label="${escapeHtml(person.name)} at ${escapeHtml(loc.name)}"
        onclick="selectCitizen('${person.id}')"
      >${citizenAvatarMarkup(person, "map")}</button>
    `;
  }).join("");

  return `
    <button
      class="map-node label-${presentation.label || "below"} ${focusedLocation === loc.id ? "focused" : ""} ${selectedHere ? "selected-location" : ""}"
      style="left:${pos.x}%; top:${pos.y}%;"
      title="${escapeHtml(nodeTitle)}"
      onclick="focusLocation('${loc.id}')"
    >
      <span class="node-dot"></span>
      <span class="node-label">${escapeHtml(loc.name)}</span>
    </button>
    ${citizenTokens}
  `;
}

function updateWorldFocus() {
  const loc = locationById(focusedLocation) || locationById("seed_site");
  const deposits = depositsForLocation(loc.id);
  const people = citizensAtLocation(loc.id).map(c => c.name);

  let visitorAction = "";
  if (visitorPresence) {
    if (visitorPresence.traveling) {
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

function renderCitizenConversationHistory() {
  const allConversations = state.citizen_conversations || [];
  const conversations = allConversations.slice(0, 12);

  const completionHistory = new Map();
  for (const row of state.history || []) {
    const conversationId = conversationIdFromChronology(row.message);
    if (conversationId != null) completionHistory.set(conversationId, row);
  }

  const snapshotKeys = new Set(allConversations.map(c =>
    normalizedConversationKey(c.sim_minute, c.initiator_name, c.target_name, c.location_name)
  ));

  // Legacy conversation chronology can predate canonical completion IDs. Preserve
  // those real chronology rows when their exchange is outside the current snapshot.
  const chronologyOnly = (state.history || [])
    .filter(h => h.category === "conversation")
    .filter(h => {
      const parsed = parseConversationHistoryMessage(h.message);
      if (!parsed) return false;
      const key = normalizedConversationKey(
        h.sim_minute,
        parsed.personA,
        parsed.personB,
        parsed.locationName
      );
      return !snapshotKeys.has(key);
    })
    .slice(0, 6);

  const storedCards = conversations.map(c => {
    const conversationId = Number(c.id ?? c.source_id);
    const completion = Number.isFinite(conversationId) ? completionHistory.get(conversationId) : null;
    const summary = String(c.summary || "").trim() || "No compact summary is available for this exchange.";
    const initiatorText = String(c.initiator_text || "").trim();
    const targetText = String(c.target_text || "").trim();
    const hasTranscript = Boolean(initiatorText || targetText);
    const sourceJobId = c.source_job_id != null ? String(c.source_job_id) : "";
    const idLabel = Number.isFinite(conversationId) ? `Conversation #${conversationId}` : "Conversation record";

    return `
      <article class="conversation-card" data-conversation-id="${Number.isFinite(conversationId) ? escapeHtml(String(conversationId)) : ""}">
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
          ${completion ? `<span>Completed ${escapeHtml(formatMinute(completion.sim_minute))}</span>` : ""}
        </div>
        <div class="conversation-summary">
          <span>Summary</span>
          <p>${escapeHtml(summary)}</p>
        </div>
        ${hasTranscript ? `
          <details class="conversation-transcript">
            <summary>Read exchange</summary>
            ${initiatorText ? `<div><strong>${escapeHtml(c.initiator_name)}</strong><span>${escapeHtml(initiatorText)}</span></div>` : ""}
            ${targetText ? `<div><strong>${escapeHtml(c.target_name)}</strong><span>${escapeHtml(targetText)}</span></div>` : ""}
          </details>
        ` : '<div class="conversation-record-note">Exchange text is not available in this state snapshot.</div>'}
      </article>
    `;
  });

  const chronologyCards = chronologyOnly.map(h => {
    const parsed = parseConversationHistoryMessage(h.message);
    return `
      <article class="conversation-card chronology-only">
        <div class="conversation-card-head">
          <div class="conversation-people">
            <strong>${escapeHtml(parsed.personA)}</strong>
            <span aria-hidden="true">↔</span>
            <strong>${escapeHtml(parsed.personB)}</strong>
          </div>
          <time>${formatMinute(h.sim_minute)}</time>
        </div>
        <div class="conversation-location">At ${escapeHtml(parsed.locationName)}</div>
        <div class="conversation-summary">
          <span>Legacy chronology record</span>
          <p>${escapeHtml(h.message)}</p>
        </div>
        <div class="conversation-record-note">
          Chronology confirms this conversation, but its exchange text is outside the current state snapshot.
        </div>
      </article>
    `;
  });

  const sections = [];
  if (storedCards.length) sections.push(storedCards.join(""));
  if (chronologyCards.length) {
    sections.push(`
      <div class="conversation-gap-label">Older chronology-only conversation records</div>
      ${chronologyCards.join("")}
    `);
  }

  els.citizenConversations.innerHTML = sections.length
    ? sections.join("")
    : '<div class="muted conversation-empty">No citizen-to-citizen conversations recorded yet.</div>';
}

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

  renderCitizenConversationHistory();

  els.history.innerHTML = state.history.map(h => `
    <div class="history-entry ${h.category === "diagnostic" ? "diagnostic" : ""}">
      <div class="history-dot"></div>
      <div>
        <strong>${formatMinute(h.sim_minute)}${h.category === "diagnostic" ? " • diagnostic" : ""}</strong>
        <p>${escapeHtml(h.message)}</p>
      </div>
    </div>
  `).join("");
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
}

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

function renderVisitConversation(data) {
  els.chatLog.innerHTML = "";
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

els.pauseButton.addEventListener("click", async () => {
  await fetch("/api/pause", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ paused: !state.paused }),
  });
  await loadState();
});

els.chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedCitizen) return;

  const message = els.chatInput.value.trim();
  const visitor = els.visitorName.value.trim() || "Visitor";
  if (!message) return;

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
  } catch (error) {
    appendChat("System", error.message, "system");
  } finally {
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
