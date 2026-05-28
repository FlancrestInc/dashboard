from pathlib import Path


def test_admin_checkboxes_have_explicit_uniform_dimensions():
    styles = Path("app/static/styles.css").read_text()

    assert 'input[type="checkbox"]' in styles
    assert "width: 44px;" in styles
    assert "height: 44px;" in styles
