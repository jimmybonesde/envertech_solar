<img width="341" height="259" alt="logo" src="https://github.com/user-attachments/assets/d396989c-63ab-412f-ad09-fa1e0db7192d" />



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

<img width="300" height="500" alt="grafik" src="https://github.com/user-attachments/assets/e4402d2e-155c-425c-bb9e-d1bfa3d65c27" />


## Credits

Created with love for solar nerds by JimmyBones

## 💡 Tips & FAQ

### 🔍 Finding Your Station ID
To set up the **Envertech Solar Integration**, you need your **Station ID**.  
1. Open the [Envertech Portal](https://www.envertecportal.com/terminal/systemoverview).  
2. Click on one of your solar panels:  

<img width="400" alt="Click on a solar panel" src="https://github.com/user-attachments/assets/77d86a11-26fe-4db6-a985-79ca1fdd157b" />

3. Check the URL in your browser. It will look like this: https://www.envertecportal.com/terminal/systemhistory/03GFF6E15154525DA16901EC7A4541G1?sn=3014511
4. The part after `/systemhistory/` and before `?sn=` is your **Station ID**:  > `03GFF6E15154525DA16901EC7A4541G1`

### ⚡ Sensor Tips
- **`Power`**: Real-time solar output in watts.  
- **`UnitEToday`, `UnitEMonth`, `UnitEYear`, `UnitETotal`**: Cumulative energy in kWh – ideal for history cards.  
- **`peak_power_today`**: Updates dynamically throughout the day.  
- **`strpeakpower`**: Retrieved from the Envertech API; may not update in real-time.

### ❗ Common Issues
- **Integration not appearing in HACS**: Ensure the repository is public and refresh HACS.  
- **Invalid Station ID**: Double-check the ID copied from the portal URL.  
- **Sensors showing `unknown`**: Verify your inverter is online and reporting data to the Envertech Portal.

### 📊 Dashboard Tips
- Use **gauge** cards for real-time power.  
- Use **entity** or **entities** cards for cumulative energy metrics.  
- Combine sensors in a **vertical-stack** or **grid** card for a clean overview.  
- Optional: Apply conditional coloring on gauges (green/yellow/red) to visualize thresholds easily.

## 📊 Example Dashboard Card

<img width="484" height="605" alt="grafik" src="https://github.com/user-attachments/assets/4d6787c6-ac72-4726-8753-f7537e0836e3" />

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
      yellow: 1000
      red: 1500
  - type: grid
    columns: 2
    square: false
    cards:
      - type: entity
        entity: sensor.daily_energy
        name: Daily Energy
        unit: kWh
        icon: mdi:weather-sunny
      - type: entity
        entity: sensor.monthly_energy
        name: Monthly Energy
        unit: kWh
        icon: mdi:calendar-month
      - type: entity
        entity: sensor.yearly_energy
        name: Yearly Energy
        unit: kWh
        icon: mdi:calendar
      - type: entity
        entity: sensor.total_energy
        name: Total Energy
        unit: kWh
        icon: mdi:counter
  - type: entities
    entities:
      - entity: sensor.daily_peak_power
        name: Today’s Peak Power
        icon: mdi:flash
      - entity: sensor.all_time_peak_power
        name: All-Time Peak Power
        icon: mdi:flash
