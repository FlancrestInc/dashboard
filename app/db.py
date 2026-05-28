from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.settings import default_settings, merge_settings


class SettingsStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_settings(self) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("select value from settings where key = 'dashboard'").fetchone()
        if not row:
            settings = default_settings()
            self.save_settings(settings)
            return settings
        try:
            return merge_settings(json.loads(row["value"]))
        except json.JSONDecodeError:
            return default_settings()

    def save_settings(self, settings: dict[str, Any]) -> None:
        payload = json.dumps(merge_settings(settings), sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                """
                insert into settings (key, value, updated_at)
                values ('dashboard', ?, datetime('now'))
                on conflict(key) do update set value = excluded.value, updated_at = excluded.updated_at
                """,
                (payload,),
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists settings (
                    key text primary key,
                    value text not null,
                    updated_at text not null default (datetime('now'))
                )
                """
            )
