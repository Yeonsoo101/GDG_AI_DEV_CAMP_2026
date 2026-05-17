"""
MCP server for the Cultural Concierge.

Exposes the Planner agent's tools (check_calendar, save_to_shortlist) over
the Model Context Protocol so the agent can reach them without a direct
Python import.

Run manually for testing:
    python -m mcp_server.server          # from final_culture_concierge/
or just:
    python server.py                     # from mcp_server/

ADK launches this automatically as a stdio subprocess when the Planner
agent is loaded (see agents/planner_agent/agent.py).
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

# Lazy Supabase: only import + connect when save_to_shortlist is first called.
# This keeps cold-start fast so ADK's MCP handshake doesn't time out.
_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        from supabase import create_client
        _supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    return _supabase


# server.py is at mcp_server/server.py; .env is at Health-Agent/.env
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
LONDON = ZoneInfo("Europe/London")

TOKEN_PATH = Path(__file__).parent.parent / "token.json"
LOG_PATH = Path(__file__).parent / "mcp_server.log"

mcp = FastMCP("Cultural Concierge")


def _log(msg: str) -> None:
    """
    Append to mcp_server.log. We can't print to stdout (it's the MCP protocol
    channel) and ADK captures stderr — so a file is the reliable place.
    Tail it with: Get-Content mcp_server.log -Wait  (PowerShell)
    """
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')}  {msg}\n")


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


@mcp.tool()
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
    _log(f"check_calendar({start_datetime!r}, {duration_hours})")

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

    result = {"free": len(conflicts) == 0, "conflicts": conflicts}
    _log(f"  → {len(conflicts)} conflict(s)")
    return result


@mcp.tool()
def save_to_shortlist(event: dict) -> dict:
    """
    Save an event the user has confirmed they want to keep.
    Persists to the `shortlist` table in Supabase.

    Args:
        event: full event JSON as produced by the Scout/Critic agent
               (title, url, date, venue, repertoire, performers, score, ...)

    Returns:
        dict with:
          ok: bool — True if saved successfully
          id: str  — the new row's UUID (or None if save failed)
    """
    title = event.get("title", "<no title>")
    _log(f"save_to_shortlist: {title!r}")

    response = _get_supabase().table("shortlist").insert({
        "title": title,
        "url": event.get("url"),
        "event_date": event.get("date"),
        "venue": event.get("venue"),
        "event": event,
    }).execute()

    saved_id = response.data[0]["id"] if response.data else None
    _log(f"  → saved id={saved_id}")
    return {"ok": saved_id is not None, "id": saved_id}


if __name__ == "__main__":
    _log("starting MCP server (stdio transport)")
    mcp.run()
