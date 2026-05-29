"""Config flow for the Poem.town integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
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

STEP_TOKEN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
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

            if not screen_id:
                errors[CONF_SCREEN_ID] = "invalid_screen_id"
            else:
                await self.async_set_unique_id(screen_id)
                self._abort_if_unique_id_configured()

                # There is no read endpoint, so confirm credentials by posting
                # a short note. The clock shows it on next check-in.
                errors = await self._async_verify_token(
                    user_input[CONF_TOKEN], screen_id
                )
                if not errors:
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

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication when a token is rejected."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a new token for an existing clock."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            errors = await self._async_verify_token(
                user_input[CONF_TOKEN], entry.data[CONF_SCREEN_ID]
            )
            if not errors:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_TOKEN: user_input[CONF_TOKEN]}
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_TOKEN_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the API token for an already-configured clock."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            errors = await self._async_verify_token(
                user_input[CONF_TOKEN], entry.data[CONF_SCREEN_ID]
            )
            if not errors:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_TOKEN: user_input[CONF_TOKEN]}
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_TOKEN_SCHEMA,
            errors=errors,
        )

    async def _async_verify_token(self, token: str, screen_id: str) -> dict[str, str]:
        """Verify credentials by posting a note. Returns an errors dict."""
        client = PoemTownClient(
            session=async_get_clientsession(self.hass),
            token=token,
            screen_id=screen_id,
        )
        try:
            await client.async_post_note("Connected to Home Assistant")
        except PoemTownAuthError:
            return {"base": "invalid_auth"}
        except PoemTownValidationError:
            return {"base": "invalid_screen_id"}
        except PoemTownError:
            return {"base": "cannot_connect"}
        return {}
