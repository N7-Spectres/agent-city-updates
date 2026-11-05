// Agent City v2 — the visitor's view of the world.
//
// Presentation only. The server is the simulation: it says where things are
// and accepts or refuses where the visitor walks. Planet coordinates are
// meters with +x east and +y north; three.js uses +x east, +y up, -z north.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const VISITOR = "N7";
const WALK_SPEED = 1.6;      // m/s
const JOG_SPEED = 3.6;       // m/s (server allows up to 4)
const TURN_SPEED = 2.2;      // rad/s
const BODY_RADIUS = 0.35;
const NEARBY_RADIUS = 3.5;
const MOVE_SEND_MS = 200;

// Citizens with a finished, rigged model. Others use a simple blockout body
// until their model is made.
const CITIZEN_MODELS = {
  cato: { src: "/static/assets/citizens/cato/world/model.glb", idle: "Idle", walk: "Walk" },
  iri: { src: "/static/assets/citizens/iri/world/model.glb", idle: "Idle", walk: "Walk" },
};
const CITIZEN_COLORS = {
  aris: 0xd98b3a, bex: 0x5aa7c9, cato: 0x8f9aa6, iri: 0xc36f8c, noma: 0x7fbf6a, vale: 0xb9a35a,
};

const toScene = (x, y, h = 0) => new THREE.Vector3(x, h, -y);

// --- renderer, scene, camera ------------------------------------------------
const canvas = document.getElementById("world");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(58, 1, 0.1, 4000);
const hemi = new THREE.HemisphereLight(0xcfe3f0, 0x3a2c20, 0.9);
const sun = new THREE.DirectionalLight(0xfff2dd, 2.2);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -40, right: 40, top: 40, bottom: -40, near: 1, far: 300 });
sun.shadow.bias = -0.0005;
scene.add(hemi, sun, sun.target);
scene.fog = new THREE.Fog(0xb9c7cf, 250, 1600);

function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

// --- terrain ------------------------------------------------------------------
let terrain = null; // {size, res, heights, origin}

function heightAt(x, y) {
  if (!terrain) return 0;
  const { size, res, heights } = terrain;
  const half = size / 2, step = size / (res - 1);
  const fx = Math.min(Math.max((x + half) / step, 0), res - 1.001);
  const fy = Math.min(Math.max((y + half) / step, 0), res - 1.001);
  const ix = Math.floor(fx), iy = Math.floor(fy), tx = fx - ix, ty = fy - iy;
  const h = (c, r) => heights[r * res + c];
  const top = h(ix, iy) * (1 - tx) + h(ix + 1, iy) * tx;
  const bottom = h(ix, iy + 1) * (1 - tx) + h(ix + 1, iy + 1) * tx;
  return top * (1 - ty) + bottom * ty;
}

function buildTerrain(data) {
  terrain = { size: data.size_m, res: data.resolution, heights: data.heights, origin: data.origin_height_m };
  const { size, res, heights } = terrain;
  const geo = new THREE.PlaneGeometry(size, size, res - 1, res - 1);
  geo.rotateX(-Math.PI / 2); // plane now lies in x/z; row 0 is at z = -size/2 (north)
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const low = new THREE.Color(0x7d6a55), mid = new THREE.Color(0xa88a68), high = new THREE.Color(0xcdb79a);
  const c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    const h = heightAt(x, -z);
    pos.setY(i, h);
    const rel = (h - terrain.origin) / 50;
    if (rel < 0) c.copy(low).lerp(mid, Math.max(0, 1 + rel));
    else c.copy(mid).lerp(high, Math.min(1, rel));
    colors.set([c.r, c.g, c.b], i * 3);
  }
  geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95 }));
  mesh.receiveShadow = true;
  scene.add(mesh);

  // Surface outcrops: what anyone can see, not what it is.
  const rockGeo = new THREE.DodecahedronGeometry(1, 0);
  const rockMat = new THREE.MeshStandardMaterial({ color: 0x4a4038, roughness: 1, flatShading: true });
  const paleMat = new THREE.MeshStandardMaterial({ color: 0xe6dcc6, roughness: 1 });
  for (const o of data.outcrops || []) {
    const h = heightAt(o.x_m, o.y_m);
    if (o.look === "dark_rock") {
      for (let k = 0; k < 5; k++) {
        const r = new THREE.Mesh(rockGeo, rockMat);
        const s = 0.6 + ((k * 37) % 10) / 6;
        const ox = o.x_m + Math.cos(k * 2.4) * k * 1.2, oy = o.y_m + Math.sin(k * 2.4) * k * 1.2;
        r.scale.set(s, s * 0.7, s);
        r.position.copy(toScene(ox, oy, heightAt(ox, oy) + s * 0.25));
        r.rotation.set(k, k * 0.7, 0);
        r.castShadow = true;
        scene.add(r);
      }
    } else {
      const patch = new THREE.Mesh(new THREE.CircleGeometry(6, 20), paleMat);
      patch.rotation.x = -Math.PI / 2;
      patch.position.copy(toScene(o.x_m, o.y_m, h + 0.08));
      scene.add(patch);
    }
  }
}

// --- facility -----------------------------------------------------------------
const solids = []; // boxes the visitor cannot walk through
const placeZones = [];
const spinners = []; // small moving parts so the station feels alive

const mats = {
  floor: new THREE.MeshStandardMaterial({ color: 0x4b5258, roughness: 0.8 }),
  wall: new THREE.MeshStandardMaterial({ color: 0xd9d4c7, roughness: 0.7 }),
  trim: new THREE.MeshStandardMaterial({ color: 0x2f353a, roughness: 0.5, metalness: 0.4 }),
  metal: new THREE.MeshStandardMaterial({ color: 0x8a949c, roughness: 0.4, metalness: 0.7 }),
  glow: new THREE.MeshStandardMaterial({ color: 0x5fd0ff, emissive: 0x2aa8e0, emissiveIntensity: 1.4 }),
  wood: new THREE.MeshStandardMaterial({ color: 0x6b5643, roughness: 0.6 }),
  crate: new THREE.MeshStandardMaterial({ color: 0xb08a4f, roughness: 0.8 }),
  marking: new THREE.MeshBasicMaterial({ color: 0xf2a541 }),
};

function box(w, h, d, mat, x, y, base, parent = scene) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.copy(toScene(x, y, base + h / 2));
  m.castShadow = true;
  m.receiveShadow = true;
  parent.add(m);
  return m;
}

function outlineBay(s, base) {
  const t = 0.12;
  const { x_m: x, y_m: y, width_m: w, depth_m: d } = s;
  box(w, 0.02, t, mats.marking, x, y + d / 2, base);
  box(w, 0.02, t, mats.marking, x, y - d / 2, base);
  box(t, 0.02, d, mats.marking, x + w / 2, y, base);
  box(t, 0.02, d, mats.marking, x - w / 2, y, base);
}

function buildFacility(structures, base) {
  for (const s of structures) {
    const { x_m: x, y_m: y, width_m: w, depth_m: d, height_m: h } = s;
    if (s.solid) solids.push(s);
    switch (s.kind) {
      case "floor":
        box(w + 1, 0.3, d + 1, mats.trim, x, y, base - 0.3);
        box(w, h, d, mats.floor, x, y, base);
        break;
      case "wall":
        box(w, h, d, mats.wall, x, y, base);
        box(w + 0.05, 0.25, d + 0.05, mats.trim, x, y, base + h);
        break;
      case "door": {
        box(0.3, h, 0.6, mats.trim, x - w / 2, y, base);
        box(0.3, h, 0.6, mats.trim, x + w / 2, y, base);
        box(w + 0.3, 0.4, 0.6, mats.trim, x, y, base + h);
        break;
      }
      case "repair_station": {
        box(w, 0.2, d, mats.metal, x, y, base + 0.15);
        box(w - 0.4, 0.04, d - 0.4, mats.glow, x, y, base + 0.35);
        box(0.25, h, 0.25, mats.trim, x - w / 2 + 0.2, y + d / 2 - 0.2, base);
        box(0.25, h, 0.25, mats.trim, x + w / 2 - 0.2, y + d / 2 - 0.2, base);
        box(w, 0.3, 0.3, mats.trim, x, y + d / 2 - 0.2, base + h);
        spinners.push(box(0.15, 0.15, d * 0.6, mats.metal, x, y + 0.2, base + h - 0.2));
        placeZones.push({ name: s.name, s });
        break;
      }
      case "expansion_bay":
        outlineBay(s, base + 0.16);
        placeZones.push({ name: "Empty repair bay (room to grow)", s });
        break;
      case "storage": {
        for (let level = 0; level < 4; level++) {
          box(w, 0.08, d, mats.metal, x, y, base + 0.15 + level * 0.9);
          for (let k = 0; k < 4; k++) {
            if ((level + k) % 3 === 0) continue;
            box(0.8, 0.6, 0.9, mats.crate, x - 0.6 + (k % 2) * 1.1, y - d / 2 + 1 + k * 2.2, base + 0.23 + level * 0.9);
          }
        }
        for (const dx of [-w / 2, w / 2]) for (const dy of [-d / 2, d / 2]) box(0.1, h, 0.1, mats.trim, x + dx, y + dy, base);
        placeZones.push({ name: "Storage center", s });
        break;
      }
      case "storage_counter":
        box(w, h, d, mats.trim, x, y, base);
        break;
      case "work_station": {
        box(w, 0.1, d, mats.wood, x, y, base + h - 0.1);
        box(w - 0.2, h - 0.1, 0.1, mats.trim, x, y + d / 2 - 0.1, base);
        box(0.1, h - 0.1, d, mats.trim, x - w / 2 + 0.1, y, base);
        box(0.1, h - 0.1, d, mats.trim, x + w / 2 - 0.1, y, base);
        box(0.6, 0.35, 0.5, mats.metal, x - 1.4, y, base + h);
        box(1.2, 0.6, 0.06, mats.glow, x + 0.8, y + d / 2 - 0.2, base + h + 0.3);
        placeZones.push({ name: "Work station", s });
        break;
      }
      case "meeting_table": {
        const r = w / 2;
        const top = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 0.08, 48), mats.wood);
        top.position.copy(toScene(x, y, base + h));
        top.castShadow = top.receiveShadow = true;
        scene.add(top);
        const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.5, h, 16), mats.trim);
        stem.position.copy(toScene(x, y, base + h / 2));
        scene.add(stem);
        const holo = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.02, 32), mats.glow);
        holo.position.copy(toScene(x, y, base + h + 0.06));
        scene.add(holo);
        placeZones.push({ name: "Meeting table", s, radius: r + 2.5 });
        break;
      }
      default:
        box(w, h, d, mats.metal, x, y, base);
    }
  }
  // A light panel over the hall so the inside reads at night too.
  const lamp = new THREE.PointLight(0xfff0d8, 30, 40, 1.6);
  lamp.position.copy(toScene(0, 0, base + 6));
  scene.add(lamp);
}

function blocked(x, y) {
  for (const s of solids) {
    if (Math.abs(x - s.x_m) <= s.width_m / 2 + BODY_RADIUS && Math.abs(y - s.y_m) <= s.depth_m / 2 + BODY_RADIUS) return true;
  }
  return false;
}

function wallAt(x, y) {
  return solids.some(s => s.kind === "wall" && Math.abs(x - s.x_m) <= s.width_m / 2 + 0.25 && Math.abs(y - s.y_m) <= s.depth_m / 2 + 0.25);
}

function placeName(x, y) {
  for (const z of placeZones) {
    const { s } = z;
    if (z.radius ? Math.hypot(x - s.x_m, y - s.y_m) < z.radius
      : Math.abs(x - s.x_m) < s.width_m / 2 + 1.2 && Math.abs(y - s.y_m) < s.depth_m / 2 + 1.2) return z.name;
  }
  if (Math.abs(x) < 16 && Math.abs(y) < 11) return "Inside Seed Station";
  return "Outside, on the planet surface";
}

// --- bodies -------------------------------------------------------------------
function nameTag(text, sub) {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 128;
  const g = c.getContext("2d");
  g.fillStyle = "rgba(14,20,26,0.75)";
  g.beginPath(); g.roundRect(8, 8, 496, 112, 24); g.fill();
  g.fillStyle = "#e9eef2"; g.font = "600 48px system-ui, sans-serif"; g.textAlign = "center";
  g.fillText(text, 256, 62);
  g.fillStyle = "#f2a541"; g.font = "28px system-ui, sans-serif";
  g.fillText(sub, 256, 100);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: true, transparent: true }));
  sprite.scale.set(1.6, 0.4, 1);
  sprite.renderOrder = 10;
  return sprite;
}

function blockoutBody(height, color) {
  const g = new THREE.Group();
  const shell = new THREE.MeshStandardMaterial({ color, roughness: 0.45, metalness: 0.5 });
  const dark = mats.trim;
  const legH = height * 0.45, torsoH = height * 0.33, headH = height * 0.14;
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(height * 0.05, legH - height * 0.1, 4, 8), dark);
    leg.position.set(side * height * 0.07, legH / 2, 0);
    g.add(leg);
    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(height * 0.035, torsoH * 0.9, 4, 8), dark);
    arm.position.set(side * height * 0.17, legH + torsoH * 0.45, 0);
    g.add(arm);
  }
  const torso = new THREE.Mesh(new THREE.BoxGeometry(height * 0.26, torsoH, height * 0.16), shell);
  torso.position.y = legH + torsoH / 2;
  g.add(torso);
  const head = new THREE.Mesh(new THREE.BoxGeometry(height * 0.15, headH, height * 0.14), shell);
  head.position.y = legH + torsoH + headH / 2 + height * 0.03;
  g.add(head);
  const visor = new THREE.Mesh(new THREE.BoxGeometry(height * 0.12, headH * 0.3, 0.02), mats.glow);
  visor.position.set(0, head.position.y + headH * 0.05, -height * 0.071);
  g.add(visor);
  g.traverse(n => { if (n.isMesh) n.castShadow = true; });
  return g;
}

const loader = new GLTFLoader();
const citizens = new Map(); // id -> {group, data, mixer}

function addCitizen(c, base) {
  const group = new THREE.Group();
  const fallback = blockoutBody(c.height_m, CITIZEN_COLORS[c.id] || 0x999999);
  group.add(fallback);
  const tag = nameTag(c.name, c.division);
  tag.position.y = c.height_m + 0.45;
  group.add(tag);
  scene.add(group);
  const record = { group, data: c, mixer: null };
  citizens.set(c.id, record);
  placeCitizen(record, c);

  const model = CITIZEN_MODELS[c.id];
  if (!model) return;
  loader.load(model.src, gltf => {
    const root = gltf.scene;
    root.updateMatrixWorld(true);
    const bb = new THREE.Box3();
    root.traverse(n => {
      if (!n.isMesh) return;
      n.castShadow = true;
      n.frustumCulled = false;
      n.geometry.computeBoundingBox();
      bb.union(n.geometry.boundingBox.clone().applyMatrix4(n.matrixWorld));
    });
    const modelHeight = bb.max.y - bb.min.y;
    // Models are authored in meters; only correct a clear mismatch.
    const scale = modelHeight > 0 && Math.abs(modelHeight - c.height_m) / c.height_m > 0.15 ? c.height_m / modelHeight : 1;
    root.scale.setScalar(scale);
    root.position.set(-(bb.min.x + bb.max.x) / 2 * scale, -bb.min.y * scale, -(bb.min.z + bb.max.z) / 2 * scale);
    // glTF models face +z; turn them to face -z (our "forward").
    const holder = new THREE.Group();
    holder.rotation.y = Math.PI;
    holder.add(root);
    group.remove(fallback);
    group.add(holder);
    record.mixer = new THREE.AnimationMixer(root);
    const idle = THREE.AnimationClip.findByName(gltf.animations, model.idle);
    if (idle) record.mixer.clipAction(idle).play();
  }, undefined, err => console.warn(`Model for ${c.id} failed; keeping blockout body`, err));
}

function placeCitizen(record, c) {
  record.data = c;
  record.group.position.copy(toScene(c.x_m, c.y_m, heightAt(c.x_m, c.y_m) + 0.15));
  // heading is the planet-space angle from +x (east) toward +y (north).
  record.group.rotation.y = c.heading - Math.PI / 2;
}

// The visitor: a slim survey suit so you can tell yourself apart.
const visitor = { x: 0, y: -20, heading: Math.PI / 2, group: new THREE.Group(), lastSent: 0, pending: false };
{
  const suit = new THREE.MeshStandardMaterial({ color: 0xf2f2ee, roughness: 0.6 });
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.28, 1.1, 6, 12), suit);
  body.position.y = 0.83;
  const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 16), suit);
  helmet.position.y = 1.62;
  const visorMesh = new THREE.Mesh(new THREE.SphereGeometry(0.17, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2.4),
    new THREE.MeshStandardMaterial({ color: 0x1a2630, metalness: 0.9, roughness: 0.15 }));
  visorMesh.rotation.x = -Math.PI / 2;
  visorMesh.position.set(0, 1.63, -0.09);
  const pack = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.5, 0.18), mats.trim);
  pack.position.set(0, 1.05, 0.3);
  for (const m of [body, helmet, visorMesh, pack]) { m.castShadow = true; visitor.group.add(m); }
  scene.add(visitor.group);
}

// --- input ---------------------------------------------------------------------
const keys = new Set();
window.addEventListener("keydown", e => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) e.preventDefault();
  keys.add(e.key);
});
window.addEventListener("keyup", e => keys.delete(e.key));
window.addEventListener("blur", () => keys.clear());

function stepVisitor(dt) {
  const turn = (keys.has("ArrowLeft") ? 1 : 0) - (keys.has("ArrowRight") ? 1 : 0);
  visitor.heading += turn * TURN_SPEED * dt;
  const forward = (keys.has("ArrowUp") ? 1 : 0) - (keys.has("ArrowDown") ? 1 : 0);
  if (!forward) return false;
  const speed = (keys.has("Shift") ? JOG_SPEED : WALK_SPEED) * (forward < 0 ? 0.6 : 1);
  const dx = Math.cos(visitor.heading) * speed * dt * forward;
  const dy = Math.sin(visitor.heading) * speed * dt * forward;
  // Slide along walls instead of stopping dead.
  if (!blocked(visitor.x + dx, visitor.y + dy)) { visitor.x += dx; visitor.y += dy; }
  else if (!blocked(visitor.x + dx, visitor.y)) visitor.x += dx;
  else if (!blocked(visitor.x, visitor.y + dy)) visitor.y += dy;
  const half = (terrain?.size || 2048) / 2 - 2;
  visitor.x = Math.max(-half, Math.min(half, visitor.x));
  visitor.y = Math.max(-half, Math.min(half, visitor.y));
  return true;
}

async function sendPosition() {
  if (visitor.pending) return;
  visitor.pending = true;
  try {
    const r = await fetch("/api/visitor/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ visitor: VISITOR, x_m: visitor.x, y_m: visitor.y, heading: visitor.heading }),
    });
    const res = await r.json();
    if (!res.accepted) { visitor.x = res.x_m; visitor.y = res.y_m; } // the world said no
  } catch (e) { /* offline for a moment; try again next send */ }
  visitor.pending = false;
}

// --- HUD ------------------------------------------------------------------------
const $ = id => document.getElementById(id);
let paused = false;
$("pause-button").addEventListener("click", async () => {
  paused = !paused;
  await fetch("/api/pause", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ paused }) });
  refreshState();
});

function updateNearby() {
  let best = null, bestD = NEARBY_RADIUS;
  for (const rec of citizens.values()) {
    const d = Math.hypot(rec.data.x_m - visitor.x, rec.data.y_m - visitor.y);
    if (d < bestD) { best = rec.data; bestD = d; }
  }
  const panel = $("nearby");
  if (!best) { panel.hidden = true; return; }
  panel.hidden = false;
  $("nearby-token").src = `/static/assets/citizens/${best.id}/token.webp`;
  $("nearby-name").textContent = `${best.name} · Director`;
  $("nearby-division").textContent = best.division;
  $("nearby-activity").textContent = best.activity;
}

function applyLighting(time) {
  const hours = time.hour + time.minute / 60;
  const angle = ((hours - 6) / 12) * Math.PI; // sunrise 06:00, sunset 18:00
  const elevation = Math.sin(angle);
  const day = Math.max(0, Math.min(1, elevation * 2 + 0.2));
  const dir = new THREE.Vector3(Math.cos(angle) * 0.8, Math.max(0.15, elevation), 0.45).normalize();
  sun.intensity = 0.25 + 2.2 * day;
  hemi.intensity = 0.25 + 0.75 * day;
  const sky = new THREE.Color(0x0d1622).lerp(new THREE.Color(0xa9c4d6), day);
  scene.background = sky;
  scene.fog.color.copy(sky);
  sun.userData.dir = dir;
}

async function refreshState() {
  const state = await (await fetch(`/api/state?visitor=${VISITOR}`)).json();
  $("seed-label").textContent = `Planet seed ${state.world.seed} · v${state.version}`;
  $("time-label").textContent = state.time.label + (state.time.paused ? " · paused" : ` · ${state.time.time_scale}x`);
  paused = state.time.paused;
  $("pause-button").textContent = paused ? "Resume" : "Pause";
  applyLighting(state.time);
  for (const c of state.citizens) {
    const rec = citizens.get(c.id);
    if (rec) placeCitizen(rec, c);
  }
  return state;
}

// --- start ----------------------------------------------------------------------
async function start() {
  const [terrainData, state] = await Promise.all([
    fetch("/api/world/terrain").then(r => r.json()),
    fetch(`/api/state?visitor=${VISITOR}`).then(r => r.json()),
  ]);
  buildTerrain(terrainData);
  const base = terrain.origin + 0.0;
  buildFacility(state.structures, base);
  for (const c of state.citizens) addCitizen(c, base);
  visitor.x = state.visitor.x_m; visitor.y = state.visitor.y_m; visitor.heading = state.visitor.heading;
  await refreshState();
  setInterval(refreshState, 2000);
  $("loading").classList.add("done");
  requestAnimationFrame(loop);
}

const clock = new THREE.Clock();
const camPos = new THREE.Vector3();
let firstFrame = true;

function loop() {
  const dt = Math.min(clock.getDelta(), 0.1);
  const moved = stepVisitor(dt);
  const now = performance.now();
  if ((moved || keys.size) && now - visitor.lastSent > MOVE_SEND_MS) {
    visitor.lastSent = now;
    sendPosition();
  }
  const ground = heightAt(visitor.x, visitor.y);
  const floorLift = Math.abs(visitor.x) < 16 && Math.abs(visitor.y) < 11 ? 0.15 : 0;
  visitor.group.position.copy(toScene(visitor.x, visitor.y, ground + floorLift));
  visitor.group.rotation.y = visitor.heading - Math.PI / 2;

  // Third-person camera behind and above the visitor.
  const back = 7.5, up = 4.6;
  const target = toScene(visitor.x + Math.cos(visitor.heading) * 3, visitor.y + Math.sin(visitor.heading) * 3, ground + 1.2);
  // Pull the camera in if a wall would come between it and the visitor.
  // Inside, the outer walls also bound the camera so it never ends up outside.
  const inside = Math.abs(visitor.x) < 15.8 && Math.abs(visitor.y) < 10.8;
  let dist = back;
  for (let d = 0.6; d <= back; d += 0.3) {
    const px = visitor.x - Math.cos(visitor.heading) * d, py = visitor.y - Math.sin(visitor.heading) * d;
    if (inside && (Math.abs(px) > 15.4 || Math.abs(py) > 10.4)) { dist = Math.max(0.8, d - 0.3); break; }
    if (wallAt(visitor.x - Math.cos(visitor.heading) * d, visitor.y - Math.sin(visitor.heading) * d)) { dist = Math.max(0.8, d - 0.6); break; }
  }
  const camX = visitor.x - Math.cos(visitor.heading) * dist;
  const camY = visitor.y - Math.sin(visitor.heading) * dist;
  const want = toScene(camX, camY, Math.max(ground + up, heightAt(camX, camY) + 1.2));
  if (firstFrame) { camPos.copy(want); firstFrame = false; } else camPos.lerp(want, 1 - Math.pow(0.001, dt));
  camera.position.copy(camPos);
  camera.lookAt(target);

  // Keep the sun's shadow box around the visitor.
  const dir = sun.userData.dir || new THREE.Vector3(0.4, 1, 0.3).normalize();
  sun.target.position.copy(target);
  sun.position.copy(target).addScaledVector(dir, 120);

  for (const rec of citizens.values()) rec.mixer?.update(dt);
  for (const m of spinners) m.rotation.y += dt * 0.6;
  updateNearby();
  $("place-label").textContent = placeName(visitor.x, visitor.y);
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
}

start().catch(err => {
  console.error(err);
  $("loading").textContent = "Agent City could not load the world. Is the server running?";
});
