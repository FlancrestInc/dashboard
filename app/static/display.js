const state = {
  data: JSON.parse(document.getElementById("initialData").textContent),
  photoIndexes: {},
};

const backgroundLayer = document.getElementById("backgroundLayer");

function preloadPhoto(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(url);
    image.onerror = reject;
    image.src = url;
  });
}

function tickClock() {
  const now = new Date();
  document.querySelectorAll("[data-clock]").forEach((clock) => {
    clock.textContent = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  });
  document.querySelectorAll("[data-date-line]").forEach((dateLine) => {
    dateLine.textContent = now.toLocaleDateString([], {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  });
}

function renderAgendaBlocks(calendar) {
  document.querySelectorAll("[data-agenda-block]").forEach((agendaBlock) => {
    if (!calendar.configured) {
      agendaBlock.innerHTML = `<div class="placeholder">Connect an ICS calendar feed in admin.</div>`;
      return;
    }
    if (calendar.error) {
      agendaBlock.innerHTML = `<div class="placeholder error">${escapeHtml(calendar.error)}</div>`;
      return;
    }
    if (!calendar.events.length) {
      agendaBlock.innerHTML = `<div class="placeholder">No upcoming events found.</div>`;
      return;
    }
    agendaBlock.innerHTML = `<ol class="agenda-list">${calendar.events
      .map((event) => {
        const time = event.all_day === "true" ? "All day" : [event.start_time, event.end_time].filter(Boolean).join(" - ");
        return `<li><div class="event-date">${escapeHtml(event.date)}</div><div><strong>${escapeHtml(
          event.title,
        )}</strong><span>${escapeHtml(time)}</span></div></li>`;
      })
      .join("")}</ol>`;
  });
}

function renderWeatherBlocks(weather) {
  document.querySelectorAll('[data-block="weather"]').forEach((weatherBlock) => {
    const block = layoutBlock(weatherBlock.dataset.blockId);
    if (!weather.configured) {
      weatherBlock.innerHTML = `<div class="placeholder compact">Add latitude and longitude for weather.</div>`;
      return;
    }
    if (weather.error || !weather.current) {
      weatherBlock.innerHTML = `<div class="placeholder compact error">${escapeHtml(weather.error || "Weather unavailable.")}</div>`;
      return;
    }
    const settings = block && block.settings ? block.settings : {};
    const days = Math.max(1, Math.min(7, Number(settings.forecast_days || state.data.settings.weather.forecast_days || 4)));
    const showIcons = settings.show_icons !== false;
    const current = weather.current;
    weatherBlock.innerHTML = `
      ${block && block.show_label ? `<p class="block-label">${escapeHtml(block.label)}</p>` : ""}
      <div class="weather-current">
        ${showIcons ? `<span class="weather-icon" aria-hidden="true">${weatherIcon(current.icon)}</span>` : ""}
        <div>
          <div class="temp">${current.temperature}${escapeHtml(current.unit)}</div>
          <strong>${escapeHtml(current.condition)}</strong>
          <span>Feels like ${current.feels_like}${escapeHtml(current.unit)}</span>
        </div>
      </div>
      <div class="forecast">${weather.forecast
        .slice(1, days)
        .map(
          (day) =>
            `<span>${showIcons ? `<i aria-hidden="true">${weatherIcon(day.icon)}</i>` : ""}${formatShortDay(day.date)} ${day.high}/${day.low}${escapeHtml(day.unit)}</span>`,
        )
        .join("")}</div>`;
  });
}

function renderCameraBlocks(frigate) {
  document.querySelectorAll("[data-camera-block]").forEach((cameraBlock) => {
    const blockElement = cameraBlock.closest("[data-block-id]");
    const blockId = blockElement ? blockElement.dataset.blockId : "";
    const camera = frigate.blocks && frigate.blocks[blockId] ? frigate.blocks[blockId] : frigate;
    if (!camera.configured) {
      cameraBlock.innerHTML = `<div class="placeholder">Configure a camera feed in admin.</div>`;
      return;
    }
    if (camera.error) {
      cameraBlock.innerHTML = `<div class="placeholder error">${escapeHtml(camera.error)} Try snapshot mode if live playback is not browser-compatible.</div>`;
      return;
    }
    if (camera.mode === "live") {
      cameraBlock.innerHTML = `<iframe title="Live camera" src="${escapeAttribute(camera.live_url)}" loading="lazy"></iframe>`;
      return;
    }
    cameraBlock.innerHTML = `<img data-snapshot-image data-snapshot-url="${escapeAttribute(
      camera.snapshot_url,
    )}" alt="Camera snapshot" src="${escapeAttribute(camera.snapshot_url)}&t=${Date.now()}">`;
  });
}

function ensureBackgroundLayers() {
  if (!backgroundLayer) return [];
  if (!backgroundLayer.querySelector("[data-background-photo-layer]")) {
    backgroundLayer.innerHTML = `
      <div class="background-layer__image" data-background-photo-layer="0"></div>
      <div class="background-layer__image" data-background-photo-layer="1"></div>`;
    backgroundLayer.setAttribute("data-active-layer", "1");
  }
  return Array.prototype.slice.call(backgroundLayer.querySelectorAll("[data-background-photo-layer]"));
}

function backgroundImageForPhoto(photo, overlay) {
  return `linear-gradient(90deg, rgba(8, 12, 15, ${overlay + 0.22}), rgba(8, 12, 15, ${overlay})), url("${photo.url}")`;
}

async function crossfadeBackground(photo, fit, overlay) {
  const layers = ensureBackgroundLayers();
  if (!layers.length) return false;
  await preloadPhoto(photo.url);
  const activeLayer = backgroundLayer.getAttribute("data-active-layer") || "1";
  const nextLayer = activeLayer === "0" ? "1" : "0";
  const nextElement = backgroundLayer.querySelector(`[data-background-photo-layer="${nextLayer}"]`);
  const previousElement = backgroundLayer.querySelector(`[data-background-photo-layer="${activeLayer}"]`);
  if (!nextElement) return false;
  backgroundLayer.classList.remove("empty");
  nextElement.style.backgroundSize = fit;
  nextElement.style.backgroundImage = backgroundImageForPhoto(photo, overlay);
  nextElement.classList.add("active");
  if (previousElement) previousElement.classList.remove("active");
  backgroundLayer.setAttribute("data-active-layer", nextLayer);
  return true;
}

async function rotateBackground() {
  const photos = state.data.photos.photos || [];
  if (!backgroundLayer) return;
  const mode = state.data.photos.display_mode || "background";
  if (!state.data.photos.enabled || !photos.length || mode === "frame") {
    ensureBackgroundLayers().forEach((layer) => {
      layer.style.backgroundImage = "";
      layer.classList.remove("active");
    });
    backgroundLayer.classList.add("empty");
    return;
  }
  const index = state.photoIndexes.background || 0;
  const photo = photos[index % photos.length];
  const rawOverlay = state.data.photos.background_overlay == null ? 55 : state.data.photos.background_overlay;
  const overlay = Math.max(0, Math.min(90, Number(rawOverlay))) / 100;
  const fit = state.data.photos.background_fit === "contain" ? "contain" : "cover";
  try {
    const didFade = await crossfadeBackground(photo, fit, overlay);
    if (didFade) state.photoIndexes.background = index + 1;
  } catch (error) {
    return;
  }
}

function frameImageLayer(photo, fit, layer, active) {
  return `<img class="photo-frame__image${active ? " active" : ""}" data-photo-frame-layer="${layer}" alt="${escapeAttribute(
    photo.name,
  )}" src="${escapeAttribute(photo.url)}" style="object-fit: ${fit};">`;
}

function renderPhotoFrameShell(photoFrameBlock, photo, fit, caption) {
  photoFrameBlock.innerHTML = `<figure class="photo-frame" data-active-layer="0">${frameImageLayer(
    photo,
    fit,
    "0",
    true,
  )}${frameImageLayer(photo, fit, "1", false)}<p data-photo-caption${caption ? "" : " hidden"}>${escapeHtml(caption)}</p></figure>`;
}

async function crossfadePhotoFrame(photoFrameBlock, photo, fit, caption) {
  const figure = photoFrameBlock.querySelector(".photo-frame");
  if (!figure) {
    await preloadPhoto(photo.url);
    renderPhotoFrameShell(photoFrameBlock, photo, fit, caption);
    return true;
  }
  await preloadPhoto(photo.url);
  const activeLayer = figure.getAttribute("data-active-layer") || "0";
  const nextLayer = activeLayer === "0" ? "1" : "0";
  const nextImage = figure.querySelector(`[data-photo-frame-layer="${nextLayer}"]`);
  const previousImage = figure.querySelector(`[data-photo-frame-layer="${activeLayer}"]`);
  if (!nextImage) return false;
  nextImage.alt = photo.name;
  nextImage.src = photo.url;
  nextImage.style.objectFit = fit;
  nextImage.classList.add("active");
  if (previousImage) previousImage.classList.remove("active");
  figure.setAttribute("data-active-layer", nextLayer);
  const captionElement = figure.querySelector("[data-photo-caption]");
  if (captionElement) {
    captionElement.textContent = caption;
    captionElement.hidden = !caption;
  }
  return true;
}

function renderPhotoFrames(advance = false) {
  document.querySelectorAll("[data-photo-frame-block]").forEach((photoFrameBlock) => {
    const blockElement = photoFrameBlock.closest("[data-block-id]");
    const blockId = blockElement ? blockElement.dataset.blockId : "";
    const photoConfig = state.data.photos.blocks && state.data.photos.blocks[blockId] ? state.data.photos.blocks[blockId] : state.data.photos;
    const photos = photoConfig.photos || [];
    const mode = state.data.photos.display_mode || "background";
    if (!photoConfig.enabled || !photos.length || mode === "background") {
      photoFrameBlock.innerHTML = `<div class="placeholder">Configure photos in admin.</div>`;
      return;
    }
    const index = state.photoIndexes[blockId] || 0;
    const photo = photos[index % photos.length];
    const fit = photoConfig.fit || state.data.photos.frame_fit || "cover";
    const caption = photoConfig.show_captions ? photo.name : "";
    crossfadePhotoFrame(photoFrameBlock, photo, fit, caption)
      .then((didFade) => {
        if (advance && didFade) state.photoIndexes[blockId] = index + 1;
      })
      .catch(() => {});
  });
}

function rotatePhotos() {
  renderPhotoFrames(true);
  rotateBackground();
}

function refreshSnapshot() {
  document.querySelectorAll("[data-snapshot-image]").forEach((img) => {
    if (img.dataset.snapshotUrl) {
      img.src = `${img.dataset.snapshotUrl}&t=${Date.now()}`;
    }
  });
}

async function refreshData() {
  try {
    const response = await fetch("/api/display-data", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.data = await response.json();
    renderAll();
  } catch (error) {
    document.querySelectorAll("[data-agenda-block]").forEach((agendaBlock) => {
      agendaBlock.innerHTML = `<div class="placeholder error">Dashboard data refresh failed.</div>`;
    });
  }
}

function renderAll() {
  renderAgendaBlocks(state.data.calendar);
  renderWeatherBlocks(state.data.weather);
  renderCameraBlocks(state.data.frigate);
  renderPhotoFrames(false);
  rotateBackground();
}

function layoutBlock(blockId) {
  return state.data.layout.blocks.find((block) => block.id === blockId);
}

function formatShortDay(raw) {
  return new Date(`${raw}T12:00:00`).toLocaleDateString([], { weekday: "short" });
}

function weatherIcon(icon) {
  return (
    {
      sun: "☀",
      "cloud-sun": "◐",
      cloud: "☁",
      "cloud-fog": "≋",
      "cloud-drizzle": "▥",
      "cloud-rain": "☂",
      "cloud-snow": "✻",
      "cloud-lightning": "⚡",
    }[icon] || "☁"
  );
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

tickClock();
renderAll();
setInterval(tickClock, 1000);
setInterval(refreshData, 5 * 60 * 1000);
setInterval(rotatePhotos, Math.max(10, Number(state.data.photos.rotation_seconds || 45)) * 1000);
setInterval(refreshSnapshot, Math.max(5, Number(state.data.settings.frigate.snapshot_refresh_seconds || 10)) * 1000);
