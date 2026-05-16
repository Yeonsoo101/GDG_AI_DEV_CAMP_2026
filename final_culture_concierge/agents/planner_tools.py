"""
Tools for the Planner agent.

`check_calendar` is now wired to Google Calendar (primary calendar only).
`save_to_shortlist` is still a stub — Supabase comes later.

On Day 7, wrap both in an MCP server. Signatures stay the same so the
agent doesn't change.
"""
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
LONDON = ZoneInfo("Europe/London")

# planner_tools.py lives in agents/; token.json lives in final_culture_concierge/
TOKEN_PATH = Path(__file__).parent.parent / "token.json"


def _load_credentials() -> Credentials:
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(
            f"Missing {TOKEN_PATH}. Run setup_google_auth.py first."
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
    return creds


def check_calendar(start_datetime: str, duration_hours: float) -> dict:
    """
    Check whether the user's primary Google Calendar has any events
    overlapping the given concert slot.

    Args:
        start_datetime: ISO 8601 datetime, e.g. "2026-06-11T19:00:00".
                        Naive datetimes are interpreted as London local time.
        duration_hours: Length of the concert (incl. any interval).

    Returns:
        dict with:
          free: bool — True if no overlapping events
          conflicts: list of {title, start, end} for any clashing events
    """
    start = datetime.fromisoformat(start_datetime)
    if start.tzinfo is None:
        start = start.replace(tzinfo=LONDON)
    end = start + timedelta(hours=duration_hours)

    creds = _load_credentials()
    service = build("calendar", "v3", credentials=creds)

    response = service.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    conflicts = [
        {
            "title": ev.get("summary", "(no title)"),
            "start": ev["start"].get("dateTime") or ev["start"].get("date"),
            "end": ev["end"].get("dateTime") or ev["end"].get("date"),
        }
        for ev in response.get("items", [])
    ]

    return {"free": len(conflicts) == 0, "conflicts": conflicts}


def save_to_shortlist(event: dict) -> dict:
    """
    Save an event the user has confirmed they want to keep.

    Args:
        event: full event JSON as produced by the Scout/Critic agent
               (title, url, date, venue, repertoire, performers, score, ...)

    Returns:
        dict with:
          ok: bool — True if saved successfully
    """
    title = event.get("title", "<no title>")
    date = event.get("date", "<no date>")
    print(f"[STUB save_to_shortlist] saved: {title} ({date})")
    return {"ok": True}
