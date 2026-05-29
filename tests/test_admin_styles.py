from pathlib import Path


def test_admin_checkboxes_have_explicit_uniform_dimensions():
    styles = Path("app/static/styles.css").read_text()

    assert 'input[type="checkbox"]' in styles
    assert "width: 44px;" in styles
    assert "height: 44px;" in styles


def test_display_clock_scales_contents_to_its_block():
    styles = Path("app/static/styles.css").read_text()

    assert ".clock-panel" in styles
    assert ".clock-panel .kicker" in styles
    assert "min(18cqw, 16cqh)" in styles
    assert ".date-line" in styles
    assert "min(9cqw, 12cqh)" in styles


def test_camera_panels_use_minimal_bezels_and_labels():
    styles = Path("app/static/styles.css").read_text()

    assert ".camera-panel {" in styles
    assert "padding: 0;" in styles
    assert ".camera-panel h2" in styles
    assert "margin: 0 0 clamp(4px, 0.9cqh, 8px);" in styles
    assert "font-size: clamp(0.62rem, min(2.8cqw, 2.6cqh), 0.82rem);" in styles


def test_live_camera_viewport_clips_and_scales_embedded_feed():
    styles = Path("app/static/styles.css").read_text()

    assert ".camera-live-viewport {" in styles
    assert "overflow: hidden;" in styles
    assert ".camera-live-image," in styles
    assert ".camera-live-frame {" in styles
    assert "object-fit: contain;" in styles
    assert "pointer-events: none;" in styles
    assert "width: 1920px;" not in styles
    assert "height: 1080px;" not in styles


def test_builder_block_dimension_badge_stays_clear_of_layer_picker():
    styles = Path("app/static/styles.css").read_text()

    assert ".block-dimensions {" in styles
    assert "top: 5px;" in styles
    assert ".block-layer-control {" in styles
    assert "bottom: 5px;" in styles
