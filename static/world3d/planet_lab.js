(() => {
  "use strict";

  const canvas = document.getElementById("world-canvas");
  const markerLayer = document.getElementById("marker-layer");
  const locationList = document.getElementById("location-list");
  const selectionTitle = document.getElementById("selection-title");
  const selectionBody = document.getElementById("selection-body");
  const simTime = document.getElementById("sim-time");
  const connectionPill = document.getElementById("connection-pill");
  const modeCaption = document.getElementById("mode-caption");
  const resetCameraButton = document.getElementById("reset-camera");
  const modeButtons = [...document.querySelectorAll(".mode-button")];

  // Pre-Blender Local citizen bodies. These are presentation-only art layered
  // over authoritative Simulation positions. Optional equipment remains separate.
  // Relative scale is visual canon/readability, not physical Simulation truth.
  const CITIZEN_WORLD_VISUALS = Object.freeze({
    aris: Object.freeze({
      kind: "sprite_body",
      baseBody: "/static/assets/citizens/aris/world/front.png",
      futureModelSlot: "/static/assets/citizens/aris/world/model.glb",
      presentationScale: 0.881,
      minReadableScale: 0.52,
    }),
    cato: Object.freeze({
      kind: "sprite_body",
      baseBody: "/static/assets/citizens/cato/world/front.webp",
      futureModelSlot: "/static/assets/citizens/cato/world/model.glb",
      presentationScale: 1.0,
      minReadableScale: 0.58,
    }),
    iri: Object.freeze({
      kind: "sprite_body",
      baseBody: "/static/assets/citizens/iri/full.webp",
      futureModelSlot: "/static/assets/citizens/iri/world/model.glb",
      presentationScale: 0.848,
      minReadableScale: 0.50,
      removeConnectedBackdrop: true,
      backdropTolerance: 72,
      backdropFringe: 126,
      backdropDarkLuma: 108,
      backdropCropPadding: 3,
    }),
  });

  function worldVisualFor(citizenId) {
    return CITIZEN_WORLD_VISUALS[String(citizenId)] || null;
  }


  function prepareWorldBodyImage(img, visual) {
    if (!visual?.removeConnectedBackdrop) return;

    img.classList.add("world-body-cleaning");

    img.addEventListener("load", () => {
      if (img.dataset.worldBodyCleaned === "1") {
        img.classList.remove("world-body-cleaning");
        return;
      }

      const width = img.naturalWidth;
      const height = img.naturalHeight;
      if (!width || !height) {
        img.classList.remove("world-body-cleaning");
        return;
      }

      try {
        const sourceCanvas = document.createElement("canvas");
        sourceCanvas.width = width;
        sourceCanvas.height = height;
        const context = sourceCanvas.getContext("2d", { willReadFrequently: true });
        if (!context) throw new Error("No 2D canvas context");

        context.drawImage(img, 0, 0, width, height);
        const frame = context.getImageData(0, 0, width, height);
        const pixels = frame.data;

        const corners = [
          0,
          (width - 1) * 4,
          ((height - 1) * width) * 4,
          (((height - 1) * width) + (width - 1)) * 4,
        ];

        const backdrop = [0, 1, 2].map(channel =>
          Math.round(corners.reduce((sum, offset) => sum + pixels[offset + channel], 0) / corners.length)
        );

        const tolerance = Number(visual.backdropTolerance || 60);
        const fringe = Number(visual.backdropFringe || (tolerance + 48));
        const darkLuma = Number(visual.backdropDarkLuma || 96);
        const cropPadding = Math.max(0, Number(visual.backdropCropPadding || 2));
        const count = width * height;
        const connected = new Uint8Array(count);
        const queued = new Uint8Array(count);
        const queue = new Int32Array(count);
        let head = 0;
        let tail = 0;

        const pixelChannels = index => {
          const offset = index * 4;
          const r = pixels[offset];
          const g = pixels[offset + 1];
          const b = pixels[offset + 2];
          return { r, g, b };
        };

        const distanceAt = index => {
          const { r, g, b } = pixelChannels(index);
          return Math.hypot(r - backdrop[0], g - backdrop[1], b - backdrop[2]);
        };

        const lumaAt = index => {
          const { r, g, b } = pixelChannels(index);
          return (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
        };

        const isBackdropCandidate = index => {
          const { r, g, b } = pixelChannels(index);
          const luma = (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
          const chroma = Math.max(r, g, b) - Math.min(r, g, b);
          const distance = Math.hypot(r - backdrop[0], g - backdrop[1], b - backdrop[2]);

          return distance <= fringe
            || luma <= darkLuma
            || (luma <= (darkLuma + 30) && chroma <= 72 && distance <= (fringe + 42));
        };

        const enqueue = index => {
          if (index < 0 || index >= count || queued[index] || !isBackdropCandidate(index)) return;
          queued[index] = 1;
          queue[tail++] = index;
        };

        for (let x = 0; x < width; x += 1) {
          enqueue(x);
          enqueue(((height - 1) * width) + x);
        }
        for (let y = 0; y < height; y += 1) {
          enqueue(y * width);
          enqueue((y * width) + width - 1);
        }

        while (head < tail) {
          const index = queue[head++];
          connected[index] = 1;
          const x = index % width;
          const y = Math.floor(index / width);

          for (let dy = -1; dy <= 1; dy += 1) {
            for (let dx = -1; dx <= 1; dx += 1) {
              if (!dx && !dy) continue;
              const nx = x + dx;
              const ny = y + dy;
              if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
              enqueue((ny * width) + nx);
            }
          }
        }

        for (let index = 0; index < count; index += 1) {
          if (!connected[index]) continue;
          pixels[(index * 4) + 3] = 0;
        }

        context.putImageData(frame, 0, 0);

        let minX = width;
        let minY = height;
        let maxX = -1;
        let maxY = -1;

        for (let y = 0; y < height; y += 1) {
          for (let x = 0; x < width; x += 1) {
            const alpha = pixels[((y * width) + x) * 4 + 3];
            if (alpha <= 6) continue;
            if (x < minX) minX = x;
            if (x > maxX) maxX = x;
            if (y < minY) minY = y;
            if (y > maxY) maxY = y;
          }
        }

        if (maxX < minX || maxY < minY) throw new Error("Backdrop cleanup removed the entire sprite");

        minX = Math.max(0, Math.floor(minX - cropPadding));
        minY = Math.max(0, Math.floor(minY - cropPadding));
        maxX = Math.min(width - 1, Math.ceil(maxX + cropPadding));
        maxY = Math.min(height - 1, Math.ceil(maxY + cropPadding));

        const croppedWidth = Math.max(1, maxX - minX + 1);
        const croppedHeight = Math.max(1, maxY - minY + 1);
        const outputCanvas = document.createElement("canvas");
        outputCanvas.width = croppedWidth;
        outputCanvas.height = croppedHeight;
        const outputContext = outputCanvas.getContext("2d");
        if (!outputContext) throw new Error("No output canvas context");

        outputContext.drawImage(
          sourceCanvas,
          minX, minY, croppedWidth, croppedHeight,
          0, 0, croppedWidth, croppedHeight
        );

        img.dataset.worldBodyCleaned = "1";
        img.src = outputCanvas.toDataURL("image/png");
      } catch (_error) {
        img.dataset.worldBodyCleaned = "1";
        img.classList.remove("world-body-cleaning");
      }
    });
  }

  const query = new URLSearchParams(window.location.search);
  const embedded = query.get("embed") === "1";
  const requestedMode = query.get("mode");
  const initialMode = ["planet", "region", "local"].includes(requestedMode) ? requestedMode : "planet";
  if (embedded) document.body.classList.add("embedded");

  const gl = canvas.getContext("webgl", {
    antialias: true,
    alpha: false,
    preserveDrawingBuffer: false,
  });

  if (!gl) {
    connectionPill.textContent = "WebGL unavailable";
    connectionPill.classList.add("offline");
    selectionBody.innerHTML = "<p>This browser did not provide WebGL. The ordinary Agent City interface still works.</p>";
    return;
  }

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  let state = null;
  let visitorPresence = null;
  let stateClockBaseSimMinute = 0;
  let stateClockBaseRealMs = performance.now();
  let mode = initialMode;
  let selected = { type: "location", id: "seed_site" };
  let markerItems = [];
  let dragging = false;
  let dragKind = "orbit";
  let lastPointer = { x: 0, y: 0 };
  let frameHandle = null;
  let cameraTween = null;
  let localRouteBuffer = null;
  let localRouteVertexCount = 0;
  let localTerrainData = null;
  let localTerrainBuffer = null;
  let localTerrainNormalBuffer = null;
  let localTerrainVertexCount = 0;
  let localTerrainHighlightBuffer = null;
  let localTerrainHighlightVertexCount = 0;
  let localTerrainShadowBuffer = null;
  let localTerrainShadowVertexCount = 0;
  let localTerrainWireBuffer = null;
  let localTerrainWireVertexCount = 0;
  let localTerrainMajorWireBuffer = null;
  let localTerrainMajorWireVertexCount = 0;
  let localLocationPadBuffer = null;
  let localLocationPadVertexCount = 0;
  let localLocationPadRingBuffer = null;
  let localLocationPadRingVertexCount = 0;
  let localTerrainRequestKey = "";
  let localSurfaceStatus = "loading surface…";

  const LOCAL_SURFACE_HALF_EXTENT = 3.45;
  const LOCAL_TERRAIN_PADDING_FACTOR = 1.55;
  const LOCAL_TERRAIN_RESOLUTION = 41;
  const LOCAL_TERRAIN_VERTICAL_EXAGGERATION = 3.2;

  const camera = {
    yaw: -0.72,
    pitch: 0.34,
    distance: 3.25,
    target: [0, 0, 0],
  };

  const localFrame = {
    seedX: 0,
    seedY: 0,
    metersPerWorld: 1000,
    radiusMeters: 1000,
    terrainRadiusMeters: 1550,
  };

  const globeFrame = {
    anchorLat: 0.32,
    anchorLon: -0.58,
    radiansPerMeter: 0.0001,
  };

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const finite = value => {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  };
  const escapeHtml = value => String(value == null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  const titleCase = value => String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, c => c.toUpperCase());

  function visualDayPhase(simMinute) {
    const minute = ((Number(simMinute) % 1440) + 1440) % 1440;
    if (minute >= 300 && minute < 420) return "dawn";
    if (minute >= 420 && minute < 1080) return "day";
    if (minute >= 1080 && minute < 1320) return "dusk";
    return "night";
  }

  function smoothstep01(edge0, edge1, value) {
    const t = clamp((value - edge0) / Math.max(0.000001, edge1 - edge0), 0, 1);
    return t * t * (3 - 2 * t);
  }

  function mix3(a, b, amount) {
    const t = clamp(amount, 0, 1);
    return [
      a[0] + (b[0] - a[0]) * t,
      a[1] + (b[1] - a[1]) * t,
      a[2] + (b[2] - a[2]) * t,
    ];
  }

  function solarLighting(now = performance.now()) {
    const simMinute = state ? continuousSimMinute(now) : 720;
    const minute = ((Number(simMinute) % 1440) + 1440) % 1440;

    // 06:00 = east horizon, 12:00 = overhead, 18:00 = west horizon,
    // 00:00 = below the Local tangent plane.
    const solarPhase = ((minute - 360) / 1440) * Math.PI * 2;
    const localDirection = vec3Normalize([
      Math.cos(solarPhase),
      Math.sin(solarPhase),
      -0.10,
    ]);

    const altitude = localDirection[1];
    const daylight = smoothstep01(-0.10, 0.22, altitude);
    const twilight = 1 - smoothstep01(0.08, 0.55, Math.abs(altitude));
    const sunColor = mix3(
      [1.0, 0.56, 0.32],
      [1.0, 0.94, 0.82],
      smoothstep01(0.02, 0.62, altitude),
    );

    // Convert the Local tangent sun direction into globe coordinates so Local,
    // Region, and Planet share one light source and the Seed Site day/night
    // state agrees with the globe hemisphere.
    const lat = globeFrame.anchorLat;
    const lon = globeFrame.anchorLon;
    const up = [
      Math.cos(lat) * Math.sin(lon),
      Math.sin(lat),
      Math.cos(lat) * Math.cos(lon),
    ];
    const east = [Math.cos(lon), 0, -Math.sin(lon)];
    const north = [
      -Math.sin(lat) * Math.sin(lon),
      Math.cos(lat),
      -Math.sin(lat) * Math.cos(lon),
    ];
    const globeDirection = vec3Normalize([
      east[0] * localDirection[0] + up[0] * localDirection[1] - north[0] * localDirection[2],
      east[1] * localDirection[0] + up[1] * localDirection[1] - north[1] * localDirection[2],
      east[2] * localDirection[0] + up[2] * localDirection[1] - north[2] * localDirection[2],
    ]);

    return {
      simMinute,
      minute,
      phase: visualDayPhase(minute),
      localDirection,
      globeDirection,
      altitude,
      daylight,
      twilight,
      ambient: 0.18 + daylight * 0.34 + twilight * 0.045,
      direct: 0.40 + daylight * 0.78,
      sunColor,
      nightColor: mix3([0.008, 0.020, 0.040], [0.020, 0.075, 0.090], daylight),
    };
  }

  function lightingPhaseLabel(lighting) {
    return {
      dawn: "dawn light",
      day: "daylight",
      dusk: "dusk light",
      night: "night",
    }[lighting.phase] || lighting.phase;
  }

  function localPalette(now = performance.now(), phaseOverride = null) {
    const phase = phaseOverride || visualDayPhase(state ? continuousSimMinute(now) : 720);
    return {
      dawn: {
        clear: [0.055, 0.075, 0.105, 1],
        plane: [0.065, 0.135, 0.14, 0.96],
        grid: [0.32, 0.67, 0.70, 0.20],
      },
      day: {
        clear: [0.018, 0.04, 0.052, 1],
        plane: [0.055, 0.14, 0.14, 0.96],
        grid: [0.28, 0.68, 0.72, 0.18],
      },
      dusk: {
        clear: [0.055, 0.035, 0.065, 1],
        plane: [0.055, 0.09, 0.105, 0.97],
        grid: [0.30, 0.50, 0.62, 0.17],
      },
      night: {
        clear: [0.006, 0.012, 0.027, 1],
        plane: [0.018, 0.055, 0.075, 0.98],
        grid: [0.22, 0.46, 0.58, 0.15],
      },
    }[phase];
  }

  function vec3Length(v) {
    return Math.hypot(v[0], v[1], v[2]);
  }

  function vec3Normalize(v) {
    const length = vec3Length(v) || 1;
    return [v[0] / length, v[1] / length, v[2] / length];
  }

  function vec3Dot(a, b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  }

  function vec3Sub(a, b) {
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  }

  function vec3Cross(a, b) {
    return [
      a[1] * b[2] - a[2] * b[1],
      a[2] * b[0] - a[0] * b[2],
      a[0] * b[1] - a[1] * b[0],
    ];
  }

  function mat4Perspective(fovY, aspect, near, far) {
    const f = 1 / Math.tan(fovY / 2);
    const nf = 1 / (near - far);
    return [
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (far + near) * nf, -1,
      0, 0, (2 * far * near) * nf, 0,
    ];
  }

  function mat4LookAt(eye, center, up) {
    const z = vec3Normalize(vec3Sub(eye, center));
    const x = vec3Normalize(vec3Cross(up, z));
    const y = vec3Cross(z, x);

    return [
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -vec3Dot(x, eye), -vec3Dot(y, eye), -vec3Dot(z, eye), 1,
    ];
  }

  function mat4Multiply(a, b) {
    const out = new Array(16).fill(0);
    for (let c = 0; c < 4; c += 1) {
      for (let r = 0; r < 4; r += 1) {
        out[c * 4 + r] =
          a[0 * 4 + r] * b[c * 4 + 0] +
          a[1 * 4 + r] * b[c * 4 + 1] +
          a[2 * 4 + r] * b[c * 4 + 2] +
          a[3 * 4 + r] * b[c * 4 + 3];
      }
    }
    return out;
  }

  function transformPoint(matrix, point) {
    const x = point[0];
    const y = point[1];
    const z = point[2];
    return [
      matrix[0] * x + matrix[4] * y + matrix[8] * z + matrix[12],
      matrix[1] * x + matrix[5] * y + matrix[9] * z + matrix[13],
      matrix[2] * x + matrix[6] * y + matrix[10] * z + matrix[14],
      matrix[3] * x + matrix[7] * y + matrix[11] * z + matrix[15],
    ];
  }

  function cameraEye() {
    const cp = Math.cos(camera.pitch);
    return [
      camera.target[0] + camera.distance * cp * Math.sin(camera.yaw),
      camera.target[1] + camera.distance * Math.sin(camera.pitch),
      camera.target[2] + camera.distance * cp * Math.cos(camera.yaw),
    ];
  }

  function viewProjection() {
    const aspect = Math.max(0.1, canvas.clientWidth / Math.max(1, canvas.clientHeight));
    const projection = mat4Perspective(Math.PI / 3.2, aspect, 0.02, 100);
    const view = mat4LookAt(cameraEye(), camera.target, [0, 1, 0]);
    return mat4Multiply(projection, view);
  }

  function compileShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const message = gl.getShaderInfoLog(shader);
      gl.deleteShader(shader);
      throw new Error(message || "Shader compilation failed");
    }
    return shader;
  }

  function createProgram(vertexSource, fragmentSource) {
    const program = gl.createProgram();
    gl.attachShader(program, compileShader(gl.VERTEX_SHADER, vertexSource));
    gl.attachShader(program, compileShader(gl.FRAGMENT_SHADER, fragmentSource));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      const message = gl.getProgramInfoLog(program);
      gl.deleteProgram(program);
      throw new Error(message || "Shader link failed");
    }
    return program;
  }

  const litProgram = createProgram(
    [
      "attribute vec3 aPosition;",
      "attribute vec3 aNormal;",
      "uniform mat4 uMVP;",
      "varying vec3 vNormal;",
      "void main() {",
      "  vNormal = aNormal;",
      "  gl_Position = uMVP * vec4(aPosition, 1.0);",
      "}",
    ].join("\n"),
    [
      "precision mediump float;",
      "uniform vec3 uLightDir;",
      "uniform vec3 uBaseColor;",
      "uniform vec3 uSunColor;",
      "uniform vec3 uNightColor;",
      "uniform float uAmbient;",
      "uniform float uDirect;",
      "uniform float uTerminatorWidth;",
      "varying vec3 vNormal;",
      "void main() {",
      "  vec3 n = normalize(vNormal);",
      "  float incidence = dot(n, normalize(uLightDir));",
      "  float dayMask = smoothstep(-uTerminatorWidth, uTerminatorWidth, incidence);",
      "  float directLight = max(incidence, 0.0);",
      "  float polar = 0.5 + 0.5 * abs(n.y);",
      "  vec3 dayColor = uBaseColor * (uAmbient + directLight * uDirect);",
      "  dayColor += uSunColor * directLight * 0.18;",
      "  vec3 nightColor = uNightColor + uBaseColor * (0.07 + polar * 0.06);",
      "  gl_FragColor = vec4(mix(nightColor, dayColor, dayMask), 1.0);",
      "}",
    ].join("\n")
  );

  const colorProgram = createProgram(
    [
      "attribute vec3 aPosition;",
      "uniform mat4 uMVP;",
      "void main() {",
      "  gl_Position = uMVP * vec4(aPosition, 1.0);",
      "}",
    ].join("\n"),
    [
      "precision mediump float;",
      "uniform vec4 uColor;",
      "void main() {",
      "  gl_FragColor = uColor;",
      "}",
    ].join("\n")
  );

  function createBuffer(data) {
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.STATIC_DRAW);
    return buffer;
  }

  function createSphere(latSegments, lonSegments) {
    const positions = [];
    const normals = [];
    const indices = [];

    for (let lat = 0; lat <= latSegments; lat += 1) {
      const v = lat / latSegments;
      const phi = (v - 0.5) * Math.PI;
      const cosPhi = Math.cos(phi);
      const sinPhi = Math.sin(phi);

      for (let lon = 0; lon <= lonSegments; lon += 1) {
        const u = lon / lonSegments;
        const theta = u * Math.PI * 2;
        const x = cosPhi * Math.sin(theta);
        const y = sinPhi;
        const z = cosPhi * Math.cos(theta);
        positions.push(x, y, z);
        normals.push(x, y, z);
      }
    }

    for (let lat = 0; lat < latSegments; lat += 1) {
      for (let lon = 0; lon < lonSegments; lon += 1) {
        const a = lat * (lonSegments + 1) + lon;
        const b = a + lonSegments + 1;
        indices.push(a, b, a + 1, b, b + 1, a + 1);
      }
    }

    const indexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indices), gl.STATIC_DRAW);

    return {
      position: createBuffer(positions),
      normal: createBuffer(normals),
      index: indexBuffer,
      count: indices.length,
    };
  }

  function createGlobeGrid() {
    const lines = [];
    const radius = 1.006;

    for (let latDeg = -60; latDeg <= 60; latDeg += 30) {
      const lat = latDeg * Math.PI / 180;
      for (let i = 0; i < 96; i += 1) {
        const lonA = (i / 96) * Math.PI * 2;
        const lonB = ((i + 1) / 96) * Math.PI * 2;
        const c = Math.cos(lat);
        const y = Math.sin(lat) * radius;
        lines.push(
          c * Math.sin(lonA) * radius, y, c * Math.cos(lonA) * radius,
          c * Math.sin(lonB) * radius, y, c * Math.cos(lonB) * radius
        );
      }
    }

    for (let lonDeg = 0; lonDeg < 360; lonDeg += 30) {
      const lon = lonDeg * Math.PI / 180;
      for (let i = 0; i < 48; i += 1) {
        const latA = (-Math.PI / 2) + (i / 48) * Math.PI;
        const latB = (-Math.PI / 2) + ((i + 1) / 48) * Math.PI;
        lines.push(
          Math.cos(latA) * Math.sin(lon) * radius,
          Math.sin(latA) * radius,
          Math.cos(latA) * Math.cos(lon) * radius,
          Math.cos(latB) * Math.sin(lon) * radius,
          Math.sin(latB) * radius,
          Math.cos(latB) * Math.cos(lon) * radius
        );
      }
    }

    return { buffer: createBuffer(lines), count: lines.length / 3 };
  }

  const sphere = createSphere(44, 64);
  const globeGrid = createGlobeGrid();

  const localPlane = {
    buffer: createBuffer([
      -LOCAL_SURFACE_HALF_EXTENT, 0, -LOCAL_SURFACE_HALF_EXTENT,
       LOCAL_SURFACE_HALF_EXTENT, 0, -LOCAL_SURFACE_HALF_EXTENT,
       LOCAL_SURFACE_HALF_EXTENT, 0,  LOCAL_SURFACE_HALF_EXTENT,
      -LOCAL_SURFACE_HALF_EXTENT, 0, -LOCAL_SURFACE_HALF_EXTENT,
       LOCAL_SURFACE_HALF_EXTENT, 0,  LOCAL_SURFACE_HALF_EXTENT,
      -LOCAL_SURFACE_HALF_EXTENT, 0,  LOCAL_SURFACE_HALF_EXTENT,
    ]),
    count: 6,
  };

  const localGridData = [];
  for (let i = -14; i <= 14; i += 1) {
    const p = i * 0.25;
    localGridData.push(
      -LOCAL_SURFACE_HALF_EXTENT, 0.008, p,
       LOCAL_SURFACE_HALF_EXTENT, 0.008, p,
    );
    localGridData.push(
      p, 0.008, -LOCAL_SURFACE_HALF_EXTENT,
      p, 0.008,  LOCAL_SURFACE_HALF_EXTENT,
    );
  }
  const localGrid = { buffer: createBuffer(localGridData), count: localGridData.length / 3 };

  function bindColorBuffer(buffer, mvp, color, primitive, count) {
    gl.useProgram(colorProgram);
    const posLoc = gl.getAttribLocation(colorProgram, "aPosition");
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 3, gl.FLOAT, false, 0, 0);
    gl.uniformMatrix4fv(gl.getUniformLocation(colorProgram, "uMVP"), false, new Float32Array(mvp));
    gl.uniform4fv(gl.getUniformLocation(colorProgram, "uColor"), new Float32Array(color));
    gl.drawArrays(primitive, 0, count);
  }

  function bindLitArrayBuffer(
    positionBuffer,
    normalBuffer,
    mvp,
    baseColor,
    lighting,
    primitive,
    count,
    options = {},
  ) {
    gl.useProgram(litProgram);
    const posLoc = gl.getAttribLocation(litProgram, "aPosition");
    const normalLoc = gl.getAttribLocation(litProgram, "aNormal");

    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, normalBuffer);
    gl.enableVertexAttribArray(normalLoc);
    gl.vertexAttribPointer(normalLoc, 3, gl.FLOAT, false, 0, 0);

    gl.uniformMatrix4fv(gl.getUniformLocation(litProgram, "uMVP"), false, new Float32Array(mvp));
    gl.uniform3fv(
      gl.getUniformLocation(litProgram, "uLightDir"),
      new Float32Array(options.lightDir || lighting.localDirection),
    );
    gl.uniform3fv(gl.getUniformLocation(litProgram, "uBaseColor"), new Float32Array(baseColor));
    gl.uniform3fv(gl.getUniformLocation(litProgram, "uSunColor"), new Float32Array(lighting.sunColor));
    gl.uniform3fv(
      gl.getUniformLocation(litProgram, "uNightColor"),
      new Float32Array(options.nightColor || lighting.nightColor),
    );
    gl.uniform1f(
      gl.getUniformLocation(litProgram, "uAmbient"),
      Number(options.ambient ?? lighting.ambient),
    );
    gl.uniform1f(
      gl.getUniformLocation(litProgram, "uDirect"),
      Number(options.direct ?? lighting.direct),
    );
    gl.uniform1f(
      gl.getUniformLocation(litProgram, "uTerminatorWidth"),
      Number(options.terminatorWidth ?? 0.08),
    );

    gl.drawArrays(primitive, 0, count);
  }

  function drawSphere(mvp, lighting) {
    gl.useProgram(litProgram);
    const posLoc = gl.getAttribLocation(litProgram, "aPosition");
    const normalLoc = gl.getAttribLocation(litProgram, "aNormal");

    gl.bindBuffer(gl.ARRAY_BUFFER, sphere.position);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, sphere.normal);
    gl.enableVertexAttribArray(normalLoc);
    gl.vertexAttribPointer(normalLoc, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, sphere.index);
    gl.uniformMatrix4fv(gl.getUniformLocation(litProgram, "uMVP"), false, new Float32Array(mvp));
    gl.uniform3fv(
      gl.getUniformLocation(litProgram, "uLightDir"),
      new Float32Array(lighting.globeDirection),
    );
    gl.uniform3fv(
      gl.getUniformLocation(litProgram, "uBaseColor"),
      new Float32Array(mode === "region" ? [0.09, 0.245, 0.27] : [0.075, 0.205, 0.235]),
    );
    gl.uniform3fv(gl.getUniformLocation(litProgram, "uSunColor"), new Float32Array(lighting.sunColor));
    gl.uniform3fv(
      gl.getUniformLocation(litProgram, "uNightColor"),
      new Float32Array(mode === "region" ? [0.012, 0.038, 0.060] : [0.005, 0.014, 0.032]),
    );
    gl.uniform1f(
      gl.getUniformLocation(litProgram, "uAmbient"),
      mode === "region" ? 0.50 : 0.42,
    );
    gl.uniform1f(
      gl.getUniformLocation(litProgram, "uDirect"),
      mode === "region" ? 0.92 : 1.04,
    );
    gl.uniform1f(
      gl.getUniformLocation(litProgram, "uTerminatorWidth"),
      mode === "region" ? 0.11 : 0.075,
    );

    gl.drawElements(gl.TRIANGLES, sphere.count, gl.UNSIGNED_SHORT, 0);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    const gridAlpha = mode === "region" ? 0.19 : 0.13;
    bindColorBuffer(
      globeGrid.buffer,
      mvp,
      [0.20, 0.75, 0.82, gridAlpha],
      gl.LINES,
      globeGrid.count,
    );
    gl.disable(gl.BLEND);
  }

  function drawLocal(mvp, lighting) {
    const palette = localPalette(performance.now(), lighting.phase);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    if (
      localTerrainBuffer
      && localTerrainNormalBuffer
      && localTerrainVertexCount
    ) {
      const terrainBase = [
        palette.plane[0] * 1.12,
        palette.plane[1] * 1.06,
        palette.plane[2] * 1.00,
      ];
      const terrainHighlight = [
        Math.min(1, palette.plane[0] * 2.35),
        Math.min(1, palette.plane[1] * 1.55),
        Math.min(1, palette.plane[2] * 1.45),
        0.035 + lighting.daylight * 0.075,
      ];
      const terrainShadow = [
        palette.plane[0] * 0.28,
        palette.plane[1] * 0.34,
        palette.plane[2] * 0.42,
        0.065 + lighting.daylight * 0.07,
      ];
      const terrainWire = [
        palette.grid[0],
        palette.grid[1],
        palette.grid[2],
        0.075 + lighting.daylight * 0.035,
      ];
      const terrainMajorWire = [
        palette.grid[0] * 1.08,
        palette.grid[1] * 1.06,
        palette.grid[2] * 1.04,
        0.15 + lighting.daylight * 0.05,
      ];

      bindLitArrayBuffer(
        localTerrainBuffer,
        localTerrainNormalBuffer,
        mvp,
        terrainBase,
        lighting,
        gl.TRIANGLES,
        localTerrainVertexCount,
        {
          lightDir: lighting.localDirection,
          nightColor: [0.007, 0.028, 0.046],
          ambient: lighting.ambient,
          direct: lighting.direct,
          terminatorWidth: 0.10,
        },
      );

      if (localTerrainHighlightBuffer && localTerrainHighlightVertexCount) {
        bindColorBuffer(
          localTerrainHighlightBuffer,
          mvp,
          terrainHighlight,
          gl.TRIANGLES,
          localTerrainHighlightVertexCount,
        );
      }
      if (localTerrainShadowBuffer && localTerrainShadowVertexCount) {
        bindColorBuffer(
          localTerrainShadowBuffer,
          mvp,
          terrainShadow,
          gl.TRIANGLES,
          localTerrainShadowVertexCount,
        );
      }

      if (localTerrainWireBuffer && localTerrainWireVertexCount) {
        bindColorBuffer(localTerrainWireBuffer, mvp, terrainWire, gl.LINES, localTerrainWireVertexCount);
      }
      if (localTerrainMajorWireBuffer && localTerrainMajorWireVertexCount) {
        bindColorBuffer(
          localTerrainMajorWireBuffer,
          mvp,
          terrainMajorWire,
          gl.LINES,
          localTerrainMajorWireVertexCount,
        );
      }

      if (localLocationPadBuffer && localLocationPadVertexCount) {
        bindColorBuffer(
          localLocationPadBuffer,
          mvp,
          [0.13, 0.39, 0.39, 0.13 + lighting.daylight * 0.06],
          gl.TRIANGLES,
          localLocationPadVertexCount,
        );
      }
      if (localLocationPadRingBuffer && localLocationPadRingVertexCount) {
        bindColorBuffer(
          localLocationPadRingBuffer,
          mvp,
          [0.42, 0.76, 0.72, 0.26 + lighting.daylight * 0.06],
          gl.LINES,
          localLocationPadRingVertexCount,
        );
      }
    } else {
      const fallbackPlane = [
        palette.plane[0] * (0.72 + lighting.daylight * 0.28),
        palette.plane[1] * (0.68 + lighting.daylight * 0.32),
        palette.plane[2] * (0.72 + lighting.daylight * 0.28),
        palette.plane[3],
      ];
      bindColorBuffer(localPlane.buffer, mvp, fallbackPlane, gl.TRIANGLES, localPlane.count);
      bindColorBuffer(localGrid.buffer, mvp, palette.grid, gl.LINES, localGrid.count);
    }

    if (localRouteBuffer && localRouteVertexCount) {
      bindColorBuffer(
        localRouteBuffer,
        mvp,
        [0.85, 0.64, 0.28, 0.56 + lighting.daylight * 0.08],
        gl.LINES,
        localRouteVertexCount,
      );
    }
    gl.disable(gl.BLEND);
  }

  function knownLocations() {
    return (state && state.locations || []).filter(loc => finite(loc.x_m) != null && finite(loc.y_m) != null);
  }

  function seedLocation() {
    return knownLocations().find(loc => String(loc.id) === "seed_site") || knownLocations()[0] || { x_m: 0, y_m: 0, id: "seed_site", name: "Seed Site" };
  }

  function refreshFrames() {
    const seed = seedLocation();
    localFrame.seedX = finite(seed.x_m) || 0;
    localFrame.seedY = finite(seed.y_m) || 0;

    const points = [];
    for (const loc of knownLocations()) points.push([finite(loc.x_m), finite(loc.y_m)]);
    for (const citizen of state && state.citizens || []) {
      if (finite(citizen.position_x_m) != null && finite(citizen.position_y_m) != null) {
        points.push([finite(citizen.position_x_m), finite(citizen.position_y_m)]);
      }
    }
    for (const structure of state && state.structures || []) {
      if (finite(structure.x_m) != null && finite(structure.y_m) != null) {
        points.push([finite(structure.x_m), finite(structure.y_m)]);
      }
    }

    let maxRadius = 500;
    for (const point of points) {
      maxRadius = Math.max(
        maxRadius,
        Math.hypot(point[0] - localFrame.seedX, point[1] - localFrame.seedY)
      );
    }

    localFrame.radiusMeters = maxRadius;
    localFrame.metersPerWorld = maxRadius / 2.18;
    localFrame.terrainRadiusMeters = clamp(
      Math.max(800, maxRadius * LOCAL_TERRAIN_PADDING_FACTOR),
      800,
      4200,
    );
    globeFrame.radiansPerMeter = 0.42 / maxRadius;
    rebuildLocalRoutes();
    if (localTerrainData) rebuildLocalLocationPads();
  }

  function localHorizontalWorld(xMeters, yMeters) {
    const x = ((finite(xMeters) || 0) - localFrame.seedX) / localFrame.metersPerWorld;
    const z = -(((finite(yMeters) || 0) - localFrame.seedY) / localFrame.metersPerWorld);
    return [x, z];
  }

  function terrainHeightMetersAt(xMeters, yMeters) {
    if (!localTerrainData) return 0;

    const resolution = Number(localTerrainData.resolution || 0);
    const radius = Number(localTerrainData.radius_m || 0);
    const centerX = Number(localTerrainData.center_x_m || 0);
    const centerY = Number(localTerrainData.center_y_m || 0);
    const heights = localTerrainData.heights_m || [];
    if (resolution < 2 || radius <= 0 || heights.length !== resolution * resolution) return 0;

    const u = ((Number(xMeters) - (centerX - radius)) / (radius * 2)) * (resolution - 1);
    const v = (((centerY + radius) - Number(yMeters)) / (radius * 2)) * (resolution - 1);
    if (u < 0 || v < 0 || u > resolution - 1 || v > resolution - 1) return 0;

    const x0 = Math.floor(u);
    const y0 = Math.floor(v);
    const x1 = Math.min(resolution - 1, x0 + 1);
    const y1 = Math.min(resolution - 1, y0 + 1);
    const tx = u - x0;
    const ty = v - y0;

    const h00 = Number(heights[y0 * resolution + x0] || 0);
    const h10 = Number(heights[y0 * resolution + x1] || 0);
    const h01 = Number(heights[y1 * resolution + x0] || 0);
    const h11 = Number(heights[y1 * resolution + x1] || 0);
    const top = h00 + (h10 - h00) * tx;
    const bottom = h01 + (h11 - h01) * tx;
    return top + (bottom - top) * ty;
  }

  function terrainWorldHeightAt(xMeters, yMeters) {
    return (terrainHeightMetersAt(xMeters, yMeters) / localFrame.metersPerWorld)
      * LOCAL_TERRAIN_VERTICAL_EXAGGERATION;
  }

  function localWorld(xMeters, yMeters, lift) {
    const [x, z] = localHorizontalWorld(xMeters, yMeters);
    const offset = lift == null ? 0.025 : Number(lift);
    return [x, terrainWorldHeightAt(xMeters, yMeters) + offset, z];
  }

  function globeWorld(xMeters, yMeters, radius) {
    const dx = (finite(xMeters) || 0) - localFrame.seedX;
    const dy = (finite(yMeters) || 0) - localFrame.seedY;
    const lat = globeFrame.anchorLat + dy * globeFrame.radiansPerMeter;
    const lon = globeFrame.anchorLon + (dx * globeFrame.radiansPerMeter) / Math.max(0.25, Math.cos(globeFrame.anchorLat));
    const r = radius || 1.025;
    const c = Math.cos(lat);
    return [
      c * Math.sin(lon) * r,
      Math.sin(lat) * r,
      c * Math.cos(lon) * r,
    ];
  }

  function locationById(id) {
    return knownLocations().find(loc => String(loc.id) === String(id)) || null;
  }

  function activeJobFor(citizen) {
    if (!citizen || !state) return null;
    if (citizen.active_job_id != null) {
      const job = (state.jobs || []).find(row => Number(row.id) === Number(citizen.active_job_id));
      if (job) return job;
    }
    return (state.jobs || []).find(row => String(row.citizen_id) === String(citizen.id)) || null;
  }

  function continuousSimMinute(now = performance.now()) {
    if (!state) return 0;
    const base = Number.isFinite(Number(stateClockBaseSimMinute))
      ? Number(stateClockBaseSimMinute)
      : Number(state.sim_minute || 0);
    if (state.paused) return base;
    const elapsedSeconds = Math.max(0, now - stateClockBaseRealMs) / 1000;
    const ratio = Math.max(0, Number(state.time_ratio || 0));
    return base + ((elapsedSeconds * ratio) / 60);
  }

  function citizenRenderMeters(citizen, now = performance.now()) {
    const fallbackX = finite(citizen && citizen.position_x_m);
    const fallbackY = finite(citizen && citizen.position_y_m);
    const fallback = [fallbackX, fallbackY];

    const job = activeJobFor(citizen);
    if (!job || String(job.action) !== "travel") return fallback;

    const from = locationById(citizen.location_id);
    const to = locationById(job.target);
    if (!from || !to) return fallback;

    const startMinute = finite(job.start_minute);
    const endMinute = finite(job.end_minute);
    if (startMinute == null || endMinute == null || endMinute <= startMinute) return fallback;

    const fraction = clamp(
      (continuousSimMinute(now) - startMinute) / (endMinute - startMinute),
      0,
      1,
    );

    return [
      Number(from.x_m) + ((Number(to.x_m) - Number(from.x_m)) * fraction),
      Number(from.y_m) + ((Number(to.y_m) - Number(from.y_m)) * fraction),
    ];
  }

  function rebuildLocalRoutes() {
    const vertices = [];
    const byId = new Map(knownLocations().map(loc => [String(loc.id), loc]));

    for (const route of state && state.routes || []) {
      const a = byId.get(String(route.a));
      const b = byId.get(String(route.b));
      if (!a || !b) continue;

      const ax = Number(a.x_m);
      const ay = Number(a.y_m);
      const bx = Number(b.x_m);
      const by = Number(b.y_m);
      const distanceMeters = Math.hypot(bx - ax, by - ay);
      const segments = clamp(Math.ceil(distanceMeters / 140), 8, 32);
      let previous = localWorld(ax, ay, 0.022);

      for (let step = 1; step <= segments; step += 1) {
        const t = step / segments;
        const x = ax + (bx - ax) * t;
        const y = ay + (by - ay) * t;
        const current = localWorld(x, y, 0.022);
        vertices.push(...previous, ...current);
        previous = current;
      }
    }

    if (localRouteBuffer) gl.deleteBuffer(localRouteBuffer);
    localRouteBuffer = vertices.length ? createBuffer(vertices) : null;
    localRouteVertexCount = vertices.length / 3;
  }

  function rebuildLocalLocationPads() {
    const triangles = [];
    const rings = [];
    const segmentCount = 18;
    const padRadiusMeters = clamp(localFrame.metersPerWorld * 0.105, 52, 110);

    for (const location of knownLocations()) {
      const xMeters = finite(location.x_m);
      const yMeters = finite(location.y_m);
      if (xMeters == null || yMeters == null) continue;

      const center = localWorld(xMeters, yMeters, 0.010);
      let previous = null;
      let first = null;

      for (let step = 0; step < segmentCount; step += 1) {
        const angle = (step / segmentCount) * Math.PI * 2;
        const x = xMeters + Math.cos(angle) * padRadiusMeters;
        const y = yMeters + Math.sin(angle) * padRadiusMeters;
        const edge = localWorld(x, y, 0.012);

        if (!first) first = edge;
        if (previous) {
          triangles.push(...center, ...previous, ...edge);
          rings.push(...previous, ...edge);
        }
        previous = edge;
      }

      if (previous && first) {
        triangles.push(...center, ...previous, ...first);
        rings.push(...previous, ...first);
      }
    }

    if (localLocationPadBuffer) gl.deleteBuffer(localLocationPadBuffer);
    if (localLocationPadRingBuffer) gl.deleteBuffer(localLocationPadRingBuffer);

    localLocationPadBuffer = triangles.length ? createBuffer(triangles) : null;
    localLocationPadVertexCount = triangles.length / 3;
    localLocationPadRingBuffer = rings.length ? createBuffer(rings) : null;
    localLocationPadRingVertexCount = rings.length / 3;
  }

  function rebuildLocalTerrain(payload) {
    const resolution = Number(payload && payload.resolution || 0);
    const radius = Number(payload && payload.radius_m || 0);
    const centerX = Number(payload && payload.center_x_m || 0);
    const centerY = Number(payload && payload.center_y_m || 0);
    const heights = payload && payload.heights_m || [];

    if (
      payload?.discovery_boundary !== "surface_only_no_geology_or_deposits"
      || resolution < 2
      || radius <= 0
      || heights.length !== resolution * resolution
    ) {
      console.warn("Local terrain payload failed its safe-surface contract.");
      return;
    }

    const triangles = [];
    const normals = [];
    const highlightTriangles = [];
    const shadowTriangles = [];
    const wires = [];
    const majorWires = [];
    const spacing = (radius * 2) / (resolution - 1);
    const minElevation = Number(payload.min_elevation_m || 0);
    const maxElevation = Number(payload.max_elevation_m || 0);
    const elevationRange = Math.max(1, maxElevation - minElevation);
    const highElevationThreshold = minElevation + elevationRange * 0.63;
    const steepSlopeThreshold = 0.045;

    const point = (row, column, lift = 0) => {
      const xMeters = centerX - radius + (column * spacing);
      const yMeters = centerY + radius - (row * spacing);
      const [x, z] = localHorizontalWorld(xMeters, yMeters);
      const elevationMeters = Number(heights[row * resolution + column] || 0);
      const y = (elevationMeters / localFrame.metersPerWorld)
        * LOCAL_TERRAIN_VERTICAL_EXAGGERATION;
      return [x, y + lift, z];
    };

    const cellTriangles = (a, b, c1, d) => [
      ...a, ...b, ...c1,
      ...a, ...c1, ...d,
    ];

    const addLitTriangle = (p0, p1, p2) => {
      triangles.push(...p0, ...p1, ...p2);
      let normal = vec3Normalize(vec3Cross(vec3Sub(p1, p0), vec3Sub(p2, p0)));
      if (normal[1] < 0) normal = [-normal[0], -normal[1], -normal[2]];
      normals.push(...normal, ...normal, ...normal);
    };

    for (let row = 0; row < resolution - 1; row += 1) {
      for (let column = 0; column < resolution - 1; column += 1) {
        const a = point(row, column);
        const b = point(row, column + 1);
        const c1 = point(row + 1, column + 1);
        const d = point(row + 1, column);
        const cell = cellTriangles(a, b, c1, d);
        addLitTriangle(a, b, c1);
        addLitTriangle(a, c1, d);

        const h00 = Number(heights[row * resolution + column] || 0);
        const h10 = Number(heights[row * resolution + column + 1] || 0);
        const h11 = Number(heights[(row + 1) * resolution + column + 1] || 0);
        const h01 = Number(heights[(row + 1) * resolution + column] || 0);
        const averageElevation = (h00 + h10 + h11 + h01) / 4;
        const localRelief = Math.max(h00, h10, h11, h01) - Math.min(h00, h10, h11, h01);
        const slopeRatio = localRelief / Math.max(1, spacing);

        if (averageElevation >= highElevationThreshold) {
          highlightTriangles.push(...cell);
        }
        if (slopeRatio >= steepSlopeThreshold) {
          shadowTriangles.push(...cell);
        }
      }
    }

    // Half-density minor wires reduce foreground visual noise. Every sixth
    // sample remains a slightly stronger major contour/grid reference.
    const minorStride = 2;
    const majorStride = 6;

    for (let row = 0; row < resolution; row += minorStride) {
      if (row % majorStride === 0) continue;
      for (let column = 0; column < resolution - 1; column += 1) {
        wires.push(...point(row, column, 0.004), ...point(row, column + 1, 0.004));
      }
    }
    for (let column = 0; column < resolution; column += minorStride) {
      if (column % majorStride === 0) continue;
      for (let row = 0; row < resolution - 1; row += 1) {
        wires.push(...point(row, column, 0.004), ...point(row + 1, column, 0.004));
      }
    }
    for (let row = 0; row < resolution; row += majorStride) {
      for (let column = 0; column < resolution - 1; column += 1) {
        majorWires.push(...point(row, column, 0.005), ...point(row, column + 1, 0.005));
      }
    }
    for (let column = 0; column < resolution; column += majorStride) {
      for (let row = 0; row < resolution - 1; row += 1) {
        majorWires.push(...point(row, column, 0.005), ...point(row + 1, column, 0.005));
      }
    }

    for (const buffer of [
      localTerrainBuffer,
      localTerrainNormalBuffer,
      localTerrainHighlightBuffer,
      localTerrainShadowBuffer,
      localTerrainWireBuffer,
      localTerrainMajorWireBuffer,
    ]) {
      if (buffer) gl.deleteBuffer(buffer);
    }

    localTerrainData = payload;
    localTerrainBuffer = createBuffer(triangles);
    localTerrainNormalBuffer = createBuffer(normals);
    localTerrainVertexCount = triangles.length / 3;
    localTerrainHighlightBuffer = highlightTriangles.length ? createBuffer(highlightTriangles) : null;
    localTerrainHighlightVertexCount = highlightTriangles.length / 3;
    localTerrainShadowBuffer = shadowTriangles.length ? createBuffer(shadowTriangles) : null;
    localTerrainShadowVertexCount = shadowTriangles.length / 3;
    localTerrainWireBuffer = wires.length ? createBuffer(wires) : null;
    localTerrainWireVertexCount = wires.length / 3;
    localTerrainMajorWireBuffer = majorWires.length ? createBuffer(majorWires) : null;
    localTerrainMajorWireVertexCount = majorWires.length / 3;

    rebuildLocalLocationPads();

    localSurfaceStatus = resolution + "×" + resolution + " surface loaded";

    // Routes and markers use localWorld(), so rebuild route geometry once the
    // surface exists and let marker projection pick up terrain height live.
    rebuildLocalRoutes();
  }

  async function refreshLocalTerrain() {
    localSurfaceStatus = localTerrainBuffer ? localSurfaceStatus : "loading surface…";
    const requestedRadius = Math.round(localFrame.terrainRadiusMeters / 50) * 50;
    const requestKey = [
      localFrame.seedX.toFixed(2),
      localFrame.seedY.toFixed(2),
      localFrame.metersPerWorld.toFixed(3),
      requestedRadius,
      LOCAL_TERRAIN_RESOLUTION,
    ].join(":");

    if (requestKey === localTerrainRequestKey) return;

    try {
      const response = await fetch(
        "/api/world/local-terrain?radius_m="
          + encodeURIComponent(requestedRadius)
          + "&resolution="
          + encodeURIComponent(LOCAL_TERRAIN_RESOLUTION),
        { cache: "no-store" },
      );
      if (!response.ok) throw new Error("Terrain endpoint unavailable");
      const payload = await response.json();
      rebuildLocalTerrain(payload);
      localTerrainRequestKey = requestKey;
    } catch (error) {
      // The old flat Local plane remains a deliberate fallback.
      localSurfaceStatus = "flat fallback";
      console.warn("Seeded Local terrain unavailable; using flat fallback.", error);
    }
  }

  function project(world, matrix) {
    const clip = transformPoint(matrix, world);
    if (clip[3] <= 0.001) return null;
    const ndcX = clip[0] / clip[3];
    const ndcY = clip[1] / clip[3];
    const ndcZ = clip[2] / clip[3];
    if (ndcZ < -1.2 || ndcZ > 1.2 || Math.abs(ndcX) > 1.25 || Math.abs(ndcY) > 1.25) return null;
    return {
      x: (ndcX * 0.5 + 0.5) * canvas.clientWidth,
      y: (-ndcY * 0.5 + 0.5) * canvas.clientHeight,
    };
  }

  function markerVisibleOnGlobe(world, eye) {
    const normal = vec3Normalize(world);
    const cameraDirection = vec3Normalize(eye);
    return vec3Dot(normal, cameraDirection) > 0.02;
  }

  function createMarkerElement(item) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "world-marker";

    if (item.type === "location") {
      button.classList.add("location-marker");
      const dot = document.createElement("span");
      dot.className = "marker-dot";
      const label = document.createElement("span");
      label.className = "marker-label";
      label.textContent = item.data.name || item.id;
      button.append(dot, label);
    } else if (item.type === "citizen") {
      button.classList.add("citizen-marker");
      const visual = worldVisualFor(item.id);
      const img = document.createElement("img");
      img.alt = item.data.name || item.id;

      if (visual?.kind === "sprite_body") {
        const bodyClass = String(item.id) + "-world-body";
        button.classList.add("world-body-marker", "citizen-world-body", bodyClass);
        button.dataset.worldVisual = visual.kind;
        img.className = "world-body-image";
        prepareWorldBodyImage(img, visual);
        img.src = visual.baseBody;

        const gearLayer = document.createElement("span");
        gearLayer.className = "world-equipment-layer";
        gearLayer.setAttribute("aria-hidden", "true");

        const label = document.createElement("span");
        label.className = "world-body-label";
        label.textContent = item.data.name || item.id;

        img.addEventListener("error", () => {
          button.classList.remove("world-body-marker", "citizen-world-body", String(item.id) + "-world-body");
          button.removeAttribute("data-world-visual");
          gearLayer.remove();
          label.remove();
          img.className = "";
          img.src = "/static/assets/citizens/" + encodeURIComponent(item.id) + "/token.webp";
        }, { once: true });

        button.append(img, gearLayer, label);
      } else {
        img.src = "/static/assets/citizens/" + encodeURIComponent(item.id) + "/token.webp";
        img.addEventListener("error", () => {
          img.remove();
          button.textContent = String(item.data.name || item.id).slice(0, 1).toUpperCase();
        }, { once: true });
        button.append(img);
      }
    } else if (item.type === "structure") {
      button.classList.add("structure-marker");
      button.setAttribute("aria-label", item.data.name || "Structure");
    } else if (item.type === "visitor") {
      button.classList.add("visitor-marker");
      button.textContent = "YOU";
    }

    button.title = item.data.name || item.data.kind || item.id;
    button.addEventListener("click", event => {
      event.stopPropagation();
      selectItem(item.type, item.id, true);
    });
    return button;
  }

  function rebuildMarkers() {
    markerLayer.replaceChildren();
    markerItems = [];

    for (const loc of knownLocations()) {
      const item = { type: "location", id: String(loc.id), data: loc };
      item.element = createMarkerElement(item);
      markerLayer.append(item.element);
      markerItems.push(item);
    }

    if (mode === "local") {
      for (const citizen of state && state.citizens || []) {
        if (finite(citizen.position_x_m) == null || finite(citizen.position_y_m) == null) continue;
        const item = { type: "citizen", id: String(citizen.id), data: citizen };
        item.element = createMarkerElement(item);
        markerLayer.append(item.element);
        markerItems.push(item);
      }

      for (const structure of state && state.structures || []) {
        if (finite(structure.x_m) == null || finite(structure.y_m) == null) continue;
        const item = { type: "structure", id: String(structure.id), data: structure };
        item.element = createMarkerElement(item);
        markerLayer.append(item.element);
        markerItems.push(item);
      }

      if (visitorPresence && finite(visitorPresence.x_m) != null && finite(visitorPresence.y_m) != null) {
        const item = { type: "visitor", id: "visitor", data: visitorPresence };
        item.element = createMarkerElement(item);
        markerLayer.append(item.element);
        markerItems.push(item);
      }
    }

    refreshMarkerSelection();
  }

  function refreshMarkerSelection() {
    for (const item of markerItems) {
      item.element.classList.toggle(
        "selected",
        selected && item.type === selected.type && String(item.id) === String(selected.id)
      );
    }
  }

  function markerWorld(item, now = performance.now()) {
    if (mode === "local") {
      let world = null;

      if (item.type === "location") {
        world = localWorld(item.data.x_m, item.data.y_m, 0.045);
      } else if (item.type === "citizen") {
        const [x, y] = citizenRenderMeters(item.data, now);
        if (x == null || y == null) return null;
        const bodyLift = worldVisualFor(item.id)?.kind === "sprite_body" ? 0.018 : 0.075;
        world = localWorld(x, y, bodyLift);
      } else if (item.type === "structure") {
        world = localWorld(item.data.x_m, item.data.y_m, 0.06);
      } else if (item.type === "visitor") {
        world = localWorld(item.data.x_m, item.data.y_m, 0.08);
      }

      if (!world) return null;

      const offset = localMarkerWorldOffset(item, now);
      return [
        world[0] + offset[0],
        world[1] + offset[1],
        world[2] + offset[2],
      ];
    }

    if (item.type === "location") {
      return globeWorld(item.data.x_m, item.data.y_m, 1.026);
    }
    return null;
  }

  function markerMeterPoint(item, now = performance.now()) {
    if (item.type === "citizen") {
      return citizenRenderMeters(item.data, now);
    }
    if (item.type === "visitor" || item.type === "location" || item.type === "structure") {
      return [finite(item.data.x_m), finite(item.data.y_m)];
    }
    return [null, null];
  }

  function sharesLocalPoint(a, b, toleranceMeters = 0.5, now = performance.now()) {
    const [ax, ay] = markerMeterPoint(a, now);
    const [bx, by] = markerMeterPoint(b, now);
    if (ax == null || ay == null || bx == null || by == null) return false;
    return Math.hypot(ax - bx, ay - by) <= toleranceMeters;
  }

  function localMarkerWorldOffset(item, now = performance.now()) {
    if (mode !== "local") return [0, 0, 0];

    if (item.type === "citizen") {
      const colocated = markerItems
        .filter(other => other.type === "citizen" && sharesLocalPoint(item, other, 0.5, now))
        .sort((a, b) => String(a.id).localeCompare(String(b.id)));

      if (colocated.length <= 1) return [0, 0, 0];

      const index = colocated.findIndex(other => String(other.id) === String(item.id));
      const hasBodyPilot = colocated.some(other => worldVisualFor(other.id)?.kind === "sprite_body");
      const radiusWorld = hasBodyPilot
        ? clamp(0.24 + (colocated.length * 0.022), 0.28, 0.40)
        : clamp(0.18 + (colocated.length * 0.018), 0.20, 0.31);
      const angle = (-Math.PI / 2) + ((Math.PI * 2 * index) / colocated.length);

      return [
        Math.cos(angle) * radiusWorld,
        0,
        Math.sin(angle) * radiusWorld,
      ];
    }

    if (item.type === "visitor") {
      const citizenCount = markerItems.filter(
        other => other.type === "citizen" && sharesLocalPoint(item, other, 0.5, now)
      ).length;

      if (citizenCount > 0) {
        const citizenRadiusWorld = clamp(0.18 + (citizenCount * 0.018), 0.20, 0.31);
        return [0, 0, citizenRadiusWorld + 0.16];
      }
    }

    return [0, 0, 0];
  }

  function markerPerspectiveScale(item, world, eye) {
    if (mode !== "local" || item.type === "location") return 1;
    const distance = Math.max(0.35, vec3Length(vec3Sub(eye, world)));
    return clamp(4.25 / distance, 0.5, 1.35);
  }

  function updateMarkers(matrix, now = performance.now()) {
    const eye = cameraEye();

    for (const item of markerItems) {
      const world = markerWorld(item, now);
      if (!world) {
        item.element.hidden = true;
        continue;
      }

      if (mode !== "local" && !markerVisibleOnGlobe(world, eye)) {
        item.element.hidden = true;
        continue;
      }

      const projected = project(world, matrix);
      if (!projected) {
        item.element.hidden = true;
        continue;
      }

      const perspectiveScale = markerPerspectiveScale(item, world, eye);
      const visual = item.type === "citizen" ? worldVisualFor(item.id) : null;
      const displayScale = visual?.kind === "sprite_body"
        ? clamp(
            perspectiveScale * Number(visual.presentationScale || 1),
            Number(visual.minReadableScale || 0.5),
            1.35 * Number(visual.presentationScale || 1)
          )
        : perspectiveScale;
      const travelJob = item.type === "citizen" ? activeJobFor(item.data) : null;
      const routeTraveling = String(travelJob?.action || "") === "travel";

      item.element.hidden = false;
      item.element.classList.toggle("route-traveling", routeTraveling);
      item.element.style.setProperty("--marker-scale", displayScale.toFixed(3));
      item.element.style.left = projected.x + "px";
      item.element.style.top = projected.y + "px";
    }
  }

  function renderLocationList() {
    const locations = knownLocations();
    if (!locations.length) {
      locationList.innerHTML = '<div class="truth-note"><p>No authoritative location coordinates are available.</p></div>';
      return;
    }

    locationList.innerHTML = locations.map(loc => {
      const active = selected && selected.type === "location" && String(selected.id) === String(loc.id);
      return '<button class="location-row' + (active ? ' selected' : '') + '" data-location-id="' + escapeHtml(loc.id) + '">' +
        '<strong>' + escapeHtml(loc.name || loc.id) + '</strong>' +
        '<span>x ' + escapeHtml(Number(loc.x_m).toFixed(1)) + ' m • y ' + escapeHtml(Number(loc.y_m).toFixed(1)) + ' m</span>' +
        '</button>';
    }).join("");

    for (const button of locationList.querySelectorAll("[data-location-id]")) {
      button.addEventListener("click", () => selectItem("location", button.dataset.locationId, true));
    }
  }

  function selectedData() {
    if (!selected || !state) return null;
    if (selected.type === "location") return knownLocations().find(loc => String(loc.id) === String(selected.id)) || null;
    if (selected.type === "citizen") return (state.citizens || []).find(row => String(row.id) === String(selected.id)) || null;
    if (selected.type === "structure") return (state.structures || []).find(row => String(row.id) === String(selected.id)) || null;
    if (selected.type === "visitor") return visitorPresence;
    return null;
  }

  function renderSelection() {
    const data = selectedData();
    if (!data) {
      selectionTitle.textContent = "Nothing selected";
      selectionBody.innerHTML = "<p>Select a known marker.</p>";
      return;
    }

    if (selected.type === "location") {
      const deposits = (state.deposits || []).filter(dep => String(dep.location_id) === String(data.id) && dep.discovered);
      selectionTitle.textContent = data.name || data.id;
      selectionBody.innerHTML =
        '<dl class="selection-grid">' +
        '<dt>Local X</dt><dd>' + escapeHtml(Number(data.x_m).toFixed(1)) + ' m</dd>' +
        '<dt>Local Y</dt><dd>' + escapeHtml(Number(data.y_m).toFixed(1)) + ' m</dd>' +
        '<dt>Surveyed</dt><dd>' + (data.surveyed ? "Yes" : "No") + '</dd>' +
        '<dt>Known resources</dt><dd>' + deposits.length + '</dd>' +
        '</dl>' +
        '<p>Planet/Region placement is a magnified presentation of the local tangent frame, not global latitude/longitude.</p>';
      return;
    }

    if (selected.type === "citizen") {
      selectionTitle.textContent = data.name || data.id;
      selectionBody.innerHTML =
        '<dl class="selection-grid">' +
        '<dt>Activity</dt><dd>' + escapeHtml(data.current_activity || "Unknown") + '</dd>' +
        '<dt>Energy</dt><dd>' + escapeHtml(Math.round(Number(data.energy || 0))) + '%</dd>' +
        '<dt>Integrity</dt><dd>' + escapeHtml(Math.round(Number(data.integrity || 0))) + '%</dd>' +
        '<dt>Local X</dt><dd>' + escapeHtml(Number(data.position_x_m || 0).toFixed(1)) + ' m</dd>' +
        '<dt>Local Y</dt><dd>' + escapeHtml(Number(data.position_y_m || 0).toFixed(1)) + ' m</dd>' +
        '</dl>';
      return;
    }

    if (selected.type === "structure") {
      selectionTitle.textContent = data.name || ("Structure #" + data.id);
      selectionBody.innerHTML =
        '<dl class="selection-grid">' +
        '<dt>Kind</dt><dd>' + escapeHtml(titleCase(data.kind || "structure")) + '</dd>' +
        '<dt>Status</dt><dd>' + escapeHtml(titleCase(data.status || "recorded")) + '</dd>' +
        '<dt>Condition</dt><dd>' + escapeHtml(finite(data.condition) == null ? "Unknown" : Number(data.condition).toFixed(1) + "%") + '</dd>' +
        '<dt>Local X</dt><dd>' + escapeHtml(Number(data.x_m || 0).toFixed(1)) + ' m</dd>' +
        '<dt>Local Y</dt><dd>' + escapeHtml(Number(data.y_m || 0).toFixed(1)) + ' m</dd>' +
        '</dl>';
      return;
    }

    if (selected.type === "visitor") {
      selectionTitle.textContent = "Visitor";
      selectionBody.innerHTML =
        '<dl class="selection-grid">' +
        '<dt>Location</dt><dd>' + escapeHtml(data.location_name || data.location_id || "Unknown") + '</dd>' +
        '<dt>Local X</dt><dd>' + escapeHtml(Number(data.x_m || 0).toFixed(1)) + ' m</dd>' +
        '<dt>Local Y</dt><dd>' + escapeHtml(Number(data.y_m || 0).toFixed(1)) + ' m</dd>' +
        '</dl>';
    }
  }

  function findItem(type, id) {
    if (type === "location") return knownLocations().find(row => String(row.id) === String(id)) || null;
    if (type === "citizen") return (state && state.citizens || []).find(row => String(row.id) === String(id)) || null;
    if (type === "structure") return (state && state.structures || []).find(row => String(row.id) === String(id)) || null;
    if (type === "visitor") return visitorPresence;
    return null;
  }

  function selectedWorld() {
    const data = findItem(selected.type, selected.id);
    if (!data) return null;

    if (mode === "local") {
      if (selected.type === "location") return localWorld(data.x_m, data.y_m, 0);
      if (selected.type === "citizen") {
        const [x, y] = citizenRenderMeters(data);
        return x == null || y == null ? null : localWorld(x, y, 0);
      }
      if (selected.type === "structure") return localWorld(data.x_m, data.y_m, 0);
      if (selected.type === "visitor") return localWorld(data.x_m, data.y_m, 0);
    } else if (selected.type === "location") {
      return globeWorld(data.x_m, data.y_m, 1);
    }
    return null;
  }

  function ease(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function animateCamera(next, duration) {
    const ms = reduceMotion.matches ? 0 : (duration || 800);
    if (!ms) {
      camera.yaw = next.yaw == null ? camera.yaw : next.yaw;
      camera.pitch = next.pitch == null ? camera.pitch : next.pitch;
      camera.distance = next.distance == null ? camera.distance : next.distance;
      camera.target = next.target ? [...next.target] : camera.target;
      cameraTween = null;
      return;
    }

    cameraTween = {
      started: performance.now(),
      duration: ms,
      from: {
        yaw: camera.yaw,
        pitch: camera.pitch,
        distance: camera.distance,
        target: [...camera.target],
      },
      to: {
        yaw: next.yaw == null ? camera.yaw : next.yaw,
        pitch: next.pitch == null ? camera.pitch : next.pitch,
        distance: next.distance == null ? camera.distance : next.distance,
        target: next.target ? [...next.target] : [...camera.target],
      },
    };
  }

  function updateTween(now) {
    if (!cameraTween) return;
    const raw = clamp((now - cameraTween.started) / cameraTween.duration, 0, 1);
    const t = ease(raw);
    const from = cameraTween.from;
    const to = cameraTween.to;

    camera.yaw = from.yaw + (to.yaw - from.yaw) * t;
    camera.pitch = from.pitch + (to.pitch - from.pitch) * t;
    camera.distance = from.distance + (to.distance - from.distance) * t;
    camera.target = [
      from.target[0] + (to.target[0] - from.target[0]) * t,
      from.target[1] + (to.target[1] - from.target[1]) * t,
      from.target[2] + (to.target[2] - from.target[2]) * t,
    ];

    if (raw >= 1) cameraTween = null;
  }

  function cameraForGlobePoint(world, distance) {
    const n = vec3Normalize(world);
    return {
      yaw: Math.atan2(n[0], n[2]),
      pitch: Math.asin(clamp(n[1], -1, 1)),
      distance,
      target: [0, 0, 0],
    };
  }

  function focusSelected() {
    const world = selectedWorld();
    if (!world) return;

    if (mode === "planet") {
      animateCamera(cameraForGlobePoint(world, 2.7), 700);
    } else if (mode === "region") {
      animateCamera(cameraForGlobePoint(world, 1.55), 760);
    } else {
      animateCamera({
        target: [world[0], 0, world[2]],
        distance: Math.min(camera.distance, 3.0),
      }, 650);
    }
  }

  function selectItem(type, id, focus) {
    selected = { type, id: String(id) };
    renderSelection();
    renderLocationList();
    refreshMarkerSelection();

    if (embedded && window.parent !== window && type === "citizen") {
      window.parent.postMessage({
        type: "agent-city-world-select",
        entityType: "citizen",
        id: String(id),
      }, window.location.origin);
    }

    if (focus) focusSelected();
  }

  function setMode(nextMode, focus) {
    if (!["planet", "region", "local"].includes(nextMode)) return;
    mode = nextMode;

    for (const button of modeButtons) {
      button.classList.toggle("active", button.dataset.mode === mode);
    }

    if (mode === "planet") {
      modeCaption.textContent = "Planet shell • local frame visually anchored";
      animateCamera({
        yaw: -0.72,
        pitch: 0.34,
        distance: 3.25,
        target: [0, 0, 0],
      }, 900);
    } else if (mode === "region") {
      modeCaption.textContent = "Regional globe focus • known landmarks only";
      const seed = seedLocation();
      const world = globeWorld(seed.x_m, seed.y_m, 1);
      animateCamera(cameraForGlobePoint(world, 1.6), 850);
    } else {
      modeCaption.textContent = localTerrainBuffer
        ? "Seeded terrain mesh • surface loaded"
        : "Seeded terrain mesh • loading surface…";
      const target = selectedWorld() || [0, 0, 0];
      animateCamera({
        yaw: -0.72,
        pitch: 0.72,
        distance: 4.85,
        target: [target[0], 0, target[2]],
      }, 900);
    }

    rebuildMarkers();
    if (focus) focusSelected();
  }

  function resetCamera() {
    if (mode === "planet") {
      animateCamera({ yaw: -0.72, pitch: 0.34, distance: 3.25, target: [0, 0, 0] }, 600);
    } else if (mode === "region") {
      const seed = seedLocation();
      animateCamera(cameraForGlobePoint(globeWorld(seed.x_m, seed.y_m, 1), 1.6), 600);
    } else {
      animateCamera({ yaw: -0.72, pitch: 0.72, distance: 4.85, target: [0, 0, 0] }, 600);
    }
  }

  function updateCanvasSize() {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(canvas.clientWidth * ratio));
    const height = Math.max(1, Math.round(canvas.clientHeight * ratio));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    gl.viewport(0, 0, width, height);
  }

  function renderFrame(now) {
    updateTween(now);
    updateCanvasSize();

    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    const clear = mode === "local" ? localPalette().clear : [0.012, 0.027, 0.039, 1];
    gl.clearColor(clear[0], clear[1], clear[2], clear[3]);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    const matrix = viewProjection();
    if (mode === "local") {
      drawLocal(matrix);
    } else {
      drawSphere(matrix);
    }

    updateMarkers(matrix, now);
    frameHandle = requestAnimationFrame(renderFrame);
  }

  async function fetchWorldState() {
    try {
      const [stateResponse, visitorResponse] = await Promise.all([
        fetch("/api/state", { cache: "no-store" }),
        fetch("/api/visitor/presence?visitor=N7", { cache: "no-store" }),
      ]);

      if (!stateResponse.ok) throw new Error("State endpoint unavailable");
      const nextState = await stateResponse.json();
      const receivedAt = performance.now();
      const priorEstimate = state ? continuousSimMinute(receivedAt) : Number(nextState.sim_minute || 0);
      state = nextState;
      stateClockBaseSimMinute = state.paused
        ? Number(state.sim_minute || 0)
        : Math.max(Number(state.sim_minute || 0), priorEstimate);
      stateClockBaseRealMs = receivedAt;
      visitorPresence = visitorResponse.ok ? await visitorResponse.json() : null;
      document.body.dataset.dayPhase = visualDayPhase(state.sim_minute);

      refreshFrames();
      await refreshLocalTerrain();
      renderLocationList();
      rebuildMarkers();

      if (!findItem(selected.type, selected.id)) {
        selected = { type: "location", id: String(seedLocation().id) };
      }
      renderSelection();

      simTime.textContent = state.sim_label || ("Sim minute " + Number(state.sim_minute || 0));
      connectionPill.textContent = "Live state";
      connectionPill.classList.remove("offline");
      connectionPill.classList.add("online");
    } catch (error) {
      connectionPill.textContent = "State unavailable";
      connectionPill.classList.remove("online");
      connectionPill.classList.add("offline");
      console.error("Planet Lab state refresh failed", error);
    }
  }

  function minCameraDistance() {
    if (mode === "planet") return 1.35;
    if (mode === "region") return 1.18;
    return 0.45;
  }

  function maxCameraDistance() {
    if (mode === "local") return 10.5;
    return 8;
  }

  canvas.addEventListener("contextmenu", event => event.preventDefault());

  canvas.addEventListener("pointerdown", event => {
    dragging = true;
    dragKind = mode === "local" && (event.shiftKey || event.button === 2) ? "pan" : "orbit";
    lastPointer = { x: event.clientX, y: event.clientY };
    canvas.classList.add("dragging");
    canvas.setPointerCapture(event.pointerId);
    cameraTween = null;
  });

  canvas.addEventListener("pointermove", event => {
    if (!dragging) return;
    const dx = event.clientX - lastPointer.x;
    const dy = event.clientY - lastPointer.y;
    lastPointer = { x: event.clientX, y: event.clientY };

    if (dragKind === "pan" && mode === "local") {
      const scale = camera.distance * 0.0024;
      const right = [Math.cos(camera.yaw), 0, -Math.sin(camera.yaw)];
      const forward = [-Math.sin(camera.yaw), 0, -Math.cos(camera.yaw)];
      camera.target[0] += (-dx * right[0] + dy * forward[0]) * scale;
      camera.target[2] += (-dx * right[2] + dy * forward[2]) * scale;
    } else {
      camera.yaw -= dx * 0.006;
      camera.pitch = clamp(camera.pitch + dy * 0.006, -1.34, 1.34);
    }
  });

  const finishDrag = event => {
    dragging = false;
    canvas.classList.remove("dragging");
    try {
      canvas.releasePointerCapture(event.pointerId);
    } catch {
      // Pointer may already have been released by the browser.
    }
  };

  canvas.addEventListener("pointerup", finishDrag);
  canvas.addEventListener("pointercancel", finishDrag);

  canvas.addEventListener("wheel", event => {
    event.preventDefault();
    cameraTween = null;
    const factor = Math.exp(event.deltaY * 0.001);
    camera.distance = clamp(camera.distance * factor, minCameraDistance(), maxCameraDistance());
  }, { passive: false });

  for (const button of modeButtons) {
    button.addEventListener("click", () => setMode(button.dataset.mode, false));
  }

  resetCameraButton.addEventListener("click", resetCamera);

  window.addEventListener("keydown", event => {
    if (event.target && ["INPUT", "TEXTAREA"].includes(event.target.tagName)) return;
    if (event.key === "1") setMode("planet", false);
    if (event.key === "2") setMode("region", false);
    if (event.key === "3") setMode("local", false);
    if (event.key.toLowerCase() === "r") resetCamera();
    if (event.key.toLowerCase() === "f") focusSelected();
  });

  window.addEventListener("resize", updateCanvasSize);

  fetchWorldState().then(() => setMode(initialMode, false));
  window.setInterval(fetchWorldState, 4000);
  frameHandle = requestAnimationFrame(renderFrame);

  window.addEventListener("beforeunload", () => {
    if (frameHandle != null) cancelAnimationFrame(frameHandle);
  });
})();
