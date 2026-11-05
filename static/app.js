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
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
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
// Seed Station: one smooth white shell with soft light lines, after N7's
// references. The server sends the wall outline; the shell is drawn from it.
const solids = []; // boxes the visitor cannot walk through
const placeZones = [];
const spinners = []; // small moving parts so the station feels alive

const GLOW = 0x4cc6ff;
const mats = {
  shell: new THREE.MeshStandardMaterial({ color: 0xf3f5f7, roughness: 0.42, metalness: 0.05, side: THREE.DoubleSide }),
  floor: new THREE.MeshStandardMaterial({ color: 0xd9dee3, roughness: 0.28, metalness: 0.08 }),
  plinth: new THREE.MeshStandardMaterial({ color: 0xc9d0d6, roughness: 0.6 }),
  white: new THREE.MeshStandardMaterial({ color: 0xf7f8fa, roughness: 0.35, metalness: 0.05 }),
  soft: new THREE.MeshStandardMaterial({ color: 0xdfe4e8, roughness: 0.5 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x1d2730, roughness: 0.3, metalness: 0.4 }),
  glow: new THREE.MeshStandardMaterial({ color: 0x9fe2ff, emissive: GLOW, emissiveIntensity: 1.5, toneMapped: false }),
  trim: new THREE.MeshStandardMaterial({ color: 0x2f353a, roughness: 0.5, metalness: 0.4 }),
  glowSoft: new THREE.MeshBasicMaterial({ color: 0x8fdcff, transparent: true, opacity: 0.55, toneMapped: false }),
  screen: new THREE.MeshStandardMaterial({ color: 0x0c2433, emissive: 0x1a6f9e, emissiveIntensity: 0.9, roughness: 0.2 }),
  leaf: new THREE.MeshStandardMaterial({ color: 0x4e8a46, roughness: 0.8, flatShading: true }),
  leafLight: new THREE.MeshStandardMaterial({ color: 0x74ad5c, roughness: 0.8, flatShading: true }),
};

function add(mesh, shadows = true) {
  mesh.castShadow = shadows;
  mesh.receiveShadow = true;
  scene.add(mesh);
  return mesh;
}

// A rounded rectangle in planet space (x east, y north) as a three.js Shape.
function roundedRectShape(w, d, r) {
  const s = new THREE.Shape();
  const hw = w / 2, hd = d / 2;
  r = Math.min(r, hw, hd);
  s.moveTo(-hw + r, -hd);
  s.lineTo(hw - r, -hd); s.absarc(hw - r, -hd + r, r, -Math.PI / 2, 0, false);
  s.lineTo(hw, hd - r); s.absarc(hw - r, hd - r, r, 0, Math.PI / 2, false);
  s.lineTo(-hw + r, hd); s.absarc(-hw + r, hd - r, r, Math.PI / 2, Math.PI, false);
  s.lineTo(-hw, -hd + r); s.absarc(-hw + r, -hd + r, r, Math.PI, Math.PI * 1.5, false);
  return s;
}

// A soft-edged block: rounded corners seen from above, bevelled edges.
function roundedBlock(w, h, d, r, mat, x, y, base) {
  const bevel = Math.min(0.08, h / 4);
  const geo = new THREE.ExtrudeGeometry(roundedRectShape(w - bevel * 2, d - bevel * 2, r), {
    depth: h - bevel * 2, bevelEnabled: true, bevelSize: bevel, bevelThickness: bevel, bevelSegments: 3, curveSegments: 16,
  });
  geo.rotateX(-Math.PI / 2); // shape x/y -> scene x/-z, extrusion -> up
  const m = new THREE.Mesh(geo, mat);
  m.position.copy(toScene(x, y, base + bevel));
  return add(m);
}

// A glowing line along points given in planet space at a height.
function lightLine(points2d, height, radius = 0.035, mat = mats.glow, closed = false) {
  const curve = new THREE.CatmullRomCurve3(points2d.map(([x, y]) => toScene(x, y, height)), closed, "centripetal");
  const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(16, points2d.length * 4), radius, 6, closed), mat);
  scene.add(tube);
  return tube;
}

function offsetPath(points, dist) {
  // Outward normal of a counter-clockwise outline is (dy, -dx).
  return points.map((p, i) => {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(points.length - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
    return [p[0] + (dy / len) * dist, p[1] - (dx / len) * dist];
  });
}

// The curved wall: a ribbon with inner face, outer face and a rounded top.
function buildShell(shell, base) {
  const pts = shell.path;
  const t = shell.wall_thickness_m, h = shell.wall_height_m;
  const outer = offsetPath(pts, t / 2), inner = offsetPath(pts, -t / 2);
  const pos = [], idx = [];
  const ring = [[outer, 0], [outer, h], [inner, h], [inner, 0]];
  for (let i = 0; i < pts.length; i++) {
    for (const [line, z] of ring) pos.push(line[i][0], base + z, -line[i][1]);
  }
  for (let i = 0; i < pts.length - 1; i++) {
    for (let k = 0; k < 3; k++) {
      const a = i * 4 + k, b = a + 1, c = (i + 1) * 4 + k, d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  // Close the two wall ends at the doorway.
  for (const i of [0, pts.length - 1]) idx.push(i * 4, i * 4 + 1, i * 4 + 2, i * 4, i * 4 + 2, i * 4 + 3);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  add(new THREE.Mesh(geo, mats.shell));

  // Ceiling cove: a white band reaching in from the top of the wall, open in
  // the middle like a skylight, with two light lines along its edge.
  const coveDepth = 3.2;
  const coveOuter = offsetPath(pts, -t / 2), coveInner = offsetPath(pts, -t / 2 - coveDepth);
  const cpos = [], cidx = [];
  for (let i = 0; i < pts.length; i++) {
    cpos.push(coveOuter[i][0], base + h - 0.05, -coveOuter[i][1]);
    cpos.push(coveInner[i][0], base + h - 0.45, -coveInner[i][1]);
  }
  for (let i = 0; i < pts.length - 1; i++) {
    const a = i * 2, b = a + 1, c = a + 2, d = a + 3;
    cidx.push(a, c, b, b, c, d);
  }
  const cgeo = new THREE.BufferGeometry();
  cgeo.setAttribute("position", new THREE.Float32BufferAttribute(cpos, 3));
  cgeo.setIndex(cidx);
  cgeo.computeVertexNormals();
  add(new THREE.Mesh(cgeo, mats.shell), false);
  lightLine(offsetPath(pts, -t / 2 - coveDepth + 0.05), base + h - 0.5, 0.045);
  lightLine(offsetPath(pts, -t / 2 - coveDepth * 0.45), base + h - 0.3, 0.03);
  // A low cove light where the wall meets the floor, inside and out.
  lightLine(offsetPath(pts, -t / 2 - 0.06), base + 0.22, 0.03);
  lightLine(offsetPath(pts, t / 2 + 0.06), base + 0.12, 0.04);
  // A soft rounded lip along the top of the wall.
  const lip = new THREE.CatmullRomCurve3(pts.map(([x, y]) => toScene(x, y, base + h)), false, "centripetal");
  add(new THREE.Mesh(new THREE.TubeGeometry(lip, pts.length * 3, t * 0.6, 10, false), mats.shell), false);

  // The doorway: a rounded portal with a light along its inner edge.
  const hd = shell.door_width_m / 2, y = -shell.depth_m / 2, top = 3.6;
  const arch = [];
  for (let i = 0; i <= 24; i++) {
    const a = Math.PI * (i / 24);
    arch.push(toScene(Math.cos(a) * hd, y, base + (top - hd) + Math.sin(a) * hd));
  }
  arch.unshift(toScene(hd, y, base)); arch.push(toScene(-hd, y, base));
  const archCurve = new THREE.CatmullRomCurve3(arch, false, "centripetal");
  add(new THREE.Mesh(new THREE.TubeGeometry(archCurve, 64, 0.32, 12, false), mats.white));
  scene.add(new THREE.Mesh(new THREE.TubeGeometry(archCurve, 64, 0.05, 8, false), mats.glow));

  // Name over the door.
  const c = document.createElement("canvas");
  c.width = 1024; c.height = 160;
  const g = c.getContext("2d");
  g.fillStyle = "#8fdcff"; g.font = "600 92px system-ui, sans-serif"; g.textAlign = "center";
  g.fillText("SEED  STATION", 512, 112);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(6, 0.95), new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false }));
  sign.position.copy(toScene(0, y - t / 2 - 0.02, base + 4.35));
  // A plane faces +z (south) by default: toward arriving visitors.
  scene.add(sign);
}

function buildFloor(shell, base) {
  const plinth = new THREE.Mesh(new THREE.ExtrudeGeometry(roundedRectShape(shell.width_m + 3, shell.depth_m + 3, shell.corner_radius_m + 1.5), { depth: 0.4, bevelEnabled: true, bevelSize: 0.15, bevelThickness: 0.15, bevelSegments: 3, curveSegments: 24 }), mats.plinth);
  plinth.geometry.rotateX(-Math.PI / 2);
  plinth.position.copy(toScene(0, 0, base - 0.45));
  add(plinth, false);
  const floor = new THREE.Mesh(new THREE.ShapeGeometry(roundedRectShape(shell.width_m, shell.depth_m, shell.corner_radius_m), 24), mats.floor);
  floor.geometry.rotateX(-Math.PI / 2);
  floor.position.copy(toScene(0, 0, base + 0.15));
  floor.receiveShadow = true;
  scene.add(floor);

  // Light lines set into the floor, flowing from the door to each area.
  const f = base + 0.165;
  const flat = (pts, r = 0.022) => { const m = lightLine(pts, f, r); m.scale.y = 0.25; m.position.y = f * 0.75; return m; };
  flat([[0.6, -13.5], [0.8, -9], [2.6, -5], [3.4, -1.8], [2.2, 0.4]]);
  flat([[-0.6, -13.5], [-1.2, -8.5], [-5, -5.2], [-10, -4.6], [-12.4, -4.6]]);
  flat([[1.6, -9.5], [6, -8.4], [9.2, -6.2], [10.2, -5.6]]);
  flat([[3.6, -1.6], [7.5, -0.2], [10.2, 0.8], [11.6, 1.2]]);
  flat([[-12.4, -4.6], [-12.6, 0], [-12.6, 4.5], [-12.4, 8.6]]);
}

function planter(x, y, base, size = 1) {
  const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.45 * size, 0.36 * size, 0.85 * size, 24), mats.white);
  pot.position.copy(toScene(x, y, base + 0.15 + 0.425 * size));
  add(pot);
  const leafGeo = new THREE.IcosahedronGeometry(0.32 * size, 0);
  for (let k = 0; k < 9; k++) {
    const leaf = new THREE.Mesh(leafGeo, k % 3 ? mats.leaf : mats.leafLight);
    const a = k * 2.39, r = 0.18 * size * (k % 4);
    leaf.position.copy(toScene(x + Math.cos(a) * r, y + Math.sin(a) * r, base + (1.0 + 0.16 * (k % 5)) * size));
    leaf.scale.set(1, 0.8 + (k % 3) * 0.3, 1);
    leaf.rotation.set(k, k * 1.7, 0);
    add(leaf);
  }
}

function buildFacility(structures, shell, base) {
  if (shell) { buildFloor(shell, base); buildShell(shell, base); }
  const b = base + 0.15; // standing height on the station floor
  for (const s of structures) {
    const { x_m: x, y_m: y, width_m: w, depth_m: d, height_m: h } = s;
    if (s.solid) solids.push(s);
    switch (s.kind) {
      case "floor": case "wall": case "door":
        break; // drawn by buildShell / buildFloor
      case "repair_station": {
        const pad = new THREE.Mesh(new THREE.CylinderGeometry(1.35, 1.45, 0.22, 40), mats.white);
        pad.position.copy(toScene(x, y, b + 0.11)); add(pad);
        const disc = new THREE.Mesh(new THREE.CircleGeometry(1.05, 40), mats.glowSoft);
        disc.rotation.x = -Math.PI / 2; disc.position.copy(toScene(x, y, b + 0.23)); scene.add(disc);
        const rim = new THREE.Mesh(new THREE.TorusGeometry(1.2, 0.03, 8, 64), mats.glow);
        rim.rotation.x = Math.PI / 2; rim.position.copy(toScene(x, y, b + 0.24)); scene.add(rim);
        // A white arch over the pad, open toward the hall (east).
        const arch = new THREE.Mesh(new THREE.TorusGeometry(1.35, 0.16, 16, 48, Math.PI), mats.white);
        arch.position.copy(toScene(x - 0.9, y, b + 0.2)); arch.scale.set(1, 1.75, 1); arch.rotation.y = Math.PI / 2;
        add(arch);
        const archGlow = new THREE.Mesh(new THREE.TorusGeometry(1.18, 0.025, 8, 48, Math.PI), mats.glow);
        archGlow.position.copy(arch.position); archGlow.scale.copy(arch.scale); archGlow.rotation.copy(arch.rotation);
        scene.add(archGlow);
        const halo = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.035, 8, 48), mats.glow);
        halo.rotation.x = Math.PI / 2; halo.position.copy(toScene(x, y, b + h)); scene.add(halo);
        spinners.push(halo);
        placeZones.push({ name: s.name, s });
        break;
      }
      case "expansion_bay": {
        const ring = new THREE.Mesh(new THREE.RingGeometry(1.15, 1.22, 48), mats.glowSoft);
        ring.rotation.x = -Math.PI / 2; ring.position.copy(toScene(x, y, b + 0.02)); scene.add(ring);
        placeZones.push({ name: "Empty repair bay (room to grow)", s });
        break;
      }
      case "storage": {
        roundedBlock(w, h, d, 0.6, mats.white, x, y, b);
        for (let row = 0; row < 3; row++) {
          for (let col = 0; col < 3; col++) {
            const cy = y - d / 2 + 1.5 + col * 3;
            const bay = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.8, 2.4), mats.soft);
            bay.position.copy(toScene(x - w / 2 - 0.01, cy, b + 0.7 + row * 1.0)); scene.add(bay);
          }
          const strip = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.03, d - 0.8), mats.glow);
          strip.position.copy(toScene(x - w / 2 - 0.03, y, b + 0.25 + row * 1.0)); scene.add(strip);
        }
        placeZones.push({ name: "Storage center", s });
        break;
      }
      case "storage_counter":
        roundedBlock(w, h, d, 0.45, mats.white, x, y, b);
        lightLine([[x - w / 2 - 0.02, y - d / 2 + 0.3], [x - w / 2 - 0.02, y + d / 2 - 0.3]], b + 0.12, 0.025);
        break;
      case "work_station": {
        roundedBlock(w, 0.12, d, 0.5, mats.white, x, y, b + h - 0.12);
        roundedBlock(w * 0.55, h - 0.12, d * 0.6, 0.35, mats.soft, x, y + 0.1, b);
        lightLine([[x - w / 2 + 0.3, y - d / 2 + 0.05], [x + w / 2 - 0.3, y - d / 2 + 0.05]], b + h - 0.14, 0.025);
        const screen = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 0.75, 32, 1, true, -0.45, 0.9), mats.screen);
        screen.material.side = THREE.DoubleSide;
        screen.position.copy(toScene(x, y - 1.4, b + h + 0.55)); scene.add(screen);
        placeZones.push({ name: "Work station", s });
        break;
      }
      case "meeting_table": {
        const r = w / 2;
        const top = new THREE.Mesh(new THREE.CylinderGeometry(r, r * 0.96, 0.12, 64), mats.white);
        top.position.copy(toScene(x, y, b + h)); add(top);
        const edge = new THREE.Mesh(new THREE.TorusGeometry(r * 0.97, 0.025, 8, 96), mats.glow);
        edge.rotation.x = Math.PI / 2; edge.position.copy(toScene(x, y, b + h - 0.07)); scene.add(edge);
        const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.9, h - 0.06, 32), mats.white);
        stem.position.copy(toScene(x, y, b + (h - 0.06) / 2)); add(stem);
        const holo = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 0.02, 48), mats.glowSoft);
        holo.position.copy(toScene(x, y, b + h + 0.08)); scene.add(holo);
        const standRing = new THREE.Mesh(new THREE.RingGeometry(2.95, 3.0, 96), mats.glowSoft);
        standRing.rotation.x = -Math.PI / 2; standRing.position.copy(toScene(x, y, b + 0.02)); scene.add(standRing);
        placeZones.push({ name: "Meeting table", s, radius: r + 2.5 });
        break;
      }
      default:
        roundedBlock(w, h, d, 0.3, mats.white, x, y, b);
    }
  }
  for (const [px, py, size] of [[-3.4, -10.6, 1], [3.4, -10.6, 1], [-6, 10.4, 1.3], [6, 10.4, 1.3], [16, -9.2, 1.1], [-16.2, 9.6, 0.9]]) planter(px, py, base, size);

  // Cool white light inside, so the white reads at night too.
  for (const [lx, ly] of [[-9, 0], [0, 3], [9, 0]]) {
    const lamp = new THREE.PointLight(0xeaf6ff, 9, 24, 1.6);
    lamp.position.copy(toScene(lx, ly, base + 4.4));
    scene.add(lamp);
  }
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
  if (Math.abs(x) < 18 && Math.abs(y) < 12) return "Inside Seed Station";
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
  buildFacility(state.structures, state.world.shell, base);
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
  const floorLift = Math.abs(visitor.x) < 18.5 && Math.abs(visitor.y) < 12.5 ? 0.15 : 0;
  visitor.group.position.copy(toScene(visitor.x, visitor.y, ground + floorLift));
  visitor.group.rotation.y = visitor.heading - Math.PI / 2;

  // Third-person camera behind and above the visitor.
  const back = 7.5, up = 4.6;
  const target = toScene(visitor.x + Math.cos(visitor.heading) * 3, visitor.y + Math.sin(visitor.heading) * 3, ground + 1.2);
  // Pull the camera in if a wall would come between it and the visitor.
  // Inside, the outer walls also bound the camera so it never ends up outside.
  const inside = Math.abs(visitor.x) < 17.8 && Math.abs(visitor.y) < 11.8;
  let dist = back;
  for (let d = 0.6; d <= back; d += 0.3) {
    const px = visitor.x - Math.cos(visitor.heading) * d, py = visitor.y - Math.sin(visitor.heading) * d;
    if (inside && (Math.abs(px) > 17.2 || Math.abs(py) > 11.2)) { dist = Math.max(0.8, d - 0.3); break; }
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
