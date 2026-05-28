from __future__ import annotations

from typing import Any
from urllib.parse import quote


class FrigateService:
    def status(self, settings: dict[str, Any]) -> dict[str, Any]:
        frigate = settings["frigate"]
        blocks = self._block_statuses(settings)
        camera_name = frigate.get("camera_name", "")
        if not frigate.get("enabled") or not frigate.get("base_url") or not camera_name:
            return {"configured": False, "mode": frigate.get("display_mode", "snapshot"), "error": None, "blocks": blocks}
        status = self._camera_status(
            enabled=True,
            base_url=frigate.get("base_url", ""),
            camera_name=camera_name,
            display_mode=frigate.get("display_mode", "snapshot"),
            live_url=frigate.get("live_url", ""),
            refresh_seconds=frigate.get("snapshot_refresh_seconds", 10),
        )
        status["blocks"] = blocks
        return status

    def snapshot_url(self, settings: dict[str, Any], camera: str) -> str | None:
        frigate = settings["frigate"]
        if not frigate["enabled"] or not frigate["base_url"] or not camera:
            return None
        return f"{frigate['base_url'].rstrip('/')}/api/{quote(camera)}/latest.jpg"

    def _block_statuses(self, settings: dict[str, Any]) -> dict[str, Any]:
        frigate = settings["frigate"]
        statuses: dict[str, Any] = {}
        for block in settings.get("block_instances", []):
            if block.get("type") != "frigate":
                continue
            block_settings = block.get("settings", {})
            statuses[block["id"]] = self._camera_status(
                enabled=bool(block.get("enabled", False)) and bool(frigate.get("enabled", True)),
                base_url=frigate.get("base_url", ""),
                camera_name=block_settings.get("camera_name", ""),
                display_mode=block_settings.get("display_mode", "snapshot"),
                live_url=block_settings.get("live_url", ""),
                refresh_seconds=frigate.get("snapshot_refresh_seconds", 10),
            )
        return statuses

    def _camera_status(
        self,
        *,
        enabled: bool,
        base_url: str,
        camera_name: str,
        display_mode: str,
        live_url: str,
        refresh_seconds: int,
    ) -> dict[str, Any]:
        if not enabled or not base_url or not camera_name:
            return {"configured": False, "mode": display_mode, "error": None}
        if display_mode == "live":
            if not live_url:
                return {
                    "configured": True,
                    "mode": "live",
                    "live_url": "",
                    "error": "Live mode needs a browser-playable Frigate/go2rtc URL.",
                }
            return {"configured": True, "mode": "live", "live_url": live_url, "error": None}
        return {
            "configured": True,
            "mode": "snapshot",
            "snapshot_url": f"/api/frigate/snapshot?camera={quote(camera_name)}",
            "refresh_seconds": refresh_seconds,
            "error": None,
        }
