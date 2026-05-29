# Poem.town — Home Assistant integration

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
   - **Screen ID** — the screen ID of your clock (e.g. `80AB412341234`).

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

Notes are limited to 140 characters; longer messages raise an error rather than
being truncated. The optional `title` field is ignored — only `message` is sent.

If the clock's token is revoked, posting fails and Home Assistant raises a
"reconfigure required" notification; update the token from the integration's
page (**Settings → Devices & Services → Poem.town → Reconfigure**).

## API reference

- Base URL: `https://poem.town/api/v1`
- Endpoint: `POST /notes` with `{ "screenId": "...", "body": "..." }`
- Auth: `Authorization: Bearer poem_...`

## Disclaimer

This is an unofficial, community integration and is not affiliated with Poem.town.
