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
    assert "padding: clamp(4px, min(1.2cqw, 1.4cqh), 10px);" in styles
    assert ".camera-panel h2" in styles
    assert "margin: 0 0 clamp(4px, 0.9cqh, 8px);" in styles
    assert "font-size: clamp(0.62rem, min(2.8cqw, 2.6cqh), 0.82rem);" in styles
