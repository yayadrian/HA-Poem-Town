"""Tests for the Poem.town API client."""

from __future__ import annotations

import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from custom_components.poemtown.api import (
    PoemTownAuthError,
    PoemTownClient,
    PoemTownError,
    PoemTownRateLimitError,
    PoemTownValidationError,
)
from custom_components.poemtown.const import MAX_NOTE_LENGTH, NOTES_ENDPOINT

SCREEN_ID = "A" * 40
TOKEN = "poem_testtoken"


async def test_post_note_success_sends_expected_request() -> None:
    """A valid note is POSTed with the right body and Bearer header."""
    with aioresponses() as mock:
        mock.post(
            NOTES_ENDPOINT,
            status=201,
            payload={"id": "abc123", "postedAt": "2026-01-01T00:00:00Z"},
        )
        async with aiohttp.ClientSession() as session:
            client = PoemTownClient(session, TOKEN, SCREEN_ID)
            result = await client.async_post_note("hello clock")

        assert result["id"] == "abc123"

        request = mock.requests[("POST", URL(NOTES_ENDPOINT))][0]
        assert request.kwargs["json"] == {
            "screenId": SCREEN_ID,
            "body": "hello clock",
        }
        assert request.kwargs["headers"]["Authorization"] == f"Bearer {TOKEN}"


async def test_post_note_too_long_raises_without_calling_api() -> None:
    """A note over the limit is rejected locally with no HTTP request."""
    with aioresponses() as mock:
        async with aiohttp.ClientSession() as session:
            client = PoemTownClient(session, TOKEN, SCREEN_ID)
            with pytest.raises(PoemTownValidationError):
                await client.async_post_note("x" * (MAX_NOTE_LENGTH + 1))

        assert mock.requests == {}


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, PoemTownAuthError),
        (422, PoemTownValidationError),
        (429, PoemTownRateLimitError),
        (500, PoemTownError),
    ],
)
async def test_post_note_maps_error_statuses(
    status: int, expected: type[Exception]
) -> None:
    """Each error status maps to the matching typed exception."""
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=status, body="nope")
        async with aiohttp.ClientSession() as session:
            client = PoemTownClient(session, TOKEN, SCREEN_ID)
            with pytest.raises(expected):
                await client.async_post_note("hello")


@pytest.mark.parametrize("body", ["", "   ", "\n\t "])
async def test_post_note_empty_or_blank_raises_without_calling_api(
    body: str,
) -> None:
    """Empty or whitespace-only notes are rejected locally with no request."""
    with aioresponses() as mock:
        async with aiohttp.ClientSession() as session:
            client = PoemTownClient(session, TOKEN, SCREEN_ID)
            with pytest.raises(PoemTownValidationError):
                await client.async_post_note(body)

        assert mock.requests == {}
