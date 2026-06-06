# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-06

Initial release.

### Added

- Config-flow setup (no YAML), one clock per entry, each as its own device.
- A `notify` entity per configured clock for posting notes (1–140 characters)
  via `notify.send_message`.
- Reconfigure and reauth flows for updating a clock's API token without
  removing and re-adding the integration.
- Credential verification during setup by posting a short confirmation note
  (the Web API has no read endpoint to test against).
- HACS metadata, hassfest/HACS validation workflow, and a Ruff + pytest CI
  workflow.

[Unreleased]: https://github.com/yayadrian/HA-Poem-Town/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yayadrian/HA-Poem-Town/releases/tag/v0.1.0
