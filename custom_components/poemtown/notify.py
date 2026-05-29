"""Notify platform for the Poem.town integration."""

from __future__ import annotations

import logging

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PoemTownConfigEntry
from .api import PoemTownAuthError, PoemTownError
from .const import CONF_NAME, CONF_SCREEN_ID, DOMAIN, MAX_NOTE_LENGTH

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PoemTownConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Poem.town notify entity from a config entry."""
    async_add_entities([PoemTownNotifyEntity(entry)])


class PoemTownNotifyEntity(NotifyEntity):
    """Posts notes to a Poem.town clock screen."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = NotifyEntityFeature(0)

    def __init__(self, entry: PoemTownConfigEntry) -> None:
        """Initialise the notify entity."""
        self._entry = entry
        self._client = entry.runtime_data
        screen_id = entry.data[CONF_SCREEN_ID]
        self._attr_unique_id = screen_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, screen_id)},
            name=entry.data[CONF_NAME],
            manufacturer="Poem.town",
        )

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Post a note to the clock's screen."""
        body = message
        if not body or not body.strip():
            raise HomeAssistantError("Note must not be empty")
        if len(body) > MAX_NOTE_LENGTH:
            raise HomeAssistantError(
                f"Note exceeds {MAX_NOTE_LENGTH} characters (got {len(body)})"
            )
        try:
            await self._client.async_post_note(body)
        except PoemTownAuthError as err:
            self._entry.async_start_reauth(self.hass)
            raise HomeAssistantError(
                "Poem.town rejected the API token; reconfigure it in settings"
            ) from err
        except PoemTownError as err:
            raise HomeAssistantError(f"Failed to post note: {err}") from err
