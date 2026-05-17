# Cultural Concierge

A multi-agent classical music concierge for London.

I built it because I missed Martha Argerich performing here — I'd been too busy to check every venue's newsletter, and by the time I noticed, the concert was gone. So I built the thing that should have noticed for me.

You ask it something natural — *"find me a piano recital next month with a Korean soloist"* — and it finds candidates, scores them, checks them against your Google Calendar, and saves the ones you pick.

---

## How it works

Three Gemini agents coordinated through Google's Agent Development Kit (ADK):

- **Scout** searches via the Tavily API (no per-venue scrapers — they break), uses Gemini's response schema to extract structured event data, and scores each event on programme, performers, venue acoustics, and a Korean-artist bonus.
- **Planner** takes the user's choice, parses the date, queries Google Calendar (OAuth, freebusy on primary). If there's a conflict it asks how to proceed before wasting effort on logistics; if you're free, it suggests dinner near the venue and offers to save.
- **Concierge** is the coordinator that routes the user's messages to the right specialist.

Behind the Planner is a **custom MCP (Model Context Protocol) server** exposing `check_calendar` and `save_to_shortlist` as tools. Saves persist to **Supabase**; calendar reads hit live Google Calendar.

```
User
  │
  ▼
Concierge (router)
  │
  ├──► Scout ──► Tavily search + Gemini extraction + scoring
  │
  └──► Planner ──► MCP server ──► Google Calendar (freebusy)
                              └─► Supabase (shortlist)
```

---

## Tech stack

| Layer | Choice |
|---|---|
| Agents | Google ADK, Gemini 2.5 Flash |
| Web search | Tavily API |
| Structured output | Gemini `response_schema` |
| Calendar | Google Calendar API (OAuth 2.0, freebusy) |
| Tool layer | Custom MCP server, stdio transport |
| Persistence | Supabase (Postgres) |
| Language | Python 3.12 |
| UI | ADK web (developer console) |

---

## Setup

### 1. Install Python deps

```powershell
pip install -r requirements.txt
```

### 2. Set up Google Calendar OAuth

1. Create a Google Cloud project, enable the **Google Calendar API**.
2. Create OAuth 2.0 credentials of type **Desktop app**, download the JSON.
3. Rename the file to `credentials.json` and place it in `final_culture_concierge/`.
4. Add yourself as a test user in **OAuth consent screen → Test users**.
5. Run the one-time auth script:
   ```powershell
   cd final_culture_concierge
   python setup_google_auth.py
   ```
   A browser tab opens — sign in, click Allow. `token.json` will be created.

### 3. Set up Supabase

1. Create a free project at [supabase.com](https://supabase.com).
2. In the SQL Editor, run:
   ```sql
   create table shortlist (
     id uuid primary key default gen_random_uuid(),
     user_id text not null default 'me',
     saved_at timestamptz not null default now(),
     title text not null,
     url text,
     event_date text,
     venue text,
     event jsonb not null
   );
   ```
3. Grab your project URL and **service_role key** from Project Settings → API.

### 4. Set up `.env`

Copy `.env.example` to `.env` and fill in:

```
TAVILY_API_KEY=...
GOOGLE_API_KEY=...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
```

### 5. Run

```powershell
cd final_culture_concierge/agents
adk web --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), select `concierge` from the dropdown, start chatting.

---
<img width="1105" height="520" alt="image" src="https://github.com/user-attachments/assets/ef917db8-399b-489b-8ce4-4adeacde3ddd" />


## What's next

Two orthogonal directions, both supported by the current architecture:

**Breadth — more domains, same shape.** A restaurant planner agent can reuse `check_calendar` and `save_to_shortlist` through the existing MCP server, no rebuild. Same for theatre, exhibitions — anything calendar-shaped.

**Depth — better personalisation.** Once there's a real UI, preferences move from prompt to profile: favourite composers, mood (chamber vs symphonic, traditional vs contemporary), priority venues, price ceiling. The Critic scoring can learn from what you actually save.
