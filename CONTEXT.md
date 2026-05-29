# Context

Domain glossary for the Poem.town Home Assistant integration. This file is a
glossary only — no implementation details. Keep test names and interface
vocabulary aligned with these terms.

## Glossary

- **Clock** — the physical Poem.town device the user owns. Holds exactly one API
  token. Modeled in Home Assistant as one config entry, one device, and one
  notify entity.
- **Screen ID** — the 40-character identifier of a clock's display. Used as the
  Home Assistant unique ID for the config entry, device, and entity.
- **Note** — a 1–140 character message posted to a clock. The only thing the Web
  API can do today is post a note.
- **Check-in** — when the clock polls Poem.town and pulls pending notes. This is
  *when* a posted note actually appears on the screen. Posting is
  fire-and-forget: the integration does not know when a check-in happens.
- **Token** — the per-clock Bearer credential (`poem_…`). Revoked if clock
  ownership transfers, so it can change over a clock's life; updating it is
  handled by the reconfigure and reauth flows.
