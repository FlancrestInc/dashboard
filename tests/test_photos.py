from app.services.photos import PhotoService


def test_photo_service_finds_nested_images(tmp_path):
    nested = tmp_path / "album"
    nested.mkdir()
    (nested / "family.JPG").write_bytes(b"not-really-an-image")
    (tmp_path / "notes.txt").write_text("ignore me")

    payload = PhotoService(tmp_path).payload({"photos": {"enabled": True, "rotation_seconds": 45}})

    assert payload["photos"] == [{"name": "album/family.JPG", "url": "/photos/album/family.JPG"}]


def test_photo_service_caps_large_libraries(tmp_path):
    for index in range(3):
        (tmp_path / f"photo-{index}.jpg").write_bytes(b"image")

    payload = PhotoService(tmp_path, max_photos=2).payload({"photos": {"enabled": True, "rotation_seconds": 45}})

    assert len(payload["photos"]) == 2


def test_photo_payload_includes_display_options(tmp_path):
    (tmp_path / "frame.jpg").write_bytes(b"image")

    payload = PhotoService(tmp_path).payload(
        {
            "photos": {
                "enabled": True,
                "rotation_seconds": 30,
                "display_mode": "both",
                "background_fit": "contain",
                "background_overlay": 35,
                "frame_fit": "cover",
                "show_captions": True,
            }
        }
    )

    assert payload["display_mode"] == "both"
    assert payload["background_fit"] == "contain"
    assert payload["background_overlay"] == 35
    assert payload["frame_fit"] == "cover"
    assert payload["show_captions"] is True


def test_photo_payload_includes_individually_configured_blocks(tmp_path):
    album = tmp_path / "album"
    album.mkdir()
    (album / "trip.jpg").write_bytes(b"image")
    (tmp_path / "portrait.jpg").write_bytes(b"image")

    payload = PhotoService(tmp_path).payload(
        {
            "photos": {"enabled": True, "rotation_seconds": 30},
            "block_instances": [
                {
                    "id": "photos_1",
                    "type": "photos",
                    "enabled": True,
                    "settings": {"source_mode": "static", "static_path": "portrait.jpg", "fit": "contain"},
                },
                {
                    "id": "photos_2",
                    "type": "photos",
                    "enabled": True,
                    "settings": {"source_mode": "folder", "folder": "album", "fit": "cover"},
                },
            ],
        }
    )

    assert payload["blocks"]["photos_1"]["photos"] == [{"name": "portrait.jpg", "url": "/photos/portrait.jpg"}]
    assert payload["blocks"]["photos_1"]["fit"] == "contain"
    assert payload["blocks"]["photos_2"]["photos"] == [{"name": "album/trip.jpg", "url": "/photos/album/trip.jpg"}]
