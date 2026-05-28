from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from dateutil.rrule import rrulestr
from icalendar import Calendar

from app.services.cache import TTLCache


class CalendarService:
    def __init__(self, cache: TTLCache, refresh_seconds: int):
        self.cache = cache
        self.refresh_seconds = refresh_seconds

    async def agenda(self, settings: dict[str, Any]) -> dict[str, Any]:
        calendar = settings["calendar"]
        if not calendar["enabled"] or not calendar["ics_url"]:
            return {"configured": False, "events": [], "error": None}

        cache_key = f"calendar:{calendar['ics_url']}:{calendar['max_events']}:{calendar.get('timezone', 'UTC')}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
                response = await client.get(calendar["ics_url"])
                response.raise_for_status()
            events = parse_ics_events(
                response.text,
                int(calendar["max_events"]),
                display_timezone=calendar.get("timezone", "UTC"),
            )
            result = {"configured": True, "events": events, "error": None}
        except Exception as exc:
            result = {"configured": True, "events": [], "error": f"Calendar unavailable: {exc}"}
        self.cache.set(cache_key, result, self.refresh_seconds)
        return result


def parse_ics_events(
    ics_text: str,
    max_events: int = 6,
    display_timezone: str = "UTC",
) -> list[dict[str, str]]:
    cal = Calendar.from_ical(ics_text)
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=90)
    display_tz = _zoneinfo(display_timezone)
    events: list[tuple[datetime, dict[str, str]]] = []

    for component in cal.walk("VEVENT"):
        summary = str(component.get("summary", "Untitled event"))
        all_day = _is_all_day(component)
        dtstart = _to_datetime(component.decoded("dtstart"))
        dtend = _optional_datetime(component, "dtend")
        rrule = component.get("rrule")
        duration = (dtend - dtstart) if dtend else timedelta(days=1) if all_day else None

        starts = [dtstart]
        if rrule:
            window_start = now - duration if duration else now
            rrule_text = _normalize_rrule_until(rrule.to_ical().decode(), dtstart)
            starts = list(
                rrulestr(rrule_text, dtstart=dtstart).between(
                    window_start, horizon, inc=True
                )
            )

        for start in starts:
            if start > horizon:
                continue
            end = start + duration if duration else None
            if end:
                if end <= now:
                    continue
            elif start < now:
                continue
            start_display = start.astimezone(display_tz)
            end_display = end.astimezone(display_tz) if end else None
            events.append(
                (
                    start,
                    {
                        "title": summary,
                        "date": start_display.strftime("%a, %b %-d"),
                        "start_time": "" if all_day else start_display.strftime("%-I:%M %p"),
                        "end_time": "" if not end_display or all_day else end_display.strftime("%-I:%M %p"),
                        "all_day": "true" if all_day else "false",
                    },
                )
            )

    events.sort(key=lambda item: item[0])
    return [event for _, event in events[:max_events]]


def _to_datetime(value: datetime | date) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo:
            return value.astimezone(timezone.utc)
        return value.replace(tzinfo=timezone.utc)
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _optional_datetime(component: Any, key: str) -> datetime | None:
    if not component.get(key):
        return None
    return _to_datetime(component.decoded(key))


def _is_all_day(component: Any) -> bool:
    return isinstance(component.decoded("dtstart"), date) and not isinstance(component.decoded("dtstart"), datetime)


def _normalize_rrule_until(rrule_text: str, dtstart: datetime) -> str:
    if not dtstart.tzinfo:
        return rrule_text

    def replace(match: re.Match[str]) -> str:
        until = match.group(1)
        if until.endswith("Z"):
            return match.group(0)
        if len(until) == 8:
            return f"UNTIL={until}T235959Z"
        return f"UNTIL={until}Z"

    return re.sub(r"UNTIL=([^;:]+)", replace, rrule_text)


def _zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")
