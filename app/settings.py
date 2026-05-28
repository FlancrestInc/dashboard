from __future__ import annotations

import json
from copy import deepcopy
from typing import Any


LAYOUT_PRESETS = {"classic", "focus", "camera", "portrait", "photo-frame", "dense"}
LAYOUT_MODES = {"preset", "custom"}
ORIENTATIONS = {"landscape", "portrait"}
DISPLAY_SIZES = {
    "1920x1080": (1920, 1080),
    "1080x1920": (1080, 1920),
    "2560x1440": (2560, 1440),
    "3840x2160": (3840, 2160),
    "1280x800": (1280, 800),
    "custom": (1920, 1080),
}
LAYOUT_BLOCKS = ("clock", "weather", "calendar", "frigate", "photos")
BLOCK_TYPES = {"clock", "weather", "calendar", "frigate", "photos"}
MIN_BLOCK_SIZE = 8
MAX_BLOCK_INSTANCES = 100
MAX_SAVED_LAYOUTS = 50

PRESET_LAYOUTS: dict[str, dict[str, dict[str, float]]] = {
    "classic": {
        "clock": {"x": 4, "y": 5, "w": 48, "h": 22},
        "weather": {"x": 72, "y": 5, "w": 24, "h": 22},
        "calendar": {"x": 4, "y": 34, "w": 42, "h": 58},
        "frigate": {"x": 49, "y": 34, "w": 47, "h": 58},
        "photos": {"x": 49, "y": 34, "w": 47, "h": 58},
    },
    "focus": {
        "clock": {"x": 4, "y": 5, "w": 38, "h": 20},
        "weather": {"x": 73, "y": 5, "w": 23, "h": 20},
        "calendar": {"x": 4, "y": 30, "w": 55, "h": 63},
        "frigate": {"x": 62, "y": 30, "w": 34, "h": 63},
        "photos": {"x": 62, "y": 30, "w": 34, "h": 63},
    },
    "camera": {
        "clock": {"x": 4, "y": 5, "w": 34, "h": 20},
        "weather": {"x": 4, "y": 29, "w": 25, "h": 24},
        "calendar": {"x": 4, "y": 57, "w": 25, "h": 36},
        "frigate": {"x": 33, "y": 5, "w": 63, "h": 88},
        "photos": {"x": 33, "y": 5, "w": 63, "h": 88},
    },
    "portrait": {
        "clock": {"x": 6, "y": 3, "w": 88, "h": 15},
        "weather": {"x": 6, "y": 20, "w": 88, "h": 16},
        "calendar": {"x": 6, "y": 38, "w": 88, "h": 31},
        "frigate": {"x": 6, "y": 71, "w": 88, "h": 26},
        "photos": {"x": 6, "y": 71, "w": 88, "h": 26},
    },
    "photo-frame": {
        "clock": {"x": 4, "y": 5, "w": 34, "h": 20},
        "weather": {"x": 4, "y": 29, "w": 34, "h": 22},
        "calendar": {"x": 4, "y": 55, "w": 34, "h": 38},
        "photos": {"x": 42, "y": 5, "w": 54, "h": 88},
        "frigate": {"x": 42, "y": 5, "w": 54, "h": 88},
    },
    "dense": {
        "clock": {"x": 3, "y": 4, "w": 30, "h": 20},
        "weather": {"x": 35, "y": 4, "w": 28, "h": 20},
        "photos": {"x": 65, "y": 4, "w": 32, "h": 20},
        "calendar": {"x": 3, "y": 28, "w": 46, "h": 68},
        "frigate": {"x": 51, "y": 28, "w": 46, "h": 68},
    },
}


def _default_block_instances() -> list[dict[str, Any]]:
    return [
        {"id": "clock", "type": "clock", "enabled": True, "label": "Home Base", "show_label": True, "settings": {}},
        {
            "id": "weather",
            "type": "weather",
            "enabled": True,
            "label": "Local Weather",
            "show_label": True,
            "settings": {"forecast_days": 4, "show_icons": True},
        },
        {"id": "calendar", "type": "calendar", "enabled": True, "label": "Agenda", "show_label": True, "settings": {}},
        {
            "id": "photos",
            "type": "photos",
            "enabled": True,
            "label": "Photos",
            "show_label": True,
            "settings": {
                "source_mode": "folder",
                "static_path": "",
                "folder": "",
                "fit": "cover",
                "show_captions": False,
            },
        },
        {
            "id": "frigate",
            "type": "frigate",
            "enabled": True,
            "label": "Camera",
            "show_label": True,
            "settings": {"camera_name": "", "display_mode": "snapshot", "live_url": ""},
        },
    ]


DEFAULT_SETTINGS: dict[str, Any] = {
    "board_title": "Home Base",
    "layout_preset": "classic",
    "layout": {
        "mode": "preset",
        "preset": "classic",
        "display_size": "1920x1080",
        "width": 1920,
        "height": 1080,
        "orientation": "landscape",
        "custom_blocks": deepcopy(PRESET_LAYOUTS["classic"]),
        "saved_layouts": [],
    },
    "weather": {
        "enabled": True,
        "label": "Local Weather",
        "latitude": "",
        "longitude": "",
        "temperature_unit": "fahrenheit",
        "forecast_days": 4,
        "show_icons": True,
    },
    "calendar": {
        "enabled": True,
        "ics_url": "",
        "max_events": 6,
        "timezone": "America/Denver",
    },
    "photos": {
        "enabled": True,
        "rotation_seconds": 45,
        "display_mode": "background",
        "background_fit": "cover",
        "background_overlay": 55,
        "frame_fit": "cover",
        "show_captions": False,
    },
    "frigate": {
        "enabled": True,
        "base_url": "",
        "camera_name": "",
        "display_mode": "snapshot",
        "live_url": "",
        "snapshot_refresh_seconds": 10,
    },
    "blocks": {
        "clock": True,
        "calendar": True,
        "weather": True,
        "photos": True,
        "frigate": True,
    },
    "block_instances": _default_block_instances(),
}


def default_settings() -> dict[str, Any]:
    return deepcopy(DEFAULT_SETTINGS)


def merge_settings(existing: dict[str, Any] | None) -> dict[str, Any]:
    merged = default_settings()
    uses_legacy_blocks = bool(existing) and "block_instances" not in existing
    if existing:
        _deep_update(merged, existing)
    if uses_legacy_blocks:
        merged["block_instances"] = []
    _normalize_settings(merged)
    return merged


def settings_from_form(form: dict[str, str]) -> dict[str, Any]:
    settings = default_settings()
    settings["board_title"] = form.get("board_title", settings["board_title"]).strip() or "Home Base"
    settings["layout_preset"] = form.get("layout_preset", "classic")
    settings["layout"].update(
        {
            "mode": form.get("layout_mode", settings["layout"]["mode"]),
            "preset": settings["layout_preset"],
            "display_size": form.get("layout_display_size", settings["layout"]["display_size"]),
            "width": _int(form.get("layout_width"), settings["layout"]["width"], 320, 7680),
            "height": _int(form.get("layout_height"), settings["layout"]["height"], 320, 7680),
            "orientation": form.get("layout_orientation", settings["layout"]["orientation"]),
            "custom_blocks": _custom_blocks_from_form(form, settings["layout"]["custom_blocks"]),
        }
    )
    settings["weather"].update(
        {
            "enabled": _checked(form, "weather_enabled"),
            "label": form.get("weather_label", "Local Weather").strip() or "Local Weather",
            "latitude": form.get("weather_latitude", "").strip(),
            "longitude": form.get("weather_longitude", "").strip(),
            "temperature_unit": form.get("weather_temperature_unit", "fahrenheit"),
            "forecast_days": _int(form.get("weather_forecast_days"), 4, 1, 7),
            "show_icons": _checked(form, "weather_show_icons"),
        }
    )
    settings["calendar"].update(
        {
            "enabled": _checked(form, "calendar_enabled"),
            "ics_url": form.get("calendar_ics_url", "").strip(),
            "max_events": _int(form.get("calendar_max_events"), 6, 1, 20),
            "timezone": form.get("calendar_timezone", "America/Denver").strip() or "America/Denver",
        }
    )
    settings["photos"].update(
        {
            "enabled": _checked(form, "photos_enabled"),
            "rotation_seconds": _int(form.get("photos_rotation_seconds"), 45, 10, 3600),
            "display_mode": form.get("photos_display_mode", "background"),
            "background_fit": form.get("photos_background_fit", "cover"),
            "background_overlay": _int(form.get("photos_background_overlay"), 55, 0, 90),
            "frame_fit": form.get("photos_frame_fit", "cover"),
            "show_captions": _checked(form, "photos_show_captions"),
        }
    )
    settings["frigate"].update(
        {
            "enabled": _checked(form, "frigate_enabled"),
            "base_url": form.get("frigate_base_url", "").strip().rstrip("/"),
            "camera_name": form.get("frigate_camera_name", "").strip(),
            "display_mode": form.get("frigate_display_mode", "snapshot"),
            "live_url": form.get("frigate_live_url", "").strip(),
            "snapshot_refresh_seconds": _int(form.get("frigate_snapshot_refresh_seconds"), 10, 5, 600),
        }
    )
    settings["blocks"] = {
        "clock": _checked(form, "block_clock"),
        "calendar": _checked(form, "block_calendar"),
        "weather": _checked(form, "block_weather"),
        "photos": _checked(form, "block_photos"),
        "frigate": _checked(form, "block_frigate"),
    }
    settings["block_instances"] = _block_instances_from_form(form, settings)
    settings["layout"]["custom_blocks"] = _custom_blocks_from_form(
        form, settings["layout"]["custom_blocks"], settings["block_instances"]
    )
    settings["layout"]["saved_layouts"] = _saved_layouts_from_form(
        form, settings["layout"].get("saved_layouts", []), settings["block_instances"]
    )
    _apply_layout_action(settings, form)
    if settings["frigate"]["display_mode"] not in {"snapshot", "live"}:
        settings["frigate"]["display_mode"] = "snapshot"
    if settings["weather"]["temperature_unit"] not in {"fahrenheit", "celsius"}:
        settings["weather"]["temperature_unit"] = "fahrenheit"
    _normalize_settings(settings)
    return settings


def layout_for_display(settings: dict[str, Any]) -> dict[str, Any]:
    normalized = merge_settings(settings)
    layout = normalized["layout"]
    blocks = PRESET_LAYOUTS[layout["preset"]] if layout["mode"] == "preset" else layout["custom_blocks"]
    active_blocks = []
    for block in normalized["block_instances"]:
        if not block.get("enabled", False):
            continue
        block_id = block["id"]
        block_type = block["type"]
        rect = blocks.get(block_id) or blocks.get(block_type)
        if not rect:
            continue
        active_blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "label": block["label"],
                "show_label": block["show_label"],
                "settings": block.get("settings", {}),
                "rect": rect,
                "style": _rect_style(rect),
            }
        )
    return {
        "mode": layout["mode"],
        "preset": layout["preset"],
        "display_size": layout["display_size"],
        "width": layout["width"],
        "height": layout["height"],
        "orientation": layout["orientation"],
        "blocks": active_blocks,
    }


def admin_block_instances(settings: dict[str, Any]) -> list[dict[str, Any]]:
    normalized = merge_settings(settings)
    return deepcopy(normalized["block_instances"])


def _deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = value


def _normalize_settings(settings: dict[str, Any]) -> None:
    preset = settings.get("layout", {}).get("preset") or settings.get("layout_preset") or "classic"
    if preset not in LAYOUT_PRESETS:
        preset = "classic"
    settings["layout_preset"] = preset
    settings["layout"]["preset"] = preset

    if settings["layout"].get("mode") not in LAYOUT_MODES:
        settings["layout"]["mode"] = "preset"
    if settings["layout"].get("display_size") not in DISPLAY_SIZES:
        settings["layout"]["display_size"] = "1920x1080"
    if settings["layout"]["display_size"] != "custom":
        width, height = DISPLAY_SIZES[settings["layout"]["display_size"]]
        settings["layout"]["width"] = width
        settings["layout"]["height"] = height
    settings["layout"]["width"] = _int(str(settings["layout"].get("width")), 1920, 320, 7680)
    settings["layout"]["height"] = _int(str(settings["layout"].get("height")), 1080, 320, 7680)
    if settings["layout"].get("orientation") not in ORIENTATIONS:
        settings["layout"]["orientation"] = "portrait" if settings["layout"]["height"] > settings["layout"]["width"] else "landscape"
    _apply_orientation_to_dimensions(settings["layout"])
    settings["block_instances"] = _normalize_block_instances(settings)
    settings["blocks"] = _legacy_blocks_from_instances(settings["block_instances"])
    settings["layout"]["custom_blocks"] = _normalize_blocks(
        settings["layout"].get("custom_blocks", {}), settings["block_instances"]
    )
    settings["layout"]["saved_layouts"] = _normalize_saved_layouts(
        settings["layout"].get("saved_layouts", []), settings["block_instances"]
    )

    if settings["photos"].get("display_mode") not in {"background", "frame", "both"}:
        settings["photos"]["display_mode"] = "background"
    if settings["photos"].get("background_fit") not in {"cover", "contain"}:
        settings["photos"]["background_fit"] = "cover"
    if settings["photos"].get("frame_fit") not in {"cover", "contain"}:
        settings["photos"]["frame_fit"] = "cover"
    settings["photos"]["background_overlay"] = _int(str(settings["photos"].get("background_overlay")), 55, 0, 90)
    settings["photos"]["show_captions"] = bool(settings["photos"].get("show_captions"))
    settings["weather"]["forecast_days"] = _int(str(settings["weather"].get("forecast_days")), 4, 1, 7)
    settings["weather"]["show_icons"] = bool(settings["weather"].get("show_icons", True))


def _custom_blocks_from_form(
    form: dict[str, str], default_blocks: dict[str, Any], instances: list[dict[str, Any]] | None = None
) -> dict[str, dict[str, float]]:
    blocks: dict[str, dict[str, float]] = {}
    instance_ids = [block["id"] for block in instances] if instances else list(LAYOUT_BLOCKS)
    instance_types = {block["id"]: block["type"] for block in instances or []}
    for index, block_id in enumerate(instance_ids):
        block_type = instance_types.get(block_id, block_id)
        default_rect = default_blocks.get(block_id, default_blocks.get(block_type, PRESET_LAYOUTS["classic"][block_type]))
        blocks[block_id] = {
            "x": _float(form.get(f"layout_block_{block_id}_x"), default_rect["x"]),
            "y": _float(form.get(f"layout_block_{block_id}_y"), default_rect["y"]),
            "w": _float(form.get(f"layout_block_{block_id}_w"), default_rect["w"]),
            "h": _float(form.get(f"layout_block_{block_id}_h"), default_rect["h"]),
            "z": _float(form.get(f"layout_block_{block_id}_z"), default_rect.get("z", index + 1)),
        }
    return _normalize_blocks(blocks, instances)


def _normalize_blocks(raw_blocks: dict[str, Any], instances: list[dict[str, Any]] | None = None) -> dict[str, dict[str, float]]:
    blocks: dict[str, dict[str, float]] = {}
    instance_ids = [block["id"] for block in instances] if instances else list(LAYOUT_BLOCKS)
    instance_types = {block["id"]: block["type"] for block in instances or []}
    for index, block_id in enumerate(instance_ids):
        block_type = instance_types.get(block_id, block_id)
        fallback = PRESET_LAYOUTS["classic"][block_type]
        raw_rect = raw_blocks.get(block_id, fallback) if isinstance(raw_blocks, dict) else fallback
        rect = {
            "x": _float(raw_rect.get("x") if isinstance(raw_rect, dict) else None, fallback["x"]),
            "y": _float(raw_rect.get("y") if isinstance(raw_rect, dict) else None, fallback["y"]),
            "w": _float(raw_rect.get("w") if isinstance(raw_rect, dict) else None, fallback["w"]),
            "h": _float(raw_rect.get("h") if isinstance(raw_rect, dict) else None, fallback["h"]),
            "z": _float(raw_rect.get("z") if isinstance(raw_rect, dict) else None, index + 1),
        }
        rect["w"] = max(MIN_BLOCK_SIZE, min(100, rect["w"]))
        rect["h"] = max(MIN_BLOCK_SIZE, min(100, rect["h"]))
        rect["x"] = max(0, min(100 - rect["w"], rect["x"]))
        rect["y"] = max(0, min(100 - rect["h"], rect["y"]))
        rect["z"] = max(1, min(999, round(rect["z"])))
        blocks[block_id] = rect
    return blocks


def _saved_layouts_from_form(
    form: dict[str, str], default_layouts: list[dict[str, Any]], instances: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    raw_layouts: Any = default_layouts
    if form.get("layout_saved_layouts"):
        try:
            raw_layouts = json.loads(form["layout_saved_layouts"])
        except json.JSONDecodeError:
            raw_layouts = default_layouts
    return _normalize_saved_layouts(raw_layouts, instances)


def _normalize_saved_layouts(raw_layouts: Any, instances: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(raw_layouts, list):
        return []
    layouts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw_layout in enumerate(raw_layouts[:MAX_SAVED_LAYOUTS], start=1):
        if not isinstance(raw_layout, dict):
            continue
        name = str(raw_layout.get("name") or f"Saved layout {index}").strip() or f"Saved layout {index}"
        layout_id = str(raw_layout.get("id") or _slugify(name) or f"saved-layout-{index}").strip()
        layout_id = _unique_id(layout_id, seen)
        seen.add(layout_id)
        layouts.append(
            {
                "id": layout_id,
                "name": name,
                "blocks": _normalize_blocks(raw_layout.get("blocks", {}), instances),
            }
        )
    return layouts


def _apply_layout_action(settings: dict[str, Any], form: dict[str, str]) -> None:
    action = form.get("layout_action", "")
    if action not in {"load_saved", "save_current", "save_new"}:
        return
    selected_id = form.get("layout_saved_id", "")
    saved_layouts = settings["layout"]["saved_layouts"]
    selected = next((layout for layout in saved_layouts if layout["id"] == selected_id), None)
    if action == "load_saved" and selected:
        settings["layout"]["mode"] = "custom"
        settings["layout"]["custom_blocks"] = deepcopy(selected["blocks"])
        return
    if action == "save_current" and selected:
        selected["blocks"] = deepcopy(settings["layout"]["custom_blocks"])
        selected["name"] = form.get("layout_saved_name", selected["name"]).strip() or selected["name"]
        return
    if action == "save_new":
        name = form.get("layout_saved_name", "").strip() or f"Saved layout {len(saved_layouts) + 1}"
        seen = {layout["id"] for layout in saved_layouts}
        saved_layouts.append(
            {
                "id": _unique_id(_slugify(name) or "saved-layout", seen),
                "name": name,
                "blocks": deepcopy(settings["layout"]["custom_blocks"]),
            }
        )


def _slugify(value: str) -> str:
    slug = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            slug.append(char)
            previous_dash = False
        elif not previous_dash:
            slug.append("-")
            previous_dash = True
    return "".join(slug).strip("-")


def _unique_id(value: str, seen: set[str]) -> str:
    base = value or "saved-layout"
    candidate = base
    index = 2
    while candidate in seen:
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def _block_instances_from_form(form: dict[str, str], settings: dict[str, Any]) -> list[dict[str, Any]]:
    raw_ids = _block_instance_ids_from_form(form)
    instances: list[dict[str, Any]] = []
    existing = {block["id"]: block for block in settings.get("block_instances", [])}
    for block_id in raw_ids[:MAX_BLOCK_INSTANCES]:
        block_type = form.get(f"block_{block_id}_type", existing.get(block_id, {}).get("type", _type_from_block_id(block_id))).strip()
        if block_type not in BLOCK_TYPES:
            continue
        fallback = existing.get(block_id) or _fallback_instance(block_id, block_type, settings)
        label = form.get(f"block_{block_id}_label", fallback["label"]).strip() or fallback["label"]
        instances.append(
            {
                "id": block_id,
                "type": block_type,
                "enabled": _checked(form, f"block_{block_id}_enabled")
                or _checked(form, f"block_{block_id}")
                or settings.get("blocks", {}).get(block_id, False),
                "label": label,
                "show_label": _checked(form, f"block_{block_id}_show_label"),
                "settings": _block_specific_settings_from_form(form, block_id, block_type, fallback.get("settings", {})),
            }
        )
    return instances


def _block_instance_ids_from_form(form: dict[str, str]) -> list[str]:
    explicit_ids = [item.strip() for item in form.get("block_instance_ids", "").split(",") if item.strip()]
    if explicit_ids:
        return explicit_ids
    photo_count = _int(form.get("photo_block_count"), 1, 0, MAX_BLOCK_INSTANCES)
    camera_count = _int(form.get("camera_block_count"), 1, 0, MAX_BLOCK_INSTANCES)
    return [
        "clock",
        "weather",
        "calendar",
        *[f"photos_{index}" for index in range(1, photo_count + 1)],
        *[f"frigate_{index}" for index in range(1, camera_count + 1)],
    ]


def _type_from_block_id(block_id: str) -> str:
    if block_id.startswith("photos_"):
        return "photos"
    if block_id.startswith("frigate_"):
        return "frigate"
    return block_id


def _normalize_block_instances(settings: dict[str, Any]) -> list[dict[str, Any]]:
    raw_instances = settings.get("block_instances")
    if not isinstance(raw_instances, list):
        raw_instances = []
    if not raw_instances:
        raw_instances = [_fallback_instance(block_id, block_id, settings) for block_id in LAYOUT_BLOCKS]

    instances: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_instances[:MAX_BLOCK_INSTANCES]:
        if not isinstance(raw, dict):
            continue
        block_type = raw.get("type")
        block_id = raw.get("id")
        if block_type not in BLOCK_TYPES or not isinstance(block_id, str) or not block_id or block_id in seen:
            continue
        fallback = _fallback_instance(block_id, block_type, settings)
        merged_settings = {**fallback.get("settings", {}), **(raw.get("settings") if isinstance(raw.get("settings"), dict) else {})}
        instances.append(
            {
                "id": block_id,
                "type": block_type,
                "enabled": bool(raw.get("enabled", fallback["enabled"])),
                "label": str(raw.get("label") or fallback["label"]).strip() or fallback["label"],
                "show_label": bool(raw.get("show_label", fallback["show_label"])),
                "settings": _normalize_block_specific_settings(block_type, merged_settings),
            }
        )
        seen.add(block_id)
    return instances


def _fallback_instance(block_id: str, block_type: str, settings: dict[str, Any]) -> dict[str, Any]:
    defaults = {block["type"]: block for block in _default_block_instances()}
    fallback = deepcopy(defaults[block_type])
    fallback["id"] = block_id
    fallback["enabled"] = bool(settings.get("blocks", {}).get(block_type, fallback["enabled"]))
    if block_type == "clock":
        fallback["label"] = settings.get("board_title", fallback["label"])
    elif block_type == "weather":
        fallback["label"] = settings.get("weather", {}).get("label", fallback["label"])
        fallback["settings"] = {
            "forecast_days": settings.get("weather", {}).get("forecast_days", 4),
            "show_icons": settings.get("weather", {}).get("show_icons", True),
        }
    elif block_type == "calendar":
        fallback["label"] = "Agenda"
    elif block_type == "frigate":
        fallback["settings"] = {
            "camera_name": settings.get("frigate", {}).get("camera_name", ""),
            "display_mode": settings.get("frigate", {}).get("display_mode", "snapshot"),
            "live_url": settings.get("frigate", {}).get("live_url", ""),
        }
    return fallback


def _block_specific_settings_from_form(
    form: dict[str, str], block_id: str, block_type: str, fallback: dict[str, Any]
) -> dict[str, Any]:
    if block_type == "weather":
        return {
            "forecast_days": _int(form.get(f"block_{block_id}_forecast_days"), fallback.get("forecast_days", 4), 1, 7),
            "show_icons": _checked(form, f"block_{block_id}_show_icons"),
        }
    if block_type == "photos":
        return {
            "source_mode": form.get(f"block_{block_id}_photo_source_mode", fallback.get("source_mode", "folder")),
            "static_path": form.get(f"block_{block_id}_photo_static_path", fallback.get("static_path", "")).strip().lstrip("/"),
            "folder": form.get(f"block_{block_id}_photo_folder", fallback.get("folder", "")).strip().strip("/"),
            "fit": form.get(f"block_{block_id}_photo_fit", fallback.get("fit", "cover")),
            "show_captions": _checked(form, f"block_{block_id}_photo_show_captions"),
        }
    if block_type == "frigate":
        return {
            "camera_name": form.get(f"block_{block_id}_camera_name", fallback.get("camera_name", "")).strip(),
            "display_mode": form.get(f"block_{block_id}_display_mode", fallback.get("display_mode", "snapshot")),
            "live_url": form.get(f"block_{block_id}_live_url", fallback.get("live_url", "")).strip(),
        }
    return {}


def _normalize_block_specific_settings(block_type: str, settings: dict[str, Any]) -> dict[str, Any]:
    if block_type == "weather":
        return {
            "forecast_days": _int(str(settings.get("forecast_days")), 4, 1, 7),
            "show_icons": bool(settings.get("show_icons", True)),
        }
    if block_type == "photos":
        source_mode = settings.get("source_mode", "folder")
        fit = settings.get("fit", "cover")
        return {
            "source_mode": source_mode if source_mode in {"static", "folder"} else "folder",
            "static_path": str(settings.get("static_path", "")).strip().lstrip("/"),
            "folder": str(settings.get("folder", "")).strip().strip("/"),
            "fit": fit if fit in {"cover", "contain"} else "cover",
            "show_captions": bool(settings.get("show_captions", False)),
        }
    if block_type == "frigate":
        display_mode = settings.get("display_mode", "snapshot")
        return {
            "camera_name": str(settings.get("camera_name", "")).strip(),
            "display_mode": display_mode if display_mode in {"snapshot", "live"} else "snapshot",
            "live_url": str(settings.get("live_url", "")).strip(),
        }
    return {}


def _legacy_blocks_from_instances(instances: list[dict[str, Any]]) -> dict[str, bool]:
    return {block_type: any(block["type"] == block_type and block["enabled"] for block in instances) for block_type in LAYOUT_BLOCKS}


def _apply_orientation_to_dimensions(layout: dict[str, Any]) -> None:
    width = layout["width"]
    height = layout["height"]
    if layout["orientation"] == "portrait" and width > height:
        layout["width"], layout["height"] = height, width
    elif layout["orientation"] == "landscape" and height > width:
        layout["width"], layout["height"] = height, width


def _rect_style(rect: dict[str, float]) -> str:
    return (
        f"left: {_format_percent(rect['x'])}%; top: {_format_percent(rect['y'])}%; "
        f"width: {_format_percent(rect['w'])}%; height: {_format_percent(rect['h'])}%; "
        f"z-index: {_format_percent(rect.get('z', 1))};"
    )


def _checked(form: dict[str, str], key: str) -> bool:
    return form.get(key) in {"on", "true", "1", "yes"}


def _int(raw: str | None, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(raw or default)
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def _float(raw: Any, default: float) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float(default)


def _format_percent(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
