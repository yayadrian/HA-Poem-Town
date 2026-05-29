"""Config flow for the Poem.town integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    PoemTownAuthError,
    PoemTownClient,
    PoemTownError,
    PoemTownValidationError,
)
from .const import (
    CONF_NAME,
    CONF_SCREEN_ID,
    CONF_TOKEN,
    DEFAULT_NAME,
    DOMAIN,
    SCREEN_ID_LENGTH,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(),
        vol.Required(CONF_TOKEN): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
        vol.Required(CONF_SCREEN_ID): TextSelector(),
    }
)


class PoemTownConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Poem.town."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            screen_id = user_input[CONF_SCREEN_ID].strip()

            if len(screen_id) != SCREEN_ID_LENGTH:
                errors[CONF_SCREEN_ID] = "invalid_screen_id"
            else:
                await self.async_set_unique_id(screen_id)
                self._abort_if_unique_id_configured()

                client = PoemTownClient(
                    session=async_get_clientsession(self.hass),
                    token=user_input[CONF_TOKEN],
                    screen_id=screen_id,
                )
                try:
                    # There is no read endpoint, so confirm credentials by
                    # posting a short note. The clock shows it on next check-in.
                    await client.async_post_note("Connected to Home Assistant")
                except PoemTownAuthError:
                    errors["base"] = "invalid_auth"
                except PoemTownValidationError:
                    errors["base"] = "invalid_screen_id"
                except PoemTownError:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data={
                            CONF_NAME: user_input[CONF_NAME],
                            CONF_TOKEN: user_input[CONF_TOKEN],
                            CONF_SCREEN_ID: screen_id,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
