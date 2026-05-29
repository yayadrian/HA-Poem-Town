"""The Poem.town integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PoemTownClient
from .const import CONF_SCREEN_ID, CONF_TOKEN

PLATFORMS: list[Platform] = [Platform.NOTIFY]

type PoemTownConfigEntry = ConfigEntry[PoemTownClient]


async def async_setup_entry(
    hass: HomeAssistant, entry: PoemTownConfigEntry
) -> bool:
    """Set up Poem.town from a config entry."""
    session = async_get_clientsession(hass)
    client = PoemTownClient(
        session=session,
        token=entry.data[CONF_TOKEN],
        screen_id=entry.data[CONF_SCREEN_ID],
    )
    entry.runtime_data = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: PoemTownConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
