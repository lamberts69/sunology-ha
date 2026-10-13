# Sunology Home Assistant integration — community fork

Unofficial fork of [`sunology-tech/sunology-ha`](https://github.com/sunology-tech/sunology-ha)
that adds **write support for STOREY batteries** via the Sunology cloud API.

> This fork exists because the upstream maintainers have chosen a
> different strategy: they intend to add write support through the local
> WebSocket, in a future firmware/integration update. Until that ships,
> this fork lets you configure your STOREY battery from Home Assistant
> today. Once upstream supports local writes, please switch back —
> a local-only solution is intrinsically preferable.

## What this fork adds on top of upstream

All upstream functionality is preserved (local WebSocket telemetry,
zeroconf discovery, support for PLAY, PLAY Max, STOREY, STREAM Connect,
STREAM Meter, ERL Gen2). On top of that:

- `number.minsoc_<storey>` — battery reserve slider, 5 to 70 percent.
- `datetime.pause_until_<storey>` — pause charge/discharge until a target time.
- `button.<storey>_pause_30min` / `_1h` / `_4h` / `_stop` — pause presets.
- **Options flow** — update your Sunology cloud credentials without removing
  and re-adding the integration.
- **French and English translations** for all new fields.
- **Bug fixes** for pre-existing upstream issues that impact everyone,
  regardless of cloud usage (see [Fixes vs upstream](#fixes-vs-upstream)).

Reads remain 100% local (WebSocket to your STREAM Connect on port 20199).
Writes go through Sunology's cloud API at
`backend-mobile.stream.sunology.eu`, which then relays to your gateway —
the gateway echoes the new state on its local WebSocket within about 30
seconds, so entity state stays consistent with the mobile app.

## Why not local-only writes?

The local WebSocket on port 20199 silently rejects `hubCommand` payloads
for STOREY-level configuration (`minSoc`, `inhibitionTimeout`,
`workingMode`). About twenty payload variants were tried during reverse
engineering; none work. The official mobile app also uses the cloud path
for these operations, which is consistent with the current gateway
firmware not implementing local writes for these fields.

Upstream (Sunology) has indicated they plan to add local write support
directly in the gateway firmware, at which point this fork becomes
obsolete and should be archived.

## Installation

### Via HACS (recommended)

1. In Home Assistant, open HACS.
2. Three-dot menu (top right) → **Custom repositories**.
3. Add `https://github.com/lamberts69/sunology-ha` with category
   **Integration**.
4. Search HACS for "Sunology (community fork)" and install it. If you
   already have the upstream `sunology-tech/sunology-ha` installed,
   remove it first — the two share the same domain and cannot coexist.
5. Restart Home Assistant.
6. **Settings → Devices & Services → Add Integration → Sunology**.

### Manual

Copy `custom_components/sunology/` into your Home Assistant
`config/custom_components/` directory and restart HA.

## Configuration

At setup you're asked for:

- **Gateway IP / hostname** — your STREAM Connect. Usually auto-filled
  via zeroconf discovery.
- **Gateway port** — default `20199`.
- **Sunology account email** *(optional)* — same credentials as the
  official mobile app.
- **Sunology account password** *(optional)*.

Leave email and password blank for **read-only mode** — behaviourally
identical to upstream. Provide them to unlock the write-capable STOREY
entities listed above.

To change credentials later (e.g. after a password reset), open
**Settings → Devices & Services → Sunology → Configure**. No need to
remove and re-add the integration.

## How writes work

For read-only mode: identical to upstream. Zeroconf discovers the
gateway, a WebSocket connection to port 20199 streams `productInfo` and
event messages, which become sensor state.

For write mode: at setup, the integration performs a `POST
/api/login-post` against `backend-mobile.stream.sunology.eu` and stores
the resulting session cookie (Max-Age about 400 days). Writes to STOREY
parameters use `PATCH /api/storage-battery/{uuid}`. The gateway then
re-emits a fresh `productInfo` event on its local WebSocket within
roughly 30 seconds, and the integration state converges automatically.
On a 401 response, re-authentication happens transparently.

Your credentials are stored only in the Home Assistant config entry
(same protection level as any other cloud-based HA integration). They
are never logged.

## Fixes vs upstream

These are pre-existing upstream bugs that this fork also fixes. If you
run this fork instead of upstream, you benefit from them regardless of
whether you configure cloud credentials:

- Device removal via the UI no longer raises `AttributeError` (upstream
  [#10](https://github.com/sunology-tech/sunology-ha/issues/10) — typo
  `config_entry.runtime` fixed to `config_entry.runtime_data`).
- `socket.py` no longer raises `NameError` on non-`ConnectionClosed`
  exceptions (invalid `except e:` syntax corrected to `except Exception as e:`).
- `manifest.json` no longer declares `asyncio` as a requirement
  (`asyncio` is in the Python standard library).

## Known limitations

- `workingMode` is defined internally but not yet exposed as a Select
  entity. Only `HUB_REMOTE` has been characterized in the wild so far;
  `MANUEL` / `SUNCAST` variants need additional MITM captures to
  document their payloads.
- `flowWorkingMode` (whole-house working mode, on a different cloud
  endpoint keyed by MAC rather than UUID) is read-only in this fork.
- Reload after a credentials change may leave a stale WebSocket open
  for a few seconds. Restart HA if the write entities don't respond
  immediately after Save.
- Translations for German and Spanish are not updated for the new
  fields (only FR and EN are). Home Assistant falls back to English
  automatically, which is acceptable but not ideal — contributions
  welcome.

## Attribution

This fork is based on
[`sunology-tech/sunology-ha`](https://github.com/sunology-tech/sunology-ha),
which remains the upstream project. All original code retains its
original ownership. This fork is maintained by a Sunology customer,
is **not affiliated with or endorsed by Sunology**, and comes with no
warranty. Additions specific to this fork (cloud client, write
entities, options flow) are provided in the same spirit as the
upstream project.

## Reporting issues

For bugs specific to this fork (cloud client, write entities), please
open an issue in this repository.

For bugs in the underlying integration (telemetry, sensors, discovery,
device support), please open the issue **upstream** at
[`sunology-tech/sunology-ha`](https://github.com/sunology-tech/sunology-ha/issues)
so the broader community benefits from the fix.

---

*Last synced with upstream: v1.3.1 (July 2026). Fork version: 1.4.0.*
