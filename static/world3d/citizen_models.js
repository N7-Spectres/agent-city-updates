// v1.1.9 — rigged citizen world models.
//
// Presentation only. planet_lab.js stays the owner of the camera, the
// authoritative Simulation positions, and the DOM markers (labels, clicks,
// selection). Each frame it hands this module a snapshot; this module draws
// any citizen whose CITIZEN_WORLD_VISUALS entry declares a `model`, on a
// transparent canvas stacked above the terrain canvas.
//
// If three.js, WebGL, or a single model fails, that citizen simply reports
// "failed" and planet_lab.js keeps showing its sprite body.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const canvas = document.getElementById("citizen-model-canvas");
const CROSSFADE_SECONDS = 0.25;

let renderer = null;
try {
  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
} catch (error) {
  console.warn("Citizen models unavailable; sprite bodies stay in place", error);
}

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(56.25, 1, 0.02, 100);
const hemi = new THREE.HemisphereLight(0xdfeff6, 0x2a2118, 0.9);
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
scene.add(hemi, sun, sun.target);

const loader = new GLTFLoader();
const clock = new THREE.Clock();
const bodies = new Map(); // citizen id -> body record

function loadBody(id, model) {
  const body = {
    id,
    src: model.src,
    status: "loading",
    root: null,
    height: 1,
    mixer: null,
    actions: {},
    current: null,
  };
  bodies.set(id, body);

  loader.load(
    model.src,
    gltf => {
      const root = gltf.scene;
      root.traverse(node => {
        if (node.isMesh) node.frustumCulled = false; // skinned bounds lag animation
      });

      // Measure the bind pose so any model is foot-anchored and sized by height.
      // (Box3.setFromObject would skin the vertices with bones that have not
      // been posed yet, which collapses the box.)
      root.updateMatrixWorld(true);
      const box = new THREE.Box3();
      root.traverse(node => {
        if (!node.isMesh) return;
        node.geometry.computeBoundingBox();
        box.union(node.geometry.boundingBox.clone().applyMatrix4(node.matrixWorld));
      });
      body.height = Math.max(0.01, box.max.y - box.min.y);
      root.position.y = -box.min.y;

      const holder = new THREE.Group();
      holder.add(root);
      holder.visible = false;
      scene.add(holder);
      body.root = holder;

      body.mixer = new THREE.AnimationMixer(root);
      const clips = model.clips || {};
      for (const [role, clipName] of Object.entries(clips)) {
        const clip = THREE.AnimationClip.findByName(gltf.animations, clipName);
        if (clip) body.actions[role] = body.mixer.clipAction(clip);
      }
      body.status = "ready";
    },
    undefined,
    error => {
      body.status = "failed";
      console.warn("Citizen model failed to load; keeping sprite for " + id, error);
    },
  );
  return body;
}

function playRole(body, role) {
  const next = body.actions[role] || body.actions.idle || null;
  if (!next || next === body.current) return;
  next.reset().play();
  if (body.current) body.current.crossFadeTo(next, CROSSFADE_SECONDS, false);
  body.current = next;
}

function syncLighting(lighting) {
  if (!lighting) return;
  const [r, g, b] = lighting.sunColor || [1, 1, 1];
  sun.color.setRGB(r, g, b);
  sun.intensity = 0.5 + Number(lighting.direct || 0) * 1.1;
  hemi.intensity = 0.35 + Number(lighting.ambient || 0) * 1.6;
  const dir = lighting.localDirection || [0.3, 1, 0.2];
  sun.position.set(dir[0] * 10, Math.max(0.15, dir[1]) * 10, dir[2] * 10);
}

window.AgentCityModels = Object.freeze({
  // "loading" | "ready" | "failed"
  status(id, model) {
    if (!renderer || !model || !model.src) return "failed";
    const body = bodies.get(String(id));
    if (!body || body.src !== model.src) return loadBody(String(id), model).status;
    return body.status;
  },

  // frame: { active, eye, target, fovY, near, far, width, height, pixelRatio,
  //          lighting, citizens: [{ id, world, heading, walking, pixelHeight }] }
  render(frame) {
    if (!renderer) return;
    const delta = Math.min(clock.getDelta(), 0.1);

    if (!frame || !frame.active) {
      if (canvas.style.visibility !== "hidden") {
        renderer.clear();
        canvas.style.visibility = "hidden";
      }
      return;
    }
    canvas.style.visibility = "visible";

    renderer.setPixelRatio(frame.pixelRatio || 1);
    renderer.setSize(frame.width, frame.height, false);

    camera.fov = THREE.MathUtils.radToDeg(frame.fovY);
    camera.aspect = Math.max(0.1, frame.width / Math.max(1, frame.height));
    camera.near = frame.near;
    camera.far = frame.far;
    camera.position.set(frame.eye[0], frame.eye[1], frame.eye[2]);
    camera.up.set(0, 1, 0);
    camera.lookAt(frame.target[0], frame.target[1], frame.target[2]);
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();
    syncLighting(frame.lighting);

    const seen = new Set();
    for (const citizen of frame.citizens || []) {
      const body = bodies.get(String(citizen.id));
      if (!body || body.status !== "ready") continue;
      seen.add(body.id);

      const holder = body.root;
      holder.visible = true;
      holder.position.set(citizen.world[0], citizen.world[1], citizen.world[2]);
      holder.rotation.y = Number(citizen.heading || 0);

      // Size the body in world units so it covers the same screen height the
      // sprite would have, which keeps it readable at every zoom level.
      const distance = Math.max(0.05, camera.position.distanceTo(holder.position));
      const worldHeight = (citizen.pixelHeight * 2 * distance * Math.tan(frame.fovY / 2)) / frame.height;
      holder.scale.setScalar(worldHeight / body.height);

      playRole(body, citizen.walking ? "walk" : "idle");
      body.mixer.update(delta);
    }

    for (const body of bodies.values()) {
      if (body.root && !seen.has(body.id)) body.root.visible = false;
    }

    renderer.render(scene, camera);
  },
});
