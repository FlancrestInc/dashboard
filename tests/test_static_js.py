from pathlib import Path


def test_dashboard_javascript_avoids_optional_chaining_for_browser_compatibility():
    for path in [Path("app/static/display.js"), Path("app/static/admin.js")]:
        source = path.read_text()

        assert "?." not in source
        assert "??" not in source


def test_layout_builder_snap_grid_uses_one_consistent_increment():
    script = Path("app/static/admin.js").read_text()
    template = Path("app/templates/admin.html").read_text()
    styles = Path("app/static/styles.css").read_text()

    assert "const GRID_PIXEL_SIZE = 16;" in script
    assert 'id="snapToGrid"' in template
    assert "snapRect(" in script
    assert "--builder-grid-size: 16px;" in styles
    assert "background-size: var(--builder-grid-size) var(--builder-grid-size);" in styles


def test_layout_builder_has_full_resize_handles_dimensions_layers_and_saved_layouts():
    script = Path("app/static/admin.js").read_text()
    template = Path("app/templates/admin.html").read_text()

    for handle in ["n", "e", "s", "w", "ne", "se", "sw", "nw"]:
        assert f'data-resize-handle="{handle}"' in template or f'handle: "{handle}"' in script
    assert 'class="block-dimensions"' in template
    assert "updateBlockDimensions(" in script
    assert 'name="layout_block_{{ block.id }}_z"' in template
    assert 'id="layoutSavedLayouts"' in template
    assert 'name="layout_action" value="load_saved"' in template
    assert 'name="layout_action" value="save_current"' in template
    assert 'name="layout_action" value="save_new"' in template


def test_photo_rotation_preloads_images_before_crossfading():
    script = Path("app/static/display.js").read_text()

    assert "function preloadPhoto(" in script
    assert "new Image()" in script
    assert "crossfadeBackground(" in script
    assert "data-active-layer" in script
    assert 'classList.add("active")' in script


def test_photo_layers_are_stacked_and_fade_between_active_states():
    styles = Path("app/static/styles.css").read_text()

    assert ".background-layer__image" in styles
    assert ".background-layer__image.active" in styles
    assert ".photo-frame__image" in styles
    assert ".photo-frame__image.active" in styles
    assert "transition: opacity" in styles


def test_display_renders_grouped_agenda_and_glanceable_weather_cards():
    script = Path("app/static/display.js").read_text()
    styles = Path("app/static/styles.css").read_text()

    assert "groupEventsByDate(" in script
    assert "agenda-day" in script
    assert "agenda-event" in script
    assert "weather-forecast-strip" in script
    assert "weather-day-card" in script
    assert ".agenda-day" in styles
    assert ".agenda-event" in styles
    assert ".weather-day-card" in styles
