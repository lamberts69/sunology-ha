# Validation Guide — Sunology Cloud Overview (v1.3.3)

## 1. Installation

### Via HACS (recommended)
1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/sunology-tech/sunology-ha` as **Integration**
3. Install **Sunology** and restart Home Assistant

### Manual
```
cp -r custom_components/sunology  <config>/custom_components/sunology
```
Restart Home Assistant after copying.

---

## 2. Prerequisites for cloud features

The `/api/overview` endpoint and all sensors described here require valid
Sunology cloud credentials (email + password) to be stored in the integration.

- During initial setup the config flow asks for **Sunology account e-mail** and
  **password** (both optional — leave blank for local-only mode).
- If credentials are already saved, go to **Settings → Devices & Services →
  Sunology → Configure** to update them.

---

## 3. Reload after update

When upgrading from a previous version without these sensors:

1. **Settings → Devices & Services → Sunology → ⋮ → Reload**
   — or —
   **Developer Tools → YAML → Reload custom integrations**
2. Wait ~10 s for the cloud overview coordinator to complete its first 30-second
   poll cycle.

---

## 4. Entities to verify in Developer Tools → States

Filter by `sunology` to list all entities.  The following should appear after a
successful cloud overview fetch.

### Fixed entities (always present when cloud is configured)

| Entity ID | Expected value |
|-----------|---------------|
| `sensor.sunology_production_total` | current total PV power in W |
| `sensor.sunology_grid_purchased` | W bought from grid (≥ 0) |
| `sensor.sunology_grid_sold` | W sold to grid (≥ 0) |
| `sensor.sunology_self_consumption_ratio` | % (0–100, or `unavailable` at night) |

### Dynamic — per panel

Entity IDs follow the template:
```
sensor.sunology_panel_<surname_slug>_production
sensor.sunology_panel_<surname_slug>_state
```
where `<surname_slug>` is the panel surname lowercased with spaces replaced by
underscores (e.g. `"Sunology 4"` → `sunology_4`).

Run this Jinja template in **Developer Tools → Template** to discover yours:
```jinja
{{ states | selectattr('entity_id','search','sunology_panel') | map(attribute='entity_id') | list }}
```

### Dynamic — per battery (replace `<serial>` with actual serial, e.g. `10003b3bd08c`)

| Entity ID | Unit | Notes |
|-----------|------|-------|
| `sensor.sunology_battery_<serial>_soc` | % | device_class: battery |
| `sensor.sunology_battery_<serial>_power` | W | positive=charging, negative=discharging |
| `sensor.sunology_battery_<serial>_state` | text | CHARGING / DISCHARGING / IDLE |
| `sensor.sunology_battery_<serial>_stored_energy` | kWh | current stored energy |
| `sensor.sunology_battery_<serial>_capacity` | Wh | nominal capacity (diagnostic) |
| `sensor.sunology_battery_<serial>_working_mode` | text | HUB_REMOTE / … (diagnostic) |

Discover battery serials:
```jinja
{{ states | selectattr('entity_id','search','sunology_battery') | map(attribute='entity_id') | list }}
```

### Dynamic — per hub (replace `<serial>` with actual serial, e.g. `80b54e626ee4`)

| Entity ID | Notes |
|-----------|-------|
| `binary_sensor.sunology_hub_<serial>_connected` | `on` = IoT connected, device_class: connectivity |

---

## 5. Add the dashboard

1. **Settings → Dashboards → Add Dashboard** (or open an existing one)
2. Click **⋮ → Edit Dashboard → Raw config editor**
3. Open `dashboard_sunology.yaml` from the repository root and paste its
   contents into the editor
4. Before saving, replace the placeholders:
   - `BATTERY_SERIAL` → your battery serial (lowercase, e.g. `10003b3bd08c`)
   - `HUB_SERIAL` → your hub serial (lowercase, e.g. `80b54e626ee4`)
   - Uncomment the panel entity lines that match your installation
5. Click **Save**

---

## 6. Expected behaviour notes

| Scenario | Expected state |
|----------|---------------|
| Night / no production | `sensor.sunology_production_total` = 0, `sensor.sunology_self_consumption_ratio` = `unavailable` (division by zero guard) |
| No battery configured | Battery entities are absent (not registered) |
| Cloud credentials absent | All overview entities are absent; local WebSocket sensors still work |
| Cloud temporarily unreachable | All overview entities show `unavailable` (coordinator sets `last_update_success=False`) |
| Hub disconnected | `binary_sensor.sunology_hub_<serial>_connected` = `off` |

---

## 7. Troubleshooting

- **Entities not appearing**: confirm credentials are saved (see §2) and check
  `custom_components/sunology/` contains `cloud_overview.py` and `binary_sensor.py`.
- **`unavailable` after reload**: check Home Assistant logs for
  `"Overview fetch failed"` — usually a 401 (credentials) or network issue.
- **Wrong panel slug**: use the Jinja template in §4 to find the exact entity
  ID rather than guessing the slug.
