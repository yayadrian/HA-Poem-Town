"""Notify platform for the Poem.town integration."""

from __future__ import annotations

import logging

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PoemTownConfigEntry
from .api import PoemTownError
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
    _attr_supported_features = NotifyEntityFeature(0)

    def __init__(self, entry: PoemTownConfigEntry) -> None:
        """Initialise the notify entity."""
        self._client = entry.runtime_data
        self._attr_name = entry.data[CONF_NAME]
        self._attr_unique_id = entry.data[CONF_SCREEN_ID]

    async def async_send_message(
        self, message: str, title: str | None = None
    ) -> None:
        """Post a note to the clock's screen."""
        body = message
        if len(body) > MAX_NOTE_LENGTH:
            raise HomeAssistantError(
                f"Note exceeds {MAX_NOTE_LENGTH} characters "
                f"(got {len(body)})"
            )
        try:
            await self._client.async_post_note(body)
        except PoemTownError as err:
            raise HomeAssistantError(f"Failed to post note: {err}") from err
