let state = null;
let visitorPresence = null;
let selectedCitizen = null;
let focusedLocation = "seed_site";
let openControlView = "history";
let currentVisitAccessKey = null;

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

const els = {
  simTime: document.getElementById("sim-time"),
  pauseButton: document.getElementById("pause-button"),
  ollamaStatus: document.getElementById("ollama-status"),
  citizens: document.getElementById("citizens"),
  routeLayer: document.getElementById("route-layer"),
  mapLayer: document.getElementById("map-layer"),
  regionStrip: document.getElementById("region-strip"),
  worldFocus: document.getElementById("world-focus"),
  locations: document.getElementById("locations"),
  resourceBalance: document.getElementById("resource-balance"),
  citizenCargo: document.getElementById("citizen-cargo"),
  structures: document.getElementById("structures"),
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

function render() {
  els.simTime.textContent = `${state.sim_label} • ${state.paused ? "Paused" : "Running"}`;
  els.pauseButton.textContent = state.paused ? "Resume" : "Pause";
  renderVisitorStatus();
  computeLocationPositions();

  renderCitizens();
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
  els.citizens.innerHTML = state.citizens.map(c => {
    const cargo = inventoryFor(c.id);
    const job = activeJobFor(c.id);
    const progress = jobProgress(job);
    const destination = job?.action === "travel" ? locationById(job.target)?.name : null;
    const where = destination ? `En route: ${c.location} → ${destination}` : c.location;
    const progressMarkup = progress ? `
      <div class="job-progress-meta">
        <span>${progress.elapsed} / ${progress.total} sim min</span>
        <span>ETA ${formatMinute(job.end_minute)}</span>
      </div>
      <div class="job-progress-track"><span style="width:${progress.percent}%"></span></div>
    ` : "";

    return `
      <button class="citizen-row ${selectedCitizen === c.id ? "selected" : ""}" onclick="selectCitizen('${c.id}')">
        <div class="citizen-row-top">
          <div>
            <div class="citizen-name">${escapeHtml(c.name)}</div>
            <div class="muted citizen-role">${escapeHtml(c.aptitude)}</div>
          </div>
          <div class="citizen-meter">
            <span>⚡ ${Math.round(c.energy)}%</span>
            <span>⛭ ${Math.round(c.integrity)}%</span>
          </div>
        </div>
        <div class="activity">${escapeHtml(c.current_activity)}</div>
        ${progressMarkup}
        <div class="location-line">${escapeHtml(where)}${cargo ? ` • Carrying ${escapeHtml(cargo)}` : ""}</div>
      </button>
    `;
  }).join("");
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
      >${escapeHtml(initialsFor(c.name))}</button>
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
      >${escapeHtml(initialsFor(person.name))}</button>
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

function renderCitizenConversationHistory() {
  const allConversations = state.citizen_conversations || [];
  const conversations = allConversations.slice(0, 12);
  const snapshotKeys = new Set(allConversations.map(c =>
    normalizedConversationKey(c.sim_minute, c.initiator_name, c.target_name, c.location_name)
  ));

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
    const summary = String(c.summary || "").trim() || "No compact summary is available for this exchange.";
    const initiatorText = String(c.initiator_text || "").trim();
    const targetText = String(c.target_text || "").trim();
    const hasTranscript = Boolean(initiatorText || targetText);

    return `
      <article class="conversation-card">
        <div class="conversation-card-head">
          <div class="conversation-people">
            <strong>${escapeHtml(c.initiator_name)}</strong>
            <span aria-hidden="true">↔</span>
            <strong>${escapeHtml(c.target_name)}</strong>
          </div>
          <time>${formatMinute(c.sim_minute)}</time>
        </div>
        <div class="conversation-location">At ${escapeHtml(c.location_name)}</div>
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
          <span>Chronology record</span>
          <p>${escapeHtml(h.message)}</p>
        </div>
        <div class="conversation-record-note">
          Chronology confirms this conversation, but its exchange text is not included in the current UI state snapshot.
        </div>
      </article>
    `;
  });

  const sections = [];
  if (storedCards.length) sections.push(storedCards.join(""));
  if (chronologyCards.length) {
    sections.push(`
      <div class="conversation-gap-label">Chronology-only conversation records</div>
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

  els.structures.innerHTML = state.structures.map(s => `
    <div class="list-row"><span>${escapeHtml(s.name)}</span><strong>${Math.round(s.condition)}%</strong></div>
  `).join("");

  renderCitizenConversationHistory();

  els.history.innerHTML = state.history.map(h => `
    <div class="history-entry">
      <div class="history-dot"></div>
      <div><strong>${formatMinute(h.sim_minute)}</strong><p>${escapeHtml(h.message)}</p></div>
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
    els.selectedLabel.textContent = "Not at the same location";
    els.chatInput.disabled = true;
    els.sendButton.disabled = true;
    els.leaveVisit.hidden = true;

    const route = visitorPresence && !visitorPresence.traveling
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
els.toggleStructures.addEventListener("click", () => openControlRoomView("structures", "Structures", "STRUCTURES"));
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

loadState();
checkOllama();
refreshUpdateStatus();
setInterval(loadState, 4000);
setInterval(checkOllama, 15000);
