"""Tests for the Poem.town notify entity (behavior via the notify action)."""

from __future__ import annotations

import aiohttp
import pytest
from aioresponses import aioresponses
from homeassistant.components.notify import (
    ATTR_MESSAGE,
    SERVICE_SEND_MESSAGE,
)
from homeassistant.components.notify import (
    DOMAIN as NOTIFY_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.poemtown.const import (
    CONF_NAME,
    CONF_SCREEN_ID,
    CONF_TOKEN,
    DOMAIN,
    MAX_NOTE_LENGTH,
    NOTES_ENDPOINT,
)

SCREEN_ID = "7CDA2990A994"
TOKEN = "poem_testtoken"


async def _init_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the integration with one configured clock."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=SCREEN_ID,
        title="Living room clock",
        data={
            CONF_NAME: "Living room clock",
            CONF_TOKEN: TOKEN,
            CONF_SCREEN_ID: SCREEN_ID,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _entity_id(hass: HomeAssistant) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(NOTIFY_DOMAIN, DOMAIN, SCREEN_ID)
    assert entity_id is not None
    return entity_id


async def _send(hass: HomeAssistant, message: str) -> None:
    await hass.services.async_call(
        NOTIFY_DOMAIN,
        SERVICE_SEND_MESSAGE,
        {ATTR_ENTITY_ID: _entity_id(hass), ATTR_MESSAGE: message},
        blocking=True,
    )


async def test_send_message_posts_note(hass: HomeAssistant) -> None:
    """Sending a message posts the note to the clock's screen."""
    await _init_integration(hass)
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=201, payload={"id": "n1"})
        await _send(hass, "hello clock")
        assert ("POST", aiohttp.client.URL(NOTES_ENDPOINT)) in mock.requests


async def test_send_message_too_long_raises(hass: HomeAssistant) -> None:
    """A note over the limit raises an error before any network call."""
    await _init_integration(hass)
    with aioresponses() as mock:
        with pytest.raises(HomeAssistantError):
            await _send(hass, "x" * (MAX_NOTE_LENGTH + 1))
        assert mock.requests == {}


@pytest.mark.parametrize("message", ["", "   "])
async def test_send_message_empty_raises(hass: HomeAssistant, message: str) -> None:
    """An empty or blank message raises an error before any network call."""
    await _init_integration(hass)
    with aioresponses() as mock:
        with pytest.raises(HomeAssistantError):
            await _send(hass, message)
        assert mock.requests == {}


async def test_send_message_runtime_401_starts_reauth(
    hass: HomeAssistant,
) -> None:
    """A 401 at runtime surfaces an error and starts a reauth flow."""
    entry = await _init_integration(hass)
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=401, body="no")
        with pytest.raises(HomeAssistantError):
            await _send(hass, "hello clock")
    await hass.async_block_till_done()

    flows = [
        flow
        for flow in hass.config_entries.flow.async_progress()
        if flow["context"].get("source") == "reauth"
        and flow["context"].get("entry_id") == entry.entry_id
    ]
    assert len(flows) == 1


async def test_send_message_rate_limited_raises(hass: HomeAssistant) -> None:
    """A 429 at runtime surfaces a clear error."""
    await _init_integration(hass)
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=429, body="slow down")
        with pytest.raises(HomeAssistantError):
            await _send(hass, "hello clock")


async def test_notify_entity_linked_to_clock_device(
    hass: HomeAssistant,
) -> None:
    """The notify entity is attached to a Poem.town device for the clock."""
    await _init_integration(hass)

    entity_entry = er.async_get(hass).async_get(_entity_id(hass))
    assert entity_entry.device_id is not None

    device = dr.async_get(hass).async_get(entity_entry.device_id)
    assert device is not None
    assert (DOMAIN, SCREEN_ID) in device.identifiers
    assert device.manufacturer == "Poem.town"
