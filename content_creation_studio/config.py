"""
Shared configuration for the Content Creation Studio agents.
Centralizes model name and retry settings.
"""

import os
from google.genai import types

# Model used by all agents
MODEL_NAME = os.getenv("WORKER_MODEL", "gemini-2.5-flash")

# Retry config for handling 429 rate limits and transient errors
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Quality threshold for the improvement loop
QUALITY_SCORE_THRESHOLD = int(os.getenv("QUALITY_SCORE_THRESHOLD", "70"))
MAX_IMPROVEMENT_ITERATIONS = int(os.getenv("MAX_IMPROVEMENT_ITERATIONS", "2"))
