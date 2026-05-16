import os
from tavily import TavilyClient
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def get_event_search(query: str):
    """
    Search for classical music events in London using Tavily.
    Returns a list of Event objects. Structured fields (date, venue, repertoire,
    performers, price_range) are left empty here — the agent fills them in
    by reading `content`.
    """
    results = tavily.search(
        query=query,
        max_results=20,
        search_depth="advanced",
        include_raw_content=True,
        include_domains=[
            "lso.co.uk",
            "lpo.org.uk",
            "rpo.co.uk",
            "wigmore-hall.org.uk",
            "southbankcentre.co.uk",
            "barbican.org.uk",
            "cadoganhall.com",
            "bachtrack.com"
        ],
        exclude_domains=[
            "feverup.com",
            "fever.com",
            "candlelightconcerts.com",
            "candlelightexperience.com",
        ],
    )

    raw_content = "\n\n---\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\n\nContent:\n{r.get('raw_content') or r['content']}"
        for r in results["results"]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Extract classical music events from these search results.\n\n"
            "Rules:\n"
            "1. Skip anything that isn't a specific concert with a date.\n"
            "2. Skip ALL candlelight-themed concerts and tourist-oriented "
            "events (e.g. 'by Candlelight', Fever, Candlelight Concerts).\n"
            "3. `repertoire` must list each work as 'Composer — Piece' "
            "(e.g. 'Mahler — Symphony No. 2'). If a programme isn't given, "
            "skip the event entirely rather than guessing.\n"
            "4. `performers` must name specific orchestras, conductors, and "
            "soloists (e.g. 'London Symphony Orchestra', 'Sir Antonio Pappano'). "
            "Do not write vague labels like 'string quartet' or 'pianist'.\n\n"
            f"Search results:\n{raw_content}"
        ),
        config = types.GenerateContentConfig(
         response_mime_type="application/json",
         response_schema={
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {
                        "type": "STRING",
                        "description": "The title of the event"
                    },
                    "url": {
                        "type": "STRING",
                        "description": "The URL of the event"
                    },
                    "content": {
                        "type": "STRING",
                        "description": "The summary of the content of the event. Maximum 2 sentences."
                    },
                    "date": {
                        "type": "STRING",
                        "description": "The date and time of the event"
                    },
                    "venue": {
                        "type": "STRING",
                        "description": "The venue of the event"
                    },
                    "duration": {
                        "type": "STRING",
                        "description": "The duration of the event"
                    },
                    "repertoire": {
                        "type": "ARRAY",
                        "items": {
                            "type": "STRING"
                        },
                        "description": "The list of music pieces of the event"
                    },
                    "performers": {
                        "type": "ARRAY",
                        "items": {
                            "type": "STRING"
                        },
                        "description": "The list of performers of the event"
                    },
                    "price_range": {
                        "type": "STRING",
                        "description": "The price range of the event"
                    }
                }
            }
         }
        )
    )

    return response.text.strip()     




