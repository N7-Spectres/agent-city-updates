let state = null;
let selectedCitizen = null;
let focusedLocation = "seed_site";
let openDrawer = null;

const LOCATION_POSITIONS = {
  seed_site: { x: 50, y: 55 },
  northern_ridge: { x: 50, y: 16 },
  rocky_basin: { x: 78, y: 42 },
  southern_flats: { x: 50, y: 85 },
  resin_grove: { x: 23, y: 42 },
};

const els = {
  simTime: document.getElementById("sim-time"),
  pauseButton: document.getElementById("pause-button"),
  ollamaStatus: document.getElementById("ollama-status"),
  citizens: document.getElementById("citizens"),
  mapLayer: document.getElementById("map-layer"),
  regionStrip: document.getElementById("region-strip"),
  worldFocus: document.getElementById("world-focus"),
  locations: document.getElementById("locations"),
  resources: document.getElementById("resources"),
  structures: document.getElementById("structures"),
  history: document.getElementById("history"),
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
  detailDrawer: document.getElementById("detail-drawer"),
  detailEyebrow: document.getElementById("detail-eyebrow"),
  detailTitle: document.getElementById("detail-title"),
  closeDrawer: document.getElementById("close-drawer"),
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

async function loadState() {
  const response = await fetch("/api/state");
  state = await response.json();
  render();

  if (!restoredVisit) {
    restoredVisit = true;
    const savedVisitor = localStorage.getItem("agentCityVisitor");
    if (savedVisitor) els.visitorName.value = savedVisitor;

    const savedCitizen = localStorage.getItem("agentCitySelectedCitizen");
    if (savedCitizen && state.citizens.some(c => c.id === savedCitizen)) {
      await selectCitizen(savedCitizen, { restore: true });
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

function citizensAtLocation(locationId) {
  return state.citizens.filter(c => c.location_id === locationId);
}

function trimNumber(value) {
  const n = Number(value);
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

function render() {
  els.simTime.textContent = `${state.sim_label} • ${state.paused ? "Paused" : "Running"}`;
  els.pauseButton.textContent = state.paused ? "Resume" : "Pause";

  renderCitizens();
  renderMap();
  renderRegionStrip();
  renderDrawerLists();
}

function renderCitizens() {
  els.citizens.innerHTML = state.citizens.map(c => {
    const cargo = inventoryFor(c.id);
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
        <div class="location-line">${escapeHtml(c.location)}${cargo ? ` • Carrying ${escapeHtml(cargo)}` : ""}</div>
      </button>
    `;
  }).join("");
}

function renderMap() {
  els.mapLayer.innerHTML = state.locations.map(loc => renderLocationNode(loc)).join("");
  updateWorldFocus();
}

function renderLocationNode(loc) {
  const pos = LOCATION_POSITIONS[loc.id] || { x: 50, y: 50 };
  const people = citizensAtLocation(loc.id);
  const deposits = depositsForLocation(loc.id);

  const citizenDots = people.map((person, index) => {
    const offset = (index - (people.length - 1) / 2) * 14;
    return `
      <button
        class="map-citizen ${selectedCitizen === person.id ? "selected" : ""}"
        style="left: calc(${pos.x}% + ${offset}px); top: calc(${pos.y}% + 20px);"
        title="${escapeHtml(person.name)}"
        onclick="selectCitizen('${person.id}')"
      ></button>
    `;
  }).join("");

  return `
    <button
      class="map-node ${focusedLocation === loc.id ? "focused" : ""}"
      style="left:${pos.x}%; top:${pos.y}%;"
      onclick="focusLocation('${loc.id}')"
    >
      <span class="node-dot"></span>
      <span class="node-label">${escapeHtml(loc.name)}</span>
      <span class="node-sub">${loc.surveyed ? "Surveyed" : "Not yet surveyed"}${deposits.length ? ` • ${deposits.length} deposit${deposits.length > 1 ? "s" : ""}` : ""}</span>
    </button>
    ${citizenDots}
  `;
}

function updateWorldFocus() {
  const loc = locationById(focusedLocation) || locationById("seed_site");
  const deposits = depositsForLocation(loc.id);
  const people = citizensAtLocation(loc.id).map(c => c.name);

  els.worldFocus.innerHTML = `
    <strong>${escapeHtml(loc.name)}</strong>
    <p>${escapeHtml(loc.description)}</p>
    <div class="focus-meta">
      <span>${loc.surveyed ? "Surveyed" : "Not yet surveyed"}</span>
      <span>${deposits.length ? `Deposits: ${deposits.map(d => escapeHtml(d.material)).join(", ")}` : "No confirmed deposits"}</span>
      <span>${people.length ? `Present: ${people.map(escapeHtml).join(", ")}` : "No citizens present"}</span>
    </div>
  `;
}

function renderRegionStrip() {
  els.regionStrip.innerHTML = state.locations.map(loc => {
    const deposits = depositsForLocation(loc.id);
    const people = citizensAtLocation(loc.id);
    return `
      <button class="region-mini ${focusedLocation === loc.id ? "focused" : ""}" onclick="focusLocation('${loc.id}')">
        <strong>${escapeHtml(loc.name)}</strong>
        <span>${loc.surveyed ? "Surveyed" : "Unsurveyed"}</span>
        <span>${deposits.length ? deposits.map(d => escapeHtml(d.material)).join(", ") : "No deposits"}</span>
        <span>${people.length ? `Present: ${people.length}` : "Empty"}</span>
      </button>
    `;
  }).join("");
}

function renderDrawerLists() {
  els.locations.innerHTML = state.locations.map(loc => {
    const known = depositsForLocation(loc.id);
    const people = citizensAtLocation(loc.id).map(c => c.name);
    return `
      <div class="location-card">
        <div class="location-name">${escapeHtml(loc.name)}</div>
        <div class="muted">${escapeHtml(loc.description)}</div>
        <div class="location-meta">${loc.surveyed ? "Surveyed" : "Not yet surveyed"}</div>
        <div class="small">${known.length ? `Confirmed: ${known.map(d => escapeHtml(d.material)).join(", ")}` : "No confirmed deposits"}</div>
        <div class="small">${people.length ? `Present: ${people.map(escapeHtml).join(", ")}` : "No citizens present"}</div>
      </div>
    `;
  }).join("");

  els.resources.innerHTML = state.resources.map(r => `
    <div class="list-row"><span>${escapeHtml(r.name)}</span><strong>${trimNumber(r.amount)}</strong></div>
  `).join("");

  els.structures.innerHTML = state.structures.map(s => `
    <div class="list-row"><span>${escapeHtml(s.name)}</span><strong>${Math.round(s.condition)}%</strong></div>
  `).join("");

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

function openDrawerView(name, title, eyebrow = "DETAILS") {
  openDrawer = name;
  els.detailDrawer.classList.remove("hidden");
  els.detailEyebrow.textContent = eyebrow;
  els.detailTitle.textContent = title;

  Object.entries(els.detailViews).forEach(([key, el]) => {
    el.classList.toggle("hidden", key !== name);
  });

  document.querySelectorAll(".tool-button").forEach(btn => {
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

function closeDrawer() {
  openDrawer = null;
  els.detailDrawer.classList.add("hidden");
  Object.values(els.detailViews).forEach(el => el.classList.add("hidden"));
  document.querySelectorAll(".tool-button").forEach(btn => btn.classList.remove("active"));
}

window.focusLocation = function(id) {
  focusedLocation = id;
  renderMap();
};

function renderVisitConversation(data) {
  els.chatLog.innerHTML = "";
  els.visitHistoryPanel.classList.add("hidden");
  els.visitHistoryPanel.innerHTML = "";

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
      appendChat(data.citizen.name, row.citizen_text, "citizen", false);
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
    await loadCurrentVisit(id);
    els.chatInput.disabled = false;
    els.sendButton.disabled = false;
    if (!options.restore) els.chatInput.focus();
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
  if (selectedCitizen) await selectCitizen(selectedCitizen, { restore: true });
});

els.toggleRegion.addEventListener("click", () => openDrawer === "region" ? closeDrawer() : openDrawerView("region", "Known region", "REGION"));
els.toggleResources.addEventListener("click", () => openDrawer === "resources" ? closeDrawer() : openDrawerView("resources", "Seed Site stores", "STORES"));
els.toggleStructures.addEventListener("click", () => openDrawer === "structures" ? closeDrawer() : openDrawerView("structures", "Structures", "STRUCTURES"));
els.toggleHistory.addEventListener("click", () => openDrawer === "history" ? closeDrawer() : openDrawerView("history", "Settlement history", "HISTORY"));
els.toggleUpdates.addEventListener("click", () => openDrawer === "updates" ? closeDrawer() : openDrawerView("updates", "Admin • Updates", "ADMIN"));
els.closeDrawer.addEventListener("click", closeDrawer);

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
