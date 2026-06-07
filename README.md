**⚠️ Disclaimer: This integration is unofficial and not officially supported or endorsed by Poem.town. Use at your own risk.**

# Poem.town 🪶 — Custom Home Assistant integration

[![Validate](https://github.com/yayadrian/HA-Poem-Town/actions/workflows/validate.yml/badge.svg)](https://github.com/yayadrian/HA-Poem-Town/actions/workflows/validate.yml)
[![Test](https://github.com/yayadrian/HA-Poem-Town/actions/workflows/test.yml/badge.svg)](https://github.com/yayadrian/HA-Poem-Town/actions/workflows/test.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

A custom [Home Assistant](https://www.home-assistant.io/) integration for
[Poem.town](https://poem.town) clocks. It lets Home Assistant post notes to a
clock's screen using the [Poem.town Web API](https://poem.town/developer/web-api).

> The Web API currently exposes a single capability: **posting a note** to a
> clock. The note appears on the screen the next time the clock checks in.
> There are no read/status endpoints, so this integration provides a
> **notify entity** rather than sensors.

## Features

- Config-flow setup (no YAML), one clock per entry, each as its own device.
- A `notify` entity per configured clock for sending notes (1–140 characters).
- Reconfigure and reauth flows for updating a clock's API token (e.g. after it
  is rotated or revoked) without removing and re-adding the integration.

## Requirements

- Home Assistant **2025.1.0** or newer.
- A Poem.town clock with a per-clock API token (from *Dashboard → your clock →
  Web API* on poem.town).

## Installation

### HACS (custom repository)

1. In HACS, open the three-dot menu → **Custom repositories**, paste this
   repository's URL, and choose category **Integration**.
2. Search for **Poem.town** in HACS and install it.
3. Restart Home Assistant.

### Manual

1. Copy `custom_components/poemtown` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration** and search for **Poem.town**.
2. Enter:
   - **Name** — a friendly name for the clock.
   - **API token** — the per-clock Bearer token from Poem.town Dashboard > *Dashboard → your clock → Web API* on poem.town (starts with `poem_`).
   - **Screen ID** — the Screen ID of your clock (e.g. `80AB412341234`).

During setup, the integration posts a short confirmation note to validate the
credentials (the API has no read endpoint to test against).

## Usage

Call the `notify.send_message` action targeting the created notify entity:

```yaml
action: notify.send_message
target:
  entity_id: notify.poem_town_clock
data:
  message: "Hello from Home Assistant!"
```

Notes are limited to 140 characters; longer messages raise an error rather than
being truncated. The optional `title` field is ignored — only `message` is sent.

If the clock's token is revoked, posting fails and Home Assistant raises a
"reconfigure required" notification; update the token from the integration's
page (**Settings → Devices & Services → Poem.town → Reconfigure**).

## API reference

- Base URL: `https://poem.town/api/v1`
- Endpoint: `POST /notes` with `{ "screenId": "...", "body": "..." }`
- Auth: `Authorization: Bearer poem_...`

## Development

Run the linter and tests the same way CI does:

```bash
python3.13 -m venv .venv
.venv/bin/pip install pytest-homeassistant-custom-component aioresponses ruff
.venv/bin/ruff check custom_components tests
.venv/bin/ruff format --check custom_components tests
.venv/bin/pytest
```

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## Disclaimer

This is an unofficial, community integration and is not affiliated with Poem.town.