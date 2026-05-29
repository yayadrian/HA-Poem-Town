"""Constants for the Poem.town integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "poemtown"

# Config entry keys
CONF_TOKEN: Final = "token"
CONF_SCREEN_ID: Final = "screen_id"
CONF_NAME: Final = "name"

# Poem.town Web API
API_BASE_URL: Final = "https://poem.town/api/v1"
NOTES_ENDPOINT: Final = f"{API_BASE_URL}/notes"

# API constraints
MAX_NOTE_LENGTH: Final = 140
SCREEN_ID_LENGTH: Final = 40

DEFAULT_NAME: Final = "Poem.town clock"
