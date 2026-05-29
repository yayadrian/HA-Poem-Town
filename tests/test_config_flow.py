"""Tests for the Poem.town config, reconfigure, and reauth flows."""

from __future__ import annotations

from aioresponses import aioresponses
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.poemtown.const import (
    CONF_NAME,
    CONF_SCREEN_ID,
    CONF_TOKEN,
    DOMAIN,
    NOTES_ENDPOINT,
)

SCREEN_ID = "7CDA2990A994"
TOKEN = "poem_testtoken"
USER_INPUT = {
    CONF_NAME: "Living room clock",
    CONF_TOKEN: TOKEN,
    CONF_SCREEN_ID: SCREEN_ID,
}


async def _start_user_flow(hass: HomeAssistant, user_input: dict) -> dict:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    return await hass.config_entries.flow.async_configure(result["flow_id"], user_input)


async def test_user_flow_success_creates_entry(hass: HomeAssistant) -> None:
    """A successful flow verifies the token and creates the entry."""
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=201, payload={"id": "n1"})
        result = await _start_user_flow(hass, USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living room clock"
    assert result["data"][CONF_TOKEN] == TOKEN
    assert result["data"][CONF_SCREEN_ID] == SCREEN_ID
    assert result["result"].unique_id == SCREEN_ID


async def test_user_flow_invalid_auth(hass: HomeAssistant) -> None:
    """A 401 during verification shows the invalid_auth error."""
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=401, body="no")
        result = await _start_user_flow(hass, USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_validation_error(hass: HomeAssistant) -> None:
    """A 422 during verification maps to invalid_screen_id."""
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=422, body="bad")
        result = await _start_user_flow(hass, USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_screen_id"}


async def test_user_flow_empty_screen_id_rejected(hass: HomeAssistant) -> None:
    """An empty screen id is rejected before any network call."""
    with aioresponses() as mock:
        result = await _start_user_flow(hass, {**USER_INPUT, CONF_SCREEN_ID: "  "})
        assert mock.requests == {}

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_SCREEN_ID: "invalid_screen_id"}


async def test_user_flow_duplicate_aborts(hass: HomeAssistant) -> None:
    """Adding a clock that is already configured aborts."""
    MockConfigEntry(domain=DOMAIN, unique_id=SCREEN_ID, data=USER_INPUT).add_to_hass(
        hass
    )

    with aioresponses() as mock:
        result = await _start_user_flow(hass, USER_INPUT)
        assert mock.requests == {}

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow_updates_token(hass: HomeAssistant) -> None:
    """Reauth verifies and stores a new token, then aborts successfully."""
    entry = MockConfigEntry(domain=DOMAIN, unique_id=SCREEN_ID, data=USER_INPUT)
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=201, payload={"id": "n1"})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_TOKEN: "poem_newtoken"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_TOKEN] == "poem_newtoken"


async def test_reauth_flow_bad_token_shows_error(hass: HomeAssistant) -> None:
    """A rejected new token keeps the reauth form open with an error."""
    entry = MockConfigEntry(domain=DOMAIN, unique_id=SCREEN_ID, data=USER_INPUT)
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=401, body="no")
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_TOKEN: "poem_stillbad"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert entry.data[CONF_TOKEN] == TOKEN


async def test_reconfigure_flow_updates_token(hass: HomeAssistant) -> None:
    """Reconfigure verifies and stores a new token, then aborts successfully."""
    entry = MockConfigEntry(domain=DOMAIN, unique_id=SCREEN_ID, data=USER_INPUT)
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with aioresponses() as mock:
        mock.post(NOTES_ENDPOINT, status=201, payload={"id": "n1"})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_TOKEN: "poem_reconfig"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_TOKEN] == "poem_reconfig"
