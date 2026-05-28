from app.services.calendar import parse_ics_events
from datetime import datetime, timedelta, timezone


def test_parse_ics_events_includes_title_date_and_times():
    start = datetime.now(timezone.utc) + timedelta(days=10)
    end = start + timedelta(hours=1)
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:1
DTSTART:{start.strftime("%Y%m%dT%H%M%SZ")}
DTEND:{end.strftime("%Y%m%dT%H%M%SZ")}
SUMMARY:Dentist
END:VEVENT
END:VCALENDAR
"""

    events = parse_ics_events(ics, max_events=3)

    assert events[0]["title"] == "Dentist"
    assert events[0]["date"]
    assert events[0]["start_time"]
    assert events[0]["end_time"]


def test_parse_ics_events_handles_google_until_with_timezone_aware_start():
    start = datetime.now(timezone.utc) + timedelta(days=7)
    start_text = start.strftime("%Y%m%dT090000")
    until_text = (start + timedelta(days=21)).strftime("%Y%m%dT235959")
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:google-style-recurring
DTSTART;TZID=America/Denver:{start_text}
DTEND;TZID=America/Denver:{start.strftime("%Y%m%dT100000")}
RRULE:FREQ=WEEKLY;UNTIL={until_text}
SUMMARY:Trash pickup
END:VEVENT
END:VCALENDAR
"""

    events = parse_ics_events(ics, max_events=3, display_timezone="America/Denver")

    assert events
    assert events[0]["title"] == "Trash pickup"


def test_parse_ics_events_handles_date_only_until_with_timezone_aware_start():
    upcoming = datetime.now(timezone.utc) + timedelta(days=10)
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:date-only-until
DTSTART;TZID=America/Denver:2020{upcoming.strftime("%m%d")}T090000
DTEND;TZID=America/Denver:2020{upcoming.strftime("%m%d")}T100000
RRULE:FREQ=YEARLY;UNTIL=20991231
SUMMARY:Anniversary
END:VEVENT
END:VCALENDAR
"""

    events = parse_ics_events(ics, max_events=1, display_timezone="America/Denver")

    assert events
    assert events[0]["title"] == "Anniversary"
