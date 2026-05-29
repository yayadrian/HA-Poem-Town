# Poem.town — Home Assistant integration

A custom [Home Assistant](https://www.home-assistant.io/) integration for
[Poem.town](https://poem.town) clocks. It lets Home Assistant post notes to a
clock's screen using the [Poem.town Web API](https://poem.town/developer/web-api).

> The Web API currently exposes a single capability: **posting a note** to a
> clock. The note appears on the screen the next time the clock checks in.
> There are no read/status endpoints, so this integration provides a
> **notify entity** rather than sensors.

## Features

- Config-flow setup (no YAML) per clock.
- A `notify` entity per configured clock for sending notes (1–140 characters).

## Installation

### HACS (custom repository)

1. In HACS, add this repository as a custom repository (type: *Integration*).
2. Install **Poem.town**.
3. Restart Home Assistant.

### Manual

1. Copy `custom_components/poemtown` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration** and search for **Poem.town**.
2. Enter:
   - **Name** — a friendly name for the clock.
   - **API token** — the per-clock Bearer token from *Dashboard → your clock → Web API* on poem.town (starts with `poem_`).
   - **Screen ID** — the 40-character screen identifier for your clock.

During setup the integration posts a short confirmation note to validate the
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

Notes are limited to 140 characters.

## API reference

- Base URL: `https://poem.town/api/v1`
- Endpoint: `POST /notes` with `{ "screenId": "...", "body": "..." }`
- Auth: `Authorization: Bearer poem_...`

## Disclaimer

This is an unofficial, community integration and is not affiliated with Poem.town.
