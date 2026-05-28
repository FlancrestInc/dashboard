# Dashboard Layout Configuration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add display-size-aware dashboard layouts, a tabbed admin layout builder, and configurable photo background/frame display.

**Architecture:** Keep the app server-rendered and settings-driven. Add focused layout normalization helpers in `app/settings.py`, render blocks as positioned dashboard regions in `display.html`, and add lightweight vanilla JavaScript for admin tabs and drag/resize layout editing.

**Tech Stack:** FastAPI, Jinja2 templates, SQLite-backed JSON settings, vanilla CSS and JavaScript, pytest.

---

## Chunk 1: Settings And Layout Model

### Task 1: Add Layout Defaults And Normalization

**Files:**
- Modify: `app/settings.py`
- Test: `tests/test_settings.py`

- [ ] Add layout constants for allowed presets, display sizes, block IDs, and default custom rectangles.
- [ ] Extend `DEFAULT_SETTINGS` with `layout` and expanded `photos` options.
- [ ] Add helpers that normalize layout mode, preset, dimensions, orientation, display size, and custom block rectangles.
- [ ] Keep `layout_preset` synchronized with `layout.preset` for legacy compatibility.
- [ ] Write tests for defaults, invalid fallback, and custom geometry clamping.
- [ ] Run: `pytest tests/test_settings.py -v`

## Chunk 2: Display Rendering

### Task 2: Render Positioned Blocks And Photo Frame

**Files:**
- Modify: `app/settings.py`
- Modify: `app/templates/display.html`
- Modify: `app/static/display.js`
- Modify: `app/static/styles.css`
- Test: `tests/test_photos.py`

- [ ] Add a `layout_for_display(settings)` helper that returns active block rectangles for preset or custom mode.
- [ ] Pass layout data into `display.html` through existing settings payload.
- [ ] Replace the fixed display grid with block regions for clock, weather, calendar, Frigate, and photos.
- [ ] Update `display.js` to render a rotating photo frame block and respect background/photo display modes.
- [ ] Update display CSS for landscape, portrait, and positioned block rendering.
- [ ] Run: `pytest tests/test_settings.py tests/test_photos.py -v`

## Chunk 3: Tabbed Admin And Builder

### Task 3: Add Settings Tabs And Visual Builder

**Files:**
- Modify: `app/templates/admin.html`
- Modify: `app/static/styles.css`
- Create: `app/static/admin.js`
- Modify: `app/templates/base.html`

- [ ] Restructure the admin form into Board, Layout, Photos, and Data Sources tabs, with block visibility controls in Layout.
- [ ] Add layout controls for mode, preset, display size, width, height, and orientation.
- [ ] Add a scaled preview canvas with draggable/resizable blocks and hidden percentage inputs.
- [ ] Add photo controls for background/frame mode, fit, overlay, and captions.
- [ ] Add CSS for tabs, builder canvas, selected block states, and responsive admin layout.
- [ ] Load `admin.js` only on the admin page.

## Chunk 4: Verification And Documentation

### Task 4: Verify End To End

**Files:**
- Modify: `README.md`

- [ ] Update README settings documentation to describe layout presets, custom builder, display sizes, and photo frame options.
- [ ] Run: `pytest -v`
- [ ] Start the app with `uvicorn app.main:app --reload` if dependencies are installed.
- [ ] Manually verify `/admin` renders tabs and `/display` renders the selected layout.
