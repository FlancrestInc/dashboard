from app.services.frigate import FrigateService


def test_frigate_status_includes_individually_configured_camera_blocks():
    status = FrigateService().status(
        {
            "frigate": {"enabled": True, "base_url": "http://frigate:5000", "snapshot_refresh_seconds": 12},
            "block_instances": [
                {
                    "id": "frigate_1",
                    "type": "frigate",
                    "enabled": True,
                    "settings": {"camera_name": "front", "display_mode": "snapshot", "live_url": ""},
                },
                {
                    "id": "frigate_2",
                    "type": "frigate",
                    "enabled": True,
                    "settings": {"camera_name": "garage", "display_mode": "live", "live_url": "http://camera/live"},
                },
            ],
        }
    )

    assert status["blocks"]["frigate_1"]["snapshot_url"] == "/api/frigate/snapshot?camera=front"
    assert status["blocks"]["frigate_1"]["refresh_seconds"] == 12
    assert status["blocks"]["frigate_2"]["mode"] == "live"
    assert status["blocks"]["frigate_2"]["live_url"] == "http://camera/live"
