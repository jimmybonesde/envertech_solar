# Envertech Solar Integration for Home Assistant

A custom Home Assistant integration to retrieve real-time data from the Envertech Solar Portal (`envertecportal.com`) using your station ID.

## Features

- Current solar power in watts
- Peak power
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
Can be found by clicking on one of your solar panels in the Envertech Cloud via a browser at the URL
https://www.envertecportal.com/terminal/systemhistory/03GFF6E15154525DA16901EC7A4541G1?sn=3014511
where 03GFF6E15154525DA16901EC7A4541G1 is your station ID.

### Manual Installation
1. Download or clone this repository.
2. Copy the `envertech_solar` folder to `custom_components/envertech_solar/` inside your Home Assistant config directory.
3. Restart Home Assistant and follow the setup instructions above.

## Credits

Created with love for solar nerds by JImmyBOnes

## Example Dashboard Card

<img width="384" height="677" alt="grafik" src="https://github.com/user-attachments/assets/62f80770-51ef-448a-96ce-a2aaf2bd4427" />


```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## ☀️ Solar Power Overview
  - type: gauge
    entity: sensor.solartotalpower
    name: Current Power
    unit: W
    min: 0
    max: 5000
    severity:
      green: 0
      yellow: 2500
      red: 4000
  - type: entity
    entity: sensor.solartodayenergy
    name: Daily Energy
    unit: kWh
  - type: entity
    entity: sensor.solarmonthenergy
    name: Monthly Energy
    unit: kWh
  - type: entity
    entity: sensor.solaryearenergy
    name: Yearly Energy
    unit: kWh
  - type: entity
    entity: sensor.solartotalenergy
    name: Total Energy
    unit: kWh
  - type: entity
    entity: sensor.solarpeakpower
    name: Peak Power Today
    unit: kW