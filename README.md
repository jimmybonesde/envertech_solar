# Envertech Solar Integration for Home Assistant ☀️

A custom Home Assistant integration to retrieve real-time data from the Envertech Solar Portal (`envertecportal.com`) using your station ID.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jimmybonesde&repository=envertech_solar&category=integration)

## Features

- Live solar power in watts
- Daily Peak Power (calculated from real-time power measurements)
- All-Time Peak Power from Envertech API
- Installed capacity (kWp)
- Inverter model information
- Daily, monthly, yearly, and total energy in kWh
- Robust, ready-to-use sensor templates
- HACS-compatible for easy installation and updates  
  [Click here to add this integration to HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=jimmybonesde&repository=envertech_solar&category=integration)
- Designed for Envertech ECO / SE series inverters (e.g. 2000SE)

## Installation

### 🧰 Via HACS (recommended)
1. In HACS, go to **Integrations** → three dots menu → **Custom repositories**.
2. Add this repository:  
   `https://github.com/jimmybonesde/envertech_solar`
3. Search for **Envertech Solar** in HACS and install.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → + Add Integration**, search for "Envertech Solar".
6. Enter your **Station ID** from `envertecportal.com`.

> 💡 You can find your station ID in the browser URL after clicking one of your solar panels:  
> `https://www.envertecportal.com/terminal/systemhistory/03GFF6E15154525DA16901EC7A4541G1?sn=3014511`  
> → The string `03GFF6E15154525DA16901EC7A4541G1` is your station ID.

### 🛠️ Manual Installation
1. Download or clone this repository.
2. Copy the folder `envertech_solar` to:  
   `custom_components/envertech_solar/` inside your Home Assistant config directory.
3. Restart Home Assistant and follow the same setup as above.

## 📡 Available Sensors

| Sensor Key        | Name               | Unit  | Description                                      |
|-------------------|-------------------|-------|------------------------------------------------|
| `Power`           | Current Power      | W     | Current solar power output                     |
| `peak_power_today` | Daily Peak Power   | W     | Daily peak power calculated from live data    |
| `strpeakpower`    | All-Time Peak Power | W     | Peak power ever recorded by the inverter (API)|
| `UnitCapacity`    | Capacity           | kWp   | Installed solar system capacity               |
| `InvModel1`       | Inverter Model     | —     | Model of the inverter                          |
| `UnitEToday`      | Daily Energy       | kWh   | Energy produced today                          |
| `UnitEMonth`      | Monthly Energy     | kWh   | Energy produced this month                     |
| `UnitEYear`       | Yearly Energy      | kWh   | Energy produced this year                      |
| `UnitETotal`      | Total Energy       | kWh   | Total energy since commissioning              |

<img width="403" height="795" alt="grafik" src="https://github.com/user-attachments/assets/341f66b1-351b-4bd9-84ea-0b1e47bf8824" />

## Credits

Created with love for solar nerds by JimmyBones

## 💡 Tips & FAQ

### Finding Your Station ID
- Your station ID is required to set up the integration.  
- You can find it in the URL after clicking on one of your solar panels in the Envertech Portal:  
  `https://www.envertecportal.com/terminal/systemhistory/<STATION_ID>?sn=XXXXX`

### Sensor Tips
- `Power` shows real-time solar output in watts.  
- `UnitEToday`, `UnitEMonth`, `UnitEYear`, `UnitETotal` are cumulative kWh values – use these for dashboard history cards.  
- `peak_power_today` updates dynamically throughout the day.  
- `strpeakpower` is retrieved from the Envertech API and may not update in real-time.  

### Common Issues
- **Integration not appearing in HACS:** Make sure the repository is public and HACS has been refreshed.  
- **Station ID invalid:** Double-check that you copied the correct ID from the portal URL.  
- **Sensors showing `unknown` values:** Ensure your inverter is online and reporting data to the Envertech Portal.  

### Dashboard Tips
- Use `gauge` cards for real-time power, and `entity` or `entities` cards for cumulative energy metrics.  
- Combine sensors in a `vertical-stack` or `grid` card for a clean overview.  
- Optional: Add conditional coloring on gauges to visualize thresholds (green/yellow/red) for easy monitoring.

## 📊 Example Dashboard Card

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## ☀️ Solar Power Overview
  - type: gauge
    entity: sensor.current_power
    name: Current Power
    unit: W
    min: 0
    max: 2000
    severity:
      green: 0
      yellow: 1500
      red: 2000
  - type: entity
    entity: sensor.daily_energy
    name: Daily Energy
    unit: kWh
  - type: entity
    entity: sensor.monthly_energy
    name: Monthly Energy
  - type: entity
    entity: sensor.yearly_energy
    name: Yearly Energy
  - type: entity
    entity: sensor.total_energy
    name: Total Energy
    unit: kWh
  - type: entities
    entities:
      - entity: sensor.peak_power_today
        name: Daily Peak Power
      - entity: sensor.strpeakpower
        name: All-Time Peak Power
