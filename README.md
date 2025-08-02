# Envertech Solar Integration for Home Assistant

A custom Home Assistant integration to retrieve real-time data from the Envertech Solar Portal (`envertecportal.com`) using your station ID.

## Features

- Current solar power in watts
- Daily, monthly, yearly, and total energy in kWh
- Ready-to-use sensor templates
- Cleanly packaged as a HACS-compatible custom integration
- Designed for the Envertech `ECO`/`SE` inverters (e.g. 2000SE)

## Installation

### Via HACS (recommended)
1. Add this repository as a **Custom Repository** in HACS → Integrations.
2. Search for **Envertech Solar** and install.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Integrations → + Add Integration**, search for "Envertech Solar".
5. Enter your **Station ID** from `envertecportal.com`.

### Manual Installation
1. Download or clone this repository.
2. Copy the `envertech_solar` folder to `custom_components/envertech_solar/` inside your Home Assistant config directory.
3. Restart Home Assistant and follow the setup instructions above.

## Example Dashboard Card

```yaml
type: entities
title: Envertech Solar Übersicht
entities:
  - entity: sensor.solartotalpower
    name: Aktuelle Leistung
  - entity: sensor.solartodayenergy
    name: Tagesenergie
  - entity: sensor.solarmonthenergy
    name: Monatsenergie
  - entity: sensor.solaryearenergy
    name: Jahresenergie
  - entity: sensor.solartotalenergy
    name: Gesamtenergie

