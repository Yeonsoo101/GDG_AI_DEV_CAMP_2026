"""
One-time Google Calendar OAuth setup.

Run this ONCE to mint `token.json` from your downloaded `credentials.json`.
After this, the Planner agent can read your calendar silently — no browser
popups, no user interaction.

Usage:
    python setup_google_auth.py

If you ever revoke access in your Google account, or the refresh token
stops working, delete `token.json` and re-run this script.
"""
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Read-only is enough for freebusy / event lookups.
# If you later want the agent to CREATE events, change to:
#   "https://www.googleapis.com/auth/calendar"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

HERE = Path(__file__).parent
CREDS_PATH = HERE / "credentials.json"
TOKEN_PATH = HERE / "token.json"


def authenticate() -> Credentials:
    creds: Credentials | None = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        print(f"✓ Existing token at {TOKEN_PATH} is still valid.")
        return creds

    if creds and creds.expired and creds.refresh_token:
        print("• Token expired — refreshing silently...")
        creds.refresh(Request())
    else:
        if not CREDS_PATH.exists():
            raise FileNotFoundError(
                f"Missing {CREDS_PATH}. Download your OAuth client JSON from "
                f"Google Cloud Console → APIs & Services → Credentials, "
                f"rename it to 'credentials.json', and place it next to this script."
            )
        print("• No valid token — running interactive OAuth flow...")
        print("  A browser window will open. Sign in and click 'Allow'.")
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json())
    print(f"✓ Saved token to {TOKEN_PATH}")
    return creds


def smoke_test(creds: Credentials) -> None:
    """Prove the token actually works by listing the user's calendars."""
    print("\n— Smoke test: listing your calendars —")
    service = build("calendar", "v3", credentials=creds)
    result = service.calendarList().list().execute()
    calendars = result.get("items", [])

    if not calendars:
        print("  (no calendars found — unusual, but auth itself worked)")
        return

    print(f"  Found {len(calendars)} calendar(s):")
    for cal in calendars:
        primary = " [primary]" if cal.get("primary") else ""
        print(f"    - {cal['summary']}{primary}")
        print(f"        id: {cal['id']}")


if __name__ == "__main__":
    creds = authenticate()
    smoke_test(creds)
    print("\nDone. The Planner agent can now use the calendar.")
