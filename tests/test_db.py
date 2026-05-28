from app.db import SettingsStore


def test_settings_persist(tmp_path):
    path = tmp_path / "dashboard.sqlite3"
    store = SettingsStore(path)
    settings = store.get_settings()
    settings["board_title"] = "Persistent Home"
    store.save_settings(settings)

    reloaded = SettingsStore(path).get_settings()

    assert reloaded["board_title"] == "Persistent Home"
