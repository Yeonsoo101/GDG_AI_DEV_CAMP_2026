# AI Cultural Concierge for London — Implementation Plan

A multi-agent classical music concierge that finds London events, judges performance quality (with a soft spot for Korean artists), and plans the evening around your calendar.

**Timeline:** 7 days × 2–3 hrs = 14–21 hours total.

---

## Core idea (final)

Three ADK agents work in sequence:

1. **Scout** — searches the web for classical events in London matching the user's query
2. **Critic** — judges each event's quality (program, performers, venue) with a Korean-artist green-flag bonus
3. **Planner** — checks Google Calendar for conflicts, suggests logistics, saves shortlisted events

A **custom MCP server** sits underneath, exposing user preferences, the shortlist, and calendar tools to the agents.

No scrapers. Web search (Tavily) replaces venue-by-venue scraping. This is what real agentic systems do — and it works for any event the web knows about, not just the 6 venues you started with.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Agents | Google ADK | Already learned in coursework |
| Search tool | Tavily API | Built for agents; clean structured results; free tier sufficient |
| MCP | Custom Python MCP server | Demonstrates MCP knowledge; clean abstraction for prefs/calendar/shortlist |
| Calendar | Google Calendar API (read-only, freebusy) | Galaxy/Samsung Calendar has no public API. GCal it is. |
| Backend | FastAPI | Hosts ADK agents + MCP client |
| Database | Supabase (Postgres) | Easy auth + DB in one; generous free tier |
| Frontend | Next.js + TailwindCSS | Chat UI + event cards |
| Deploy | Vercel (frontend) + Render (backend) | Both free tiers; fewer surprises than Railway |

---

## Architecture

```
┌──────────────┐     ┌──────────────────────────────────────┐
│  Next.js UI  │ ──▶ │  FastAPI                             │
└──────────────┘     │  ┌──────────────────────────────┐    │
                     │  │ ADK Orchestrator             │    │
                     │  │   Scout ─▶ Critic ─▶ Planner │    │
                     │  └──────────────────────────────┘    │
                     │           │            │             │
                     │           ▼            ▼             │
                     │      Tavily API   MCP client         │
                     │                       │              │
                     └───────────────────────┼──────────────┘
                                             ▼
                                  ┌──────────────────────┐
                                  │ Custom MCP server    │
                                  │  • get_preferences   │
                                  │  • save_to_shortlist │
                                  │  • get_shortlist     │
                                  │  • check_calendar    │
                                  └──────────────────────┘
                                             │
                                             ▼
                                  Supabase + Google Calendar API
```

---

## The three agents in detail

### 1. Scout agent

**Goal:** Return ~10 candidate events in structured JSON.

- Tool: Tavily web search
- Prompt strategy: Compose targeted queries like `"classical concert London June 2026 piano recital"`, then have the LLM extract `{title, venue, date, program, performers, price_range, url}` from the search results.
- No scrapers, no per-venue logic. The agent decides what to search for.

### 2. Critic agent

**Goal:** Score each event 1–10 and explain why.

Scoring rubric (in the agent's prompt):
- **Program interest** (0–3): is the repertoire compelling / unusual / a personal favorite?
- **Performer reputation** (0–3): web search for the conductor/soloist; recent reviews
- **Venue/acoustics** (0–1): Wigmore > most others for chamber; Barbican/RFH for orchestral
- **Korean artist bonus** (0–3): if a Korean artist is performing → strong green flag

Korean artist green-flag list (configurable in DB, seeded with):
- **Piano:** Seong-Jin Cho, Yunchan Lim, Sunwook Kim, Yeol Eum Son, Kun-Woo Paik
- **Violin:** Bomsori Kim, Inmo Yang, Clara-Jumi Kang
- **Cello:** Sung-Won Yang, Han-Na Chang
- **Voice:** Sumi Jo
- **Conductor:** Myung-Whun Chung
- (User can add more via UI)

Critic tool: Tavily search for performer reviews / recent performances.

### 3. Planner agent

**Goal:** Take the user's chosen events and make the evening real.

- Calls MCP `check_calendar` to flag conflicts
- Suggests when to leave, dinner near venue (LLM reasoning, no Maps API needed for v1)
- Calls MCP `save_to_shortlist` when user confirms

---

## Custom MCP server

A single Python MCP server (`mcp_server/`) exposing four tools:

| Tool | Input | Output |
|---|---|---|
| `get_user_preferences` | `user_id` | Korean artist list, favorite composers, price ceiling, preferred venues |
| `save_to_shortlist` | `user_id, event_json` | `{ok: true}` |
| `get_shortlist` | `user_id` | List of saved events |
| `check_calendar` | `user_id, datetime, duration_hrs` | `{free: bool, conflicts: [...]}` |

Why MCP here (and not just direct function calls): you wanted to use MCP, and this is a clean fit — the agents don't know or care that prefs live in Postgres and calendar lives in Google. The MCP layer hides that.

---

## Day-by-day plan (14–21 hrs)

### Day 1 — Scaffolding (2–3 hrs)
- New repo branch, clean directory structure: `agents/`, `mcp_server/`, `frontend/`, `backend/`
- FastAPI hello-world endpoint
- ADK installed, dummy single-agent test working
- Tavily account + API key, run one test search from a script
- Supabase project created, schema for `users`, `preferences`, `shortlist`

### Day 2 — Scout agent (2–3 hrs)
- Wire Tavily as an ADK tool
- Scout agent prompt: extract structured event data from search results
- Test query: "piano recitals in London June 2026" → returns 5+ valid events
- Handle obvious failure modes (no results, malformed dates)

### Day 3 — Critic agent + Korean preference (2–3 hrs)
- Critic agent with Tavily review-search tool
- Korean artist list hardcoded in prompt for v1 (move to DB later if time)
- Scoring rubric in prompt; output `{score, reasoning, korean_flag: bool}`
- Test on 5 real events from Day 2 — sanity-check scores manually

### Day 4 — MCP server + Google Calendar (2–3 hrs) **⚠ highest risk day**
- Build MCP server with 4 tools, in-memory stubs first
- Wire `get_preferences`, `save_to_shortlist`, `get_shortlist` to Supabase
- Google Cloud project, OAuth credentials, GCal API enabled
- Implement `check_calendar` using freebusy endpoint
- **Buffer:** if GCal OAuth eats the day, stub it and return mock conflicts — fix on Day 7

### Day 5 — Planner agent + orchestration (2–3 hrs)
- Planner agent uses MCP tools
- ADK orchestrator: Scout → Critic → Planner pipeline
- End-to-end CLI test: "find me a piano recital next month under £50"

### Day 6 — Frontend (2–3 hrs)
- Next.js + Tailwind
- Chat input → display ranked event cards
- Each card shows: title, venue, date, score, Critic's reasoning, Korean flag 🇰🇷, calendar conflict warning
- "Save to shortlist" button
- Shortlist page

### Day 7 — Deploy + polish (2–3 hrs)
- Frontend → Vercel
- Backend + MCP server → Render
- Env vars, CORS, OAuth redirect URIs (always painful)
- Test full flow on deployed version
- Buffer for whatever broke

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Google Calendar OAuth eats a full day | High | Stub it on Day 4, only wire real auth on Day 7 if time |
| Tavily results are noisy for niche events | Medium | Tighten Scout's query strategy; fall back to specific venue queries |
| ADK multi-agent handoff is fiddly | Medium | Start with sequential pipeline, no "agent decides next agent" magic |
| Render free tier cold starts | Low | Acceptable for a demo |
| Critic gives weird scores | Medium | Iterate prompt with 5 real events; add few-shot examples |

---

## MVP cut order (if running behind)

Cut in this order — each line saves ~2 hrs:

1. **Skip Next.js frontend.** Use ADK's built-in web UI. Still demoable.
2. **Stub Google Calendar.** Hardcode "no conflicts" — Planner agent still works.
3. **Merge Critic into Scout.** One agent that finds + scores. Still multi-agent (Scout/Critic-combined + Planner = 2).
4. **Hardcode preferences.** No `get_preferences` MCP tool — just put the Korean artist list in the Critic prompt.

You should NOT cut: the MCP server (you want to learn it), the Korean-artist preference (your differentiator), web search (the architectural pivot).

---

## What success looks like at end of week

A deployed app where you can type:
> "Find me a piano recital in London in the next 6 weeks under £60"

and get back:

- 5 ranked events
- Each with a 1–10 quality score and a one-sentence reason
- A 🇰🇷 flag if a Korean artist is performing
- A ⚠ flag if it conflicts with your calendar
- A "save" button that puts it in your shortlist

That's the demo. It's small, it's real, and you'll actually use it.
