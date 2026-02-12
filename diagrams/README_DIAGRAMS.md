# Architecture & System Diagrams

This directory contains Mermaid diagrams documenting the Content Creation Studio architecture and multi-agent system.

## Main Diagrams

### [Architecture Diagram](architecture.mmd)

**File**: `architecture.mmd` (Mermaid format)

Complete system architecture showing:
- **User Interface**: Web Browser
- **Google Cloud Run**: Combined Frontend + Backend Service (Port 8080)
- **Vertex AI Agent Engine**: Master Orchestrator, Coordinators, Analyzers
- **Infrastructure**: Artifact Registry, Cloud Storage, Cloud Logging
- **AI Models**: Gemini 2.5 Flash via Vertex AI

**Components:**
- Frontend: React 18 + Vite (static files)
- Backend: FastAPI + Uvicorn (API server)
- Agents: Master Orchestrator, Content Coordinator, Analyzer
- AI: Google Gemini 2.5 Flash
- Infrastructure: GCP services

### [Multi-Agent System Diagram](multi-agent-system.mmd)

**File**: `multi-agent-system.mmd` (Mermaid format)

Complete multi-agent workflow with 3 phases:

The Master Orchestrator routes to either the Full Content Workflow (complex) or the Content Analyzer (simple). The content brief is set directly in session state by the caller -- no intake agent needed.

**Phase 1: Research & Draft** (Blue - Sequential)
- Topic Research Agent: Find trending topics via google_search
- Content Drafter Agent: Create initial draft

**Phase 2: Quality Loop** (Orange - max 2 iterations)
- Quality Checker Agent: Score content (threshold >= 70)
- Content Improver Agent: Refine content, calls exit_loop when approved

**Phase 3: Multi-Channel Generation** (Green - Parallel)
- Blog Post Writer: 800-1200 words, SEO optimized
- Social Media Creator: LinkedIn, Twitter, Instagram
- Email Newsletter Writer: Subject + body + CTA
- SEO Metadata Agent: Meta tags, 5-10 keywords

Each parallel agent stores output via `output_key` in session state -- no final packager needed.

**Total Agents**: 9 specialist agents + 1 orchestrator + 1 analyzer
**Workflow Type**: Sequential -> Loop -> Parallel

## Color Coding

### Architecture Diagram
- **Cyan (#61dafb)**: Frontend components
- **Teal (#009688)**: Backend components
- **Orange (#ff6f00)**: Agent components
- **Red (#ea4335)**: AI/ML models
- **Blue (#4285f4)**: Cloud infrastructure

### Multi-Agent System Diagram
- **Purple (#9c27b0)**: Master Orchestrator (thick border)
- **Orange (#ff6f00)**: Full Content Workflow (medium border)
- **Light Blue (#e3f2fd)**: Phase 1 agents (Research & Draft)
- **Light Orange (#fff3e0)**: Phase 2 agents (Quality Loop)
- **Light Green (#e8f5e9)**: Phase 3 agents (Parallel generation)
- **Light Purple (#f3e5f5)**: Content Analyzer
- **Gold (#ffd700)**: Start/End points (thick border)

## How to Use

### GitHub/GitLab
Mermaid diagrams render automatically in `.mmd` files on GitHub and GitLab.

### VS Code
Install the [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension to preview `.mmd` files.

### Mermaid Live Editor
1. Open [mermaid.live](https://mermaid.live/)
2. Copy the content from `.mmd` files
3. View, edit, and export diagrams

## Quick Links

| Diagram | File | Purpose |
|---------|------|---------|
| **Architecture** | [architecture.mmd](architecture.mmd) | System architecture |
| **Multi-Agent** | [multi-agent-system.mmd](multi-agent-system.mmd) | Agent workflow |

## Key Insights from Diagrams

### Architecture
- Single Cloud Run service hosts both frontend and backend
- RemoteRunner connects backend to Agent Engine
- All agents use Gemini 2.5 Flash model
- Infrastructure includes staging bucket and logging

### Multi-Agent System
- Master Orchestrator routes to content workflow or analyzer via AgentTool
- Content brief set directly in session state (no intake agent)
- 3-phase pipeline: Sequential -> Loop -> Parallel
- Quality loop ensures score >= 70 (max 2 iterations)
- 4 parallel agents store outputs via output_key (no final packager)
- Content Analyzer handles simple text analysis requests

---

**Additional Resources:**
- [Main README](../README.md) - Project overview
- [Mermaid Documentation](https://mermaid.js.org/) - Syntax reference
