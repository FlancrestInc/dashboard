from app.settings import default_settings, layout_for_display, merge_settings, settings_from_form


def test_form_settings_normalize_values():
    settings = settings_from_form(
        {
            "board_title": " Kitchen ",
            "layout_preset": "camera",
            "weather_enabled": "on",
            "weather_latitude": "39.7392",
            "weather_longitude": "-104.9903",
            "weather_temperature_unit": "celsius",
            "calendar_timezone": "America/Chicago",
            "calendar_max_events": "9",
            "photos_rotation_seconds": "3",
            "frigate_display_mode": "bad-mode",
            "block_clock": "on",
        }
    )

    assert settings["board_title"] == "Kitchen"
    assert settings["layout_preset"] == "camera"
    assert settings["weather"]["temperature_unit"] == "celsius"
    assert settings["calendar"]["timezone"] == "America/Chicago"
    assert settings["calendar"]["max_events"] == 9
    assert settings["photos"]["rotation_seconds"] == 10
    assert settings["frigate"]["display_mode"] == "snapshot"
    assert settings["blocks"]["clock"] is True
    assert settings["blocks"]["weather"] is False


def test_merge_settings_keeps_new_defaults():
    merged = merge_settings({"board_title": "Existing", "weather": {"latitude": "1"}})
    defaults = default_settings()

    assert merged["board_title"] == "Existing"
    assert merged["weather"]["latitude"] == "1"
    assert merged["weather"]["temperature_unit"] == defaults["weather"]["temperature_unit"]
    assert "frigate" in merged


def test_default_settings_include_display_layout_and_photo_modes():
    settings = default_settings()

    assert settings["layout"]["mode"] == "preset"
    assert settings["layout"]["preset"] == "classic"
    assert settings["layout"]["display_size"] == "1920x1080"
    assert settings["layout"]["width"] == 1920
    assert settings["layout"]["height"] == 1080
    assert settings["layout"]["orientation"] == "landscape"
    assert settings["photos"]["display_mode"] == "background"
    assert settings["photos"]["background_overlay"] == 55


def test_form_settings_normalizes_layout_and_photo_options():
    settings = settings_from_form(
        {
            "layout_mode": "custom",
            "layout_preset": "portrait",
            "layout_display_size": "custom",
            "layout_width": "1080",
            "layout_height": "1920",
            "layout_orientation": "portrait",
            "layout_block_clock_x": "-10",
            "layout_block_clock_y": "5.5",
            "layout_block_clock_w": "150",
            "layout_block_clock_h": "2",
            "layout_block_calendar_x": "20",
            "layout_block_calendar_y": "30",
            "layout_block_calendar_w": "40",
            "layout_block_calendar_h": "50",
            "photos_display_mode": "both",
            "photos_background_fit": "contain",
            "photos_background_overlay": "110",
            "photos_frame_fit": "bad-fit",
            "photos_show_captions": "on",
        }
    )

    assert settings["layout_preset"] == "portrait"
    assert settings["layout"]["mode"] == "custom"
    assert settings["layout"]["preset"] == "portrait"
    assert settings["layout"]["display_size"] == "custom"
    assert settings["layout"]["width"] == 1080
    assert settings["layout"]["height"] == 1920
    assert settings["layout"]["orientation"] == "portrait"
    assert settings["layout"]["custom_blocks"]["clock"] == {"x": 0, "y": 5.5, "w": 100, "h": 8, "z": 1}
    assert settings["layout"]["custom_blocks"]["calendar"] == {"x": 20, "y": 30, "w": 40, "h": 50, "z": 3}
    assert settings["photos"]["display_mode"] == "both"
    assert settings["photos"]["background_fit"] == "contain"
    assert settings["photos"]["background_overlay"] == 90
    assert settings["photos"]["frame_fit"] == "cover"
    assert settings["photos"]["show_captions"] is True


def test_form_settings_applies_orientation_to_display_size():
    settings = settings_from_form(
        {
            "layout_display_size": "1920x1080",
            "layout_width": "1920",
            "layout_height": "1080",
            "layout_orientation": "portrait",
        }
    )

    assert settings["layout"]["width"] == 1080
    assert settings["layout"]["height"] == 1920
    assert settings["layout"]["orientation"] == "portrait"


def test_layout_for_display_uses_custom_blocks_and_enabled_blocks():
    settings = merge_settings(
        {
            "layout": {
                "mode": "custom",
                "custom_blocks": {
                    "clock": {"x": 0, "y": 0, "w": 40, "h": 20},
                    "calendar": {"x": 0, "y": 20, "w": 40, "h": 80},
                    "frigate": {"x": 40, "y": 0, "w": 60, "h": 100},
                },
            },
            "blocks": {"weather": False, "photos": False},
        }
    )

    layout = layout_for_display(settings)

    assert layout["mode"] == "custom"
    assert [block["id"] for block in layout["blocks"]] == ["clock", "calendar", "frigate"]
    assert layout["blocks"][0]["style"] == "left: 0%; top: 0%; width: 40%; height: 20%; z-index: 1;"


def test_form_settings_normalizes_layout_block_layer_and_display_style():
    settings = settings_from_form(
        {
            "layout_mode": "custom",
            "layout_block_clock_x": "10",
            "layout_block_clock_y": "12",
            "layout_block_clock_w": "30",
            "layout_block_clock_h": "20",
            "layout_block_clock_z": "12",
            "block_clock_enabled": "on",
            "block_clock_type": "clock",
            "block_clock_label": "Clock",
        }
    )

    assert settings["layout"]["custom_blocks"]["clock"]["z"] == 12
    layout = layout_for_display(settings)
    assert "z-index: 12;" in layout["blocks"][0]["style"]


def test_form_settings_saves_loads_and_updates_named_layouts():
    saved_layouts_json = (
        '[{"id":"morning","name":"Morning","blocks":{"clock":{"x":5,"y":5,"w":25,"h":15,"z":4}}}]'
    )

    created = settings_from_form(
        {
            "layout_saved_layouts": saved_layouts_json,
            "layout_action": "save_new",
            "layout_saved_name": "Movie Night",
            "layout_block_clock_x": "20",
            "layout_block_clock_y": "25",
            "layout_block_clock_w": "30",
            "layout_block_clock_h": "35",
            "layout_block_clock_z": "7",
        }
    )
    assert [layout["name"] for layout in created["layout"]["saved_layouts"]] == ["Morning", "Movie Night"]
    assert created["layout"]["saved_layouts"][1]["blocks"]["clock"]["z"] == 7

    loaded = settings_from_form(
        {
            "layout_saved_layouts": saved_layouts_json,
            "layout_action": "load_saved",
            "layout_saved_id": "morning",
            "layout_block_clock_x": "20",
            "layout_block_clock_y": "25",
            "layout_block_clock_w": "30",
            "layout_block_clock_h": "35",
            "layout_block_clock_z": "7",
        }
    )
    assert loaded["layout"]["mode"] == "custom"
    assert loaded["layout"]["custom_blocks"]["clock"] == {"x": 5, "y": 5, "w": 25, "h": 15, "z": 4}

    updated = settings_from_form(
        {
            "layout_saved_layouts": saved_layouts_json,
            "layout_action": "save_current",
            "layout_saved_id": "morning",
            "layout_block_clock_x": "40",
            "layout_block_clock_y": "45",
            "layout_block_clock_w": "20",
            "layout_block_clock_h": "20",
            "layout_block_clock_z": "2",
        }
    )
    assert updated["layout"]["saved_layouts"][0]["blocks"]["clock"] == {"x": 40, "y": 45, "w": 20, "h": 20, "z": 2}


def test_merge_settings_migrates_legacy_blocks_to_configurable_instances():
    settings = merge_settings(
        {
            "blocks": {"clock": True, "weather": True, "calendar": False, "photos": True, "frigate": False},
            "weather": {"label": "Patio", "forecast_days": 6, "show_icons": False},
        }
    )

    instances = {block["id"]: block for block in settings["block_instances"]}

    assert list(instances) == ["clock", "weather", "calendar", "frigate", "photos"]
    assert instances["clock"]["label"] == "Home Base"
    assert instances["clock"]["show_label"] is True
    assert instances["weather"]["label"] == "Patio"
    assert instances["weather"]["enabled"] is True
    assert instances["weather"]["settings"]["forecast_days"] == 6
    assert instances["weather"]["settings"]["show_icons"] is False
    assert instances["calendar"]["enabled"] is False
    assert instances["photos"]["settings"]["source_mode"] == "folder"
    assert instances["frigate"]["settings"]["camera_name"] == ""


def test_form_settings_accepts_multiple_configurable_photo_and_camera_blocks():
    settings = settings_from_form(
        {
            "board_title": "Kitchen",
            "block_instance_ids": "clock,weather,photos_1,photos_2,frigate_1,frigate_2",
            "block_clock_type": "clock",
            "block_clock_enabled": "on",
            "block_clock_label": "Now",
            "block_clock_show_label": "",
            "block_weather_type": "weather",
            "block_weather_enabled": "on",
            "block_weather_label": "Outside",
            "block_weather_show_label": "on",
            "block_weather_forecast_days": "7",
            "block_weather_show_icons": "on",
            "block_photos_1_type": "photos",
            "block_photos_1_enabled": "on",
            "block_photos_1_label": "Family",
            "block_photos_1_show_label": "on",
            "block_photos_1_photo_source_mode": "static",
            "block_photos_1_photo_static_path": "portraits/may.jpg",
            "block_photos_1_photo_folder": "",
            "block_photos_2_type": "photos",
            "block_photos_2_enabled": "on",
            "block_photos_2_label": "Trips",
            "block_photos_2_show_label": "",
            "block_photos_2_photo_source_mode": "folder",
            "block_photos_2_photo_folder": "vacation",
            "block_frigate_1_type": "frigate",
            "block_frigate_1_enabled": "on",
            "block_frigate_1_label": "Front",
            "block_frigate_1_show_label": "on",
            "block_frigate_1_camera_name": "front_door",
            "block_frigate_1_display_mode": "snapshot",
            "block_frigate_2_type": "frigate",
            "block_frigate_2_enabled": "on",
            "block_frigate_2_label": "Garage",
            "block_frigate_2_camera_name": "garage",
            "block_frigate_2_display_mode": "live",
            "block_frigate_2_live_url": "http://camera.local/live",
            "layout_block_photos_2_x": "90",
            "layout_block_photos_2_y": "90",
            "layout_block_photos_2_w": "40",
            "layout_block_photos_2_h": "40",
        }
    )

    instances = {block["id"]: block for block in settings["block_instances"]}

    assert instances["clock"]["show_label"] is False
    assert instances["weather"]["settings"] == {"forecast_days": 7, "show_icons": True}
    assert instances["photos_1"]["settings"]["source_mode"] == "static"
    assert instances["photos_1"]["settings"]["static_path"] == "portraits/may.jpg"
    assert instances["photos_2"]["show_label"] is False
    assert instances["photos_2"]["settings"]["folder"] == "vacation"
    assert instances["frigate_1"]["settings"]["camera_name"] == "front_door"
    assert instances["frigate_2"]["settings"]["display_mode"] == "live"
    assert instances["frigate_2"]["settings"]["live_url"] == "http://camera.local/live"
    assert settings["layout"]["custom_blocks"]["photos_2"] == {"x": 60, "y": 60, "w": 40, "h": 40, "z": 5}


def test_layout_for_display_returns_repeated_instances_with_labels():
    settings = merge_settings(
        {
            "layout": {
                "mode": "custom",
                "custom_blocks": {
                    "photos_1": {"x": 0, "y": 0, "w": 30, "h": 40},
                    "photos_2": {"x": 30, "y": 0, "w": 30, "h": 40},
                },
            },
            "block_instances": [
                {"id": "photos_1", "type": "photos", "enabled": True, "label": "One", "show_label": True},
                {"id": "photos_2", "type": "photos", "enabled": True, "label": "Two", "show_label": False},
            ],
        }
    )

    layout = layout_for_display(settings)

    assert [block["id"] for block in layout["blocks"]] == ["photos_1", "photos_2"]
    assert [block["type"] for block in layout["blocks"]] == ["photos", "photos"]
    assert layout["blocks"][0]["label"] == "One"
    assert layout["blocks"][1]["show_label"] is False


def test_admin_block_instances_default_to_one_photo_and_one_camera():
    from app.settings import admin_block_instances

    blocks = admin_block_instances(default_settings())
    photo_blocks = [block for block in blocks if block["type"] == "photos"]
    camera_blocks = [block for block in blocks if block["type"] == "frigate"]

    assert [block["id"] for block in photo_blocks] == ["photos"]
    assert [block["id"] for block in camera_blocks] == ["frigate"]


def test_form_settings_allows_arbitrary_photo_and_camera_blocks_from_counts():
    settings = settings_from_form(
        {
            "board_title": "Kitchen",
            "photo_block_count": "3",
            "camera_block_count": "2",
            "block_clock_enabled": "on",
            "block_clock_type": "clock",
            "block_clock_label": "Clock",
            "block_clock_show_label": "on",
            "block_weather_enabled": "on",
            "block_weather_type": "weather",
            "block_weather_label": "Weather",
            "block_weather_show_label": "on",
            "block_calendar_enabled": "on",
            "block_calendar_type": "calendar",
            "block_calendar_label": "Agenda",
            "block_calendar_show_label": "on",
            "block_photos_1_enabled": "on",
            "block_photos_1_type": "photos",
            "block_photos_1_label": "Family",
            "block_photos_1_show_label": "on",
            "block_photos_1_photo_source_mode": "folder",
            "block_photos_1_photo_folder": "family",
            "block_photos_2_enabled": "on",
            "block_photos_2_type": "photos",
            "block_photos_2_label": "Trips",
            "block_photos_2_photo_source_mode": "static",
            "block_photos_2_photo_static_path": "trips.jpg",
            "block_photos_3_enabled": "on",
            "block_photos_3_type": "photos",
            "block_photos_3_label": "Pets",
            "block_frigate_1_enabled": "on",
            "block_frigate_1_type": "frigate",
            "block_frigate_1_label": "Front",
            "block_frigate_1_camera_name": "front",
            "block_frigate_2_enabled": "on",
            "block_frigate_2_type": "frigate",
            "block_frigate_2_label": "Garage",
            "block_frigate_2_camera_name": "garage",
        }
    )

    instances = {block["id"]: block for block in settings["block_instances"]}

    assert [block["id"] for block in settings["block_instances"]] == [
        "clock",
        "weather",
        "calendar",
        "photos_1",
        "photos_2",
        "photos_3",
        "frigate_1",
        "frigate_2",
    ]
    assert instances["photos_1"]["settings"]["folder"] == "family"
    assert instances["photos_2"]["settings"]["source_mode"] == "static"
    assert instances["photos_3"]["label"] == "Pets"
    assert instances["frigate_1"]["settings"]["camera_name"] == "front"
    assert instances["frigate_2"]["settings"]["camera_name"] == "garage"
