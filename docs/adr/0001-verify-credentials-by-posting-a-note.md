# 1. Verify credentials by posting a note

Date: 2026-05-29

## Status

Accepted

## Context

During config-flow setup (and the reauth/reconfigure flows), we want to confirm
that the API token and screen ID the user entered are valid before creating or
updating the config entry. This gives immediate feedback instead of letting the
first `notify.send_message` fail later.

The Poem.town Web API currently exposes a **single** endpoint: `POST /notes`.
There is no read/status/verify-credentials endpoint (one is planned for future
API development but does not exist today). So there is no side-effect-free way to
test credentials.

## Decision

Verify credentials by posting a short real note (e.g. "Connected to Home
Assistant") to the clock during setup, reconfigure, and reauth. A `201` confirms
the token and screen ID; `401` → `invalid_auth`, `422` → `invalid_screen_id`,
other failures → `cannot_connect`.

## Consequences

- **Visible side effect**: setup writes a note that will appear on the user's
  clock at its next check-in. This is surprising without context — hence this
  ADR and the note in the setup UI description.
- **No silent failures**: bad credentials are caught at setup rather than at
  first use.
- **Reversible later**: when the API gains a verify-credentials endpoint, swap
  the verification call in `_async_verify_token` (config_flow.py) to use it and
  drop the side effect. The flows' error mapping stays the same.
