"""Lightweight async client for the Poem.town Web API."""

from __future__ import annotations

import logging

import aiohttp

from .const import MAX_NOTE_LENGTH, NOTES_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class PoemTownError(Exception):
    """Base error for the Poem.town API."""


class PoemTownAuthError(PoemTownError):
    """Raised when the API token is missing, malformed, or mismatched (401)."""


class PoemTownValidationError(PoemTownError):
    """Raised when the request fails validation (422)."""


class PoemTownRateLimitError(PoemTownError):
    """Raised when the API rate limit is hit (429)."""


class PoemTownClient:
    """Minimal client for the Poem.town Web API.

    The Web API currently exposes a single endpoint: posting a note to a
    clock's screen. See https://poem.town/developer/web-api.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: str,
        screen_id: str,
    ) -> None:
        """Initialise the client with a session and per-clock credentials."""
        self._session = session
        self._token = token
        self._screen_id = screen_id

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    async def async_post_note(self, body: str) -> dict:
        """Post a note to the clock's screen.

        Returns the created note object (``id`` and ``postedAt``) on success.
        Raises a :class:`PoemTownError` subclass on failure.
        """
        if not body or not body.strip():
            raise PoemTownValidationError("Note body must not be empty")
        if len(body) > MAX_NOTE_LENGTH:
            raise PoemTownValidationError(
                f"Note body exceeds {MAX_NOTE_LENGTH} characters"
            )

        payload = {"screenId": self._screen_id, "body": body}

        try:
            async with self._session.post(
                NOTES_ENDPOINT, headers=self._headers, json=payload
            ) as resp:
                if resp.status == 401:
                    raise PoemTownAuthError("Invalid or mismatched API token")
                if resp.status == 422:
                    text = await resp.text()
                    raise PoemTownValidationError(f"Validation failed: {text}")
                if resp.status == 429:
                    raise PoemTownRateLimitError(
                        "Rate limited by Poem.town; try again later"
                    )
                if resp.status != 201:
                    text = await resp.text()
                    raise PoemTownError(f"Unexpected response {resp.status}: {text}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise PoemTownError(f"Connection error: {err}") from err
