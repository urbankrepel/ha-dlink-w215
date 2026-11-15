# D-Link DSP-W215 for Home Assistant (firmware 2.2x)

The built-in `dlink` integration can read the state of a DSP-W215 on firmware 2.2x, but it can't switch it: the plug answers `ERROR` to `SetSocketSettings`. This integration switches the relay with `SetModuleEnabled` instead, which the plug still accepts. Everything stays local, with no cloud.

Tested on DSP-W215 hardware B1, firmware 2.24.

## Install (HACS)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/urbankrepel/ha-dlink-w215`, type **Integration**.
2. Install **D-Link DSP-W215 (firmware 2.2x)** and restart Home Assistant.

Manual install: copy `custom_components/dlink_w215` into `/config/custom_components/`.

## Configure

Remove the built-in D-Link integration for the plug first, then add to `configuration.yaml`:

```yaml
switch:
  - platform: dlink_w215
    host: 192.168.x.x          # plug IP
    password: !secret w215_pin # 6-digit PIN from the plug's label
    name: D-Link Plug
```

Restart Home Assistant. The switch also exposes `current_power_w` and `temperature_c` attributes.
