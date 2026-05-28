const DISPLAY_SIZES = {
  "1920x1080": [1920, 1080],
  "1080x1920": [1080, 1920],
  "2560x1440": [2560, 1440],
  "3840x2160": [3840, 2160],
  "1280x800": [1280, 800],
};
const GRID_PIXEL_SIZE = 16;
const RESIZE_HANDLES = ["n", "e", "s", "w", "ne", "se", "sw", "nw"];

const presetDataElement = document.getElementById("layoutPresetData");
const presetData = JSON.parse((presetDataElement && presetDataElement.textContent) || "{}");
const tabs = document.querySelectorAll("[data-tab]");
const panels = document.querySelectorAll("[data-tab-panel]");
const builder = document.getElementById("layoutBuilder");
const layoutMode = document.getElementById("layoutMode");
const layoutPreset = document.getElementById("layoutPreset");
const displaySize = document.getElementById("layoutDisplaySize");
const widthInput = document.getElementById("layoutWidth");
const heightInput = document.getElementById("layoutHeight");
const orientationInput = document.getElementById("layoutOrientation");
const snapToGrid = document.getElementById("snapToGrid");
const seedButton = document.getElementById("seedCustomLayout");
const blockToggles = document.querySelectorAll("[data-block-toggle]");
const blockInstanceIds = document.getElementById("blockInstanceIds");
const photoBlockConfigs = document.getElementById("photoBlockConfigs");
const cameraBlockConfigs = document.getElementById("cameraBlockConfigs");
const photoBlockCount = document.getElementById("photoBlockCount");
const cameraBlockCount = document.getElementById("cameraBlockCount");
const addPhotoBlock = document.getElementById("addPhotoBlock");
const addCameraBlock = document.getElementById("addCameraBlock");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((item) => item.classList.toggle("active", item === tab));
    panels.forEach((panel) => panel.classList.toggle("active", panel.dataset.tabPanel === tab.dataset.tab));
  });
});

if (displaySize) displaySize.addEventListener("change", () => {
  const size = DISPLAY_SIZES[displaySize.value];
  if (size) {
    widthInput.value = size[0];
    heightInput.value = size[1];
    orientationInput.value = size[1] > size[0] ? "portrait" : "landscape";
  }
  syncDisplayShape();
});

[widthInput, heightInput].forEach((input) => {
  if (input) input.addEventListener("input", syncDisplayShape);
});

if (orientationInput) orientationInput.addEventListener("change", () => {
  const width = Number(widthInput.value) || 1920;
  const height = Number(heightInput.value) || 1080;
  if ((orientationInput.value === "portrait" && width > height) || (orientationInput.value === "landscape" && height > width)) {
    widthInput.value = height;
    heightInput.value = width;
  }
  syncDisplayShape();
});

if (layoutMode) layoutMode.addEventListener("change", () => {
  builder.dataset.mode = layoutMode.value;
});

if (seedButton) seedButton.addEventListener("click", () => {
  const preset = presetData[layoutPreset.value] || presetData.classic;
  if (!builder) return;
  builder.querySelectorAll(".builder-block").forEach((block) => {
    const rect = preset[block.dataset.block] || preset[block.dataset.blockType];
    if (rect) updateBlock(block.dataset.block, { ...rect, z: readRect(block.dataset.block).z });
  });
  layoutMode.value = "custom";
  builder.dataset.mode = "custom";
});

if (builder) builder.querySelectorAll(".builder-block").forEach((block) => {
  block.addEventListener("pointerdown", (event) => startDrag(event, block));
});

blockToggles.forEach((toggle) => {
  toggle.addEventListener("change", () => syncBlockVisibility(toggle.dataset.blockToggle, toggle.checked));
});

document.addEventListener("change", (event) => {
  const toggle = event.target.closest("[data-block-toggle]");
  if (toggle) syncBlockVisibility(toggle.dataset.blockToggle, toggle.checked);
});

document.addEventListener("input", (event) => {
  const layerInput = event.target.closest("[data-layer-input]");
  if (!layerInput) return;
  const blockId = layerInput.dataset.layerInput;
  const rect = readRect(blockId);
  rect.z = Number(layerInput.value) || rect.z;
  updateBlock(blockId, rect);
});

document.addEventListener("click", (event) => {
  const removeButton = event.target.closest("[data-remove-block]");
  if (!removeButton) return;
  removeBlock(removeButton.dataset.removeBlock);
});

if (addPhotoBlock) addPhotoBlock.addEventListener("click", () => addManagedBlock("photos"));
if (addCameraBlock) addCameraBlock.addEventListener("click", () => addManagedBlock("frigate"));

syncDisplayShape();
blockToggles.forEach((toggle) => syncBlockVisibility(toggle.dataset.blockToggle, toggle.checked));
syncManagedCounts();
updateAllBlockDimensions();

function startDrag(event, block) {
  if (layoutMode.value !== "custom") return;
  if (event.target.closest("input, button, select, textarea")) return;
  event.preventDefault();
  block.setPointerCapture(event.pointerId);
  const start = getPointerPercent(event);
  const initial = readRect(block.dataset.block);
  const resizeHandle = event.target.closest("[data-resize-handle]");
  const resizing = resizeHandle ? resizeHandle.dataset.resizeHandle : "";

  function move(moveEvent) {
    const current = getPointerPercent(moveEvent);
    const dx = current.x - start.x;
    const dy = current.y - start.y;
    const rect = resizing
      ? resizedRect(initial, resizing, dx, dy)
      : { ...initial, x: initial.x + dx, y: initial.y + dy };
    updateBlock(block.dataset.block, shouldSnapToGrid() ? snapRect(rect) : clampRect(rect));
  }

  function stop() {
    block.removeEventListener("pointermove", move);
    block.removeEventListener("pointerup", stop);
    block.removeEventListener("pointercancel", stop);
  }

  block.addEventListener("pointermove", move);
  block.addEventListener("pointerup", stop);
  block.addEventListener("pointercancel", stop);
}

function getPointerPercent(event) {
  const bounds = builder.getBoundingClientRect();
  return {
    x: ((event.clientX - bounds.left) / bounds.width) * 100,
    y: ((event.clientY - bounds.top) / bounds.height) * 100,
  };
}

function readRect(block) {
  return {
    x: Number(inputFor(block, "x").value),
    y: Number(inputFor(block, "y").value),
    w: Number(inputFor(block, "w").value),
    h: Number(inputFor(block, "h").value),
    z: Number(inputFor(block, "z").value) || 1,
  };
}

function updateBlock(block, rect) {
  const normalized = clampRect(rect);
  const element = builder.querySelector(`[data-block="${block}"]`);
  if (!element) return;
  element.style.left = `${formatNumber(normalized.x)}%`;
  element.style.top = `${formatNumber(normalized.y)}%`;
  element.style.width = `${formatNumber(normalized.w)}%`;
  element.style.height = `${formatNumber(normalized.h)}%`;
  element.style.zIndex = String(Math.round(normalized.z));
  Object.entries(normalized).forEach(([key, value]) => {
    const input = inputFor(block, key);
    if (input) input.value = key === "z" ? String(Math.round(value)) : formatNumber(value);
  });
  updateBlockDimensions(element, normalized);
}

function clampRect(rect) {
  const w = Math.max(8, Math.min(100, rect.w));
  const h = Math.max(8, Math.min(100, rect.h));
  return {
    x: Math.max(0, Math.min(100 - w, rect.x)),
    y: Math.max(0, Math.min(100 - h, rect.y)),
    w,
    h,
    z: Math.max(1, Math.min(999, Math.round(Number(rect.z) || 1))),
  };
}

function resizedRect(initial, handle, dx, dy) {
  const rect = { ...initial };
  if (handle.indexOf("e") !== -1) rect.w = initial.w + dx;
  if (handle.indexOf("s") !== -1) rect.h = initial.h + dy;
  if (handle.indexOf("w") !== -1) {
    rect.x = initial.x + dx;
    rect.w = initial.w - dx;
  }
  if (handle.indexOf("n") !== -1) {
    rect.y = initial.y + dy;
    rect.h = initial.h - dy;
  }
  return rect;
}

function shouldSnapToGrid() {
  return snapToGrid && snapToGrid.checked;
}

function snapRect(rect) {
  const clamped = clampRect(rect);
  const snapped = {
    x: snapValue(clamped.x, "x"),
    y: snapValue(clamped.y, "y"),
    w: Math.max(8, snapValue(clamped.w, "x")),
    h: Math.max(8, snapValue(clamped.h, "y")),
    z: clamped.z,
  };
  return clampRect(snapped);
}

function snapValue(value, axis) {
  const increment = gridPercent(axis);
  return Math.round(value / increment) * increment;
}

function gridPercent(axis) {
  const bounds = builder.getBoundingClientRect();
  const length = axis === "y" ? bounds.height : bounds.width;
  if (!length) return 1;
  return (GRID_PIXEL_SIZE / length) * 100;
}

function inputFor(block, key) {
  return document.querySelector(`input[name="layout_block_${block}_${key}"]`);
}

function syncDisplayShape() {
  if (!builder) return;
  const shape = displayShape();
  builder.style.setProperty("--builder-aspect", `${shape.width} / ${shape.height}`);
  updateAllBlockDimensions();
}

function formatNumber(value) {
  return Number(value.toFixed(2)).toString();
}

function displayShape() {
  let width = Number(widthInput.value) || 1920;
  let height = Number(heightInput.value) || 1080;
  if (orientationInput && ((orientationInput.value === "portrait" && width > height) || (orientationInput.value === "landscape" && height > width))) {
    [width, height] = [height, width];
  }
  return { width, height };
}

function syncBlockVisibility(block, isVisible) {
  if (!builder) return;
  const element = builder.querySelector(`[data-block="${block}"]`);
  if (element) element.classList.toggle("hidden", !isVisible);
}

function addManagedBlock(type) {
  const container = type === "photos" ? photoBlockConfigs : cameraBlockConfigs;
  if (!container) return;
  const index = nextIndex(type, container);
  const blockId = `${type}_${index}`;
  container.dataset.nextIndex = String(index + 1);
  container.insertAdjacentHTML("beforeend", type === "photos" ? photoConfigHtml(blockId, `Photos ${index}`) : cameraConfigHtml(blockId, `Camera ${index}`));
  addBuilderBlock(blockId, type, type === "photos" ? `Photos ${index}` : `Camera ${index}`);
  appendBlockId(blockId);
  syncManagedCounts();
  layoutMode.value = "custom";
  builder.dataset.mode = "custom";
}

function removeBlock(blockId) {
  const config = document.querySelector(`[data-config-block="${blockId}"]`);
  if (config) config.remove();
  const block = builder ? builder.querySelector(`[data-block="${blockId}"]`) : null;
  if (block) block.remove();
  ["x", "y", "w", "h", "z"].forEach((key) => {
    const input = inputFor(blockId, key);
    if (input) input.remove();
  });
  removeBlockId(blockId);
  syncManagedCounts();
}

function addBuilderBlock(blockId, type, label) {
  const preset = presetData[layoutPreset.value] || presetData.classic;
  const rect = preset[type] || { x: 4, y: 5, w: 24, h: 22 };
  const layer = nextLayer();
  const block = document.createElement("div");
  block.className = "builder-block";
  block.dataset.block = blockId;
  block.dataset.blockType = type;
  block.style.left = `${rect.x}%`;
  block.style.top = `${rect.y}%`;
  block.style.width = `${rect.w}%`;
  block.style.height = `${rect.h}%`;
  block.style.zIndex = String(layer);
  block.innerHTML = `${blockContentsHtml(label, blockId, layer)}`;
  block.addEventListener("pointerdown", (event) => startDrag(event, block));
  if (builder) builder.appendChild(block);
  ["x", "y", "w", "h"].forEach((key) => {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = `layout_block_${blockId}_${key}`;
    input.value = rect[key];
    if (builder) builder.appendChild(input);
  });
  updateBlock(blockId, { ...rect, z: layer });
}

function nextIndex(type, container) {
  const prefix = `${type}_`;
  const existing = Array.from(document.querySelectorAll(`[data-config-type="${type}"]`))
    .map((element) => Number((element.dataset.configBlock || "").replace(prefix, "")))
    .filter((value) => Number.isFinite(value));
  return Math.max(Number(container.dataset.nextIndex || 1), existing.length ? Math.max(...existing) + 1 : 1);
}

function appendBlockId(blockId) {
  if (!blockInstanceIds) return;
  const ids = blockIds();
  if (!ids.includes(blockId)) ids.push(blockId);
  blockInstanceIds.value = ids.join(",");
}

function removeBlockId(blockId) {
  if (!blockInstanceIds) return;
  blockInstanceIds.value = blockIds().filter((id) => id !== blockId).join(",");
}

function blockIds() {
  return ((blockInstanceIds && blockInstanceIds.value) || "").split(",").map((id) => id.trim()).filter(Boolean);
}

function syncManagedCounts() {
  if (photoBlockCount) photoBlockCount.value = String(document.querySelectorAll('[data-config-type="photos"]').length);
  if (cameraBlockCount) cameraBlockCount.value = String(document.querySelectorAll('[data-config-type="frigate"]').length);
}

function updateAllBlockDimensions() {
  if (!builder) return;
  builder.querySelectorAll(".builder-block").forEach((block) => updateBlockDimensions(block, readRect(block.dataset.block)));
}

function updateBlockDimensions(block, rect) {
  const dimensions = block.querySelector(".block-dimensions");
  if (!dimensions) return;
  const bounds = builder.getBoundingClientRect();
  const widthUnits = Math.max(1, Math.round(((rect.w / 100) * bounds.width) / GRID_PIXEL_SIZE));
  const heightUnits = Math.max(1, Math.round(((rect.h / 100) * bounds.height) / GRID_PIXEL_SIZE));
  dimensions.textContent = `${widthUnits} x ${heightUnits}`;
}

function nextLayer() {
  const layers = Array.from(document.querySelectorAll("[data-layer-input]")).map((input) => Number(input.value) || 0);
  return Math.max(0, ...layers) + 1;
}

function blockContentsHtml(label, blockId, layer) {
  return `
    <span class="block-title">${escapeHtml(label)}</span>
    <span class="block-dimensions" aria-live="polite"></span>
    <label class="block-layer-control"><span>Layer</span><input data-layer-input="${escapeAttribute(blockId)}" name="layout_block_${escapeAttribute(blockId)}_z" type="number" min="1" max="999" value="${layer}"></label>
    ${RESIZE_HANDLES.map((handle) => `<i data-resize-handle="${handle}" aria-hidden="true"></i>`).join("")}`;
}

function photoConfigHtml(blockId, label) {
  return `
    <fieldset class="block-config" data-config-block="${blockId}" data-config-type="photos">
      <legend>${escapeHtml(label)}</legend>
      <button class="secondary remove-block" type="button" data-remove-block="${blockId}">Remove</button>
      <input type="hidden" name="block_${blockId}_type" value="photos">
      <div class="form-row">
        <label><span>Label</span><input name="block_${blockId}_label" value="${escapeAttribute(label)}"></label>
        <label class="check"><input type="checkbox" name="block_${blockId}_show_label" checked> Show label</label>
        <label class="check"><input type="checkbox" name="block_${blockId}_enabled" data-block-toggle="${blockId}" checked> Show block</label>
      </div>
      <div class="form-row">
        <label><span>Photo source</span><select name="block_${blockId}_photo_source_mode"><option value="folder">Folder rotation</option><option value="static">Static image</option></select></label>
        <label><span>Fit</span><select name="block_${blockId}_photo_fit"><option value="cover">Cover</option><option value="contain">Contain</option></select></label>
      </div>
      <div class="form-row">
        <label><span>Static image path</span><input name="block_${blockId}_photo_static_path" placeholder="portrait.jpg"></label>
        <label><span>Folder path</span><input name="block_${blockId}_photo_folder" placeholder="album"></label>
      </div>
      <label class="check"><input type="checkbox" name="block_${blockId}_photo_show_captions"> Show captions</label>
    </fieldset>`;
}

function cameraConfigHtml(blockId, label) {
  return `
    <fieldset class="block-config" data-config-block="${blockId}" data-config-type="frigate">
      <legend>${escapeHtml(label)}</legend>
      <button class="secondary remove-block" type="button" data-remove-block="${blockId}">Remove</button>
      <input type="hidden" name="block_${blockId}_type" value="frigate">
      <div class="form-row">
        <label><span>Label</span><input name="block_${blockId}_label" value="${escapeAttribute(label)}"></label>
        <label class="check"><input type="checkbox" name="block_${blockId}_show_label" checked> Show label</label>
        <label class="check"><input type="checkbox" name="block_${blockId}_enabled" data-block-toggle="${blockId}" checked> Show block</label>
      </div>
      <div class="form-row">
        <label><span>Camera name</span><input name="block_${blockId}_camera_name" placeholder="front_door"></label>
        <label><span>Display mode</span><select name="block_${blockId}_display_mode"><option value="snapshot">Snapshot</option><option value="live">Live</option></select></label>
      </div>
      <label><span>Live URL</span><input name="block_${blockId}_live_url" placeholder="Browser-playable go2rtc/MSE/WebRTC URL"></label>
    </fieldset>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}
