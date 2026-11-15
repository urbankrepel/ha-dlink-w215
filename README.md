# D-Link DSP-W215 for Home Assistant (firmware 2.2x)

The built-in `dlink` integration can read the state of a DSP-W215 on firmware 2.2x, but it can't switch it: the plug answers `ERROR` to `SetSocketSettings`. This integration switches the relay with `SetModuleEnabled` instead, which the plug still accepts. Everything stays local, with no cloud.

Tested on DSP-W215 hardware B1, firmware 2.24.

## Install (HACS)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/urbankrepel/ha-dlink-w215`, type **Integration**.
2. Install **D-Link DSP-W215 (firmware 2.2x)** and restart Home Assistant.

Manual install: copy `custom_components/dlink_w215` into `/config/custom_components/`.

## Configure

Remove the built-in D-Link integration for the plug first, then:

**Settings → Devices & services → Add integration → "D-Link DSP-W215"**, and enter the plug's IP address and the 6-digit PIN from its label.

You get:
- **Switch**: on/off
- **Power** (W): live reading
- **Energy** (kWh): total that keeps counting up, ready for the **Energy dashboard** (Settings → Dashboards → Energy → add device). The plug stores no total that can be read, so this adds up the power readings every 15 s. It survives restarts, and it doesn't count time when the plug is unreachable.
- **Temperature**: the plug's internal temperature, disabled by default. If you used the YAML setup from v1.0.0, it's imported into the UI automatically. After that you can delete the YAML block.
