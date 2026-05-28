from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import quote


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}


class PhotoService:
    def __init__(self, photo_dir: Path, max_photos: int = 500):
        self.photo_dir = photo_dir
        self.max_photos = max_photos

    def list_photos(self, folder: str = "") -> list[dict[str, str]]:
        root_dir = self._safe_path(folder) if folder else self.photo_dir
        if not root_dir or not root_dir.exists() or not root_dir.is_dir():
            return []
        photos: list[Path] = []
        for root, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [
                dirname
                for dirname in sorted(dirnames)
                if not dirname.startswith(".") and dirname.lower() not in {"#recycle", "@eadir"}
            ]
            for filename in sorted(filenames):
                path = Path(root) / filename
                if path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                photos.append(path)
                if len(photos) >= self.max_photos:
                    return self._photo_payload(photos)
        return self._photo_payload(photos)

    def static_photo(self, path: str) -> list[dict[str, str]]:
        photo = self._safe_path(path)
        if not photo or not photo.exists() or not photo.is_file() or photo.suffix.lower() not in IMAGE_EXTENSIONS:
            return []
        return self._photo_payload([photo])

    def _photo_payload(self, photos: list[Path]) -> list[dict[str, str]]:
        return [
            {
                "name": path.relative_to(self.photo_dir).as_posix(),
                "url": f"/photos/{quote(path.relative_to(self.photo_dir).as_posix())}",
            }
            for path in sorted(photos)
        ]

    def payload(self, settings: dict[str, Any]) -> dict[str, Any]:
        photo_settings = settings["photos"]
        options = {
            "rotation_seconds": photo_settings["rotation_seconds"],
            "display_mode": photo_settings.get("display_mode", "background"),
            "background_fit": photo_settings.get("background_fit", "cover"),
            "background_overlay": photo_settings.get("background_overlay", 55),
            "frame_fit": photo_settings.get("frame_fit", "cover"),
            "show_captions": photo_settings.get("show_captions", False),
        }
        blocks = self._block_payloads(settings)
        if not photo_settings["enabled"]:
            return {"enabled": False, "photos": [], "blocks": blocks, **options}
        return {
            "enabled": True,
            "photos": self.list_photos(),
            "blocks": blocks,
            **options,
        }

    def _block_payloads(self, settings: dict[str, Any]) -> dict[str, Any]:
        block_payloads: dict[str, Any] = {}
        for block in settings.get("block_instances", []):
            if block.get("type") != "photos":
                continue
            block_settings = block.get("settings", {})
            source_mode = block_settings.get("source_mode", "folder")
            photos = (
                self.static_photo(block_settings.get("static_path", ""))
                if source_mode == "static"
                else self.list_photos(block_settings.get("folder", ""))
            )
            block_payloads[block["id"]] = {
                "enabled": bool(block.get("enabled", False)) and bool(settings["photos"].get("enabled", True)),
                "source_mode": source_mode,
                "photos": photos,
                "fit": block_settings.get("fit", settings["photos"].get("frame_fit", "cover")),
                "show_captions": bool(block_settings.get("show_captions", settings["photos"].get("show_captions", False))),
            }
        return block_payloads

    def _safe_path(self, raw_path: str) -> Path | None:
        if not raw_path:
            return None
        candidate = (self.photo_dir / raw_path).resolve()
        root = self.photo_dir.resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return None
        return candidate
