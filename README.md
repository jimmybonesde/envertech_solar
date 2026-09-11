<p align="center">
  <img src="https://github.com/jimmybonesde/Envertech_local/raw/main/brand/logo.png" alt="Envertech Solar" width="180">
</p>

<h1 align="center">Envertech Solar for Home Assistant</h1>

<p align="center">
  <strong>Solar-Erträge, Leistung und Anlageninformationen direkt aus dem Envertech Solar Portal.</strong>
</p>

<p align="center">
  <a href="https://github.com/jimmybonesde/envertech_solar/releases"><img src="https://img.shields.io/github/v/release/jimmybonesde/envertech_solar?style=flat&logo=github" alt="Aktuelles Release"></a>
  <a href="https://github.com/jimmybonesde/envertech_solar/stargazers"><img src="https://img.shields.io/github/stars/jimmybonesde/envertech_solar?style=flat&logo=github" alt="GitHub Stars"></a>
  <a href="https://www.hacs.xyz/"><img src="https://img.shields.io/badge/HACS-Default-41BDF5?logo=homeassistant&logoColor=white" alt="HACS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT-Lizenz"></a>
</p>

<p align="center">
  <a href="#-installation">Installation</a> ·
  <a href="#-einrichtung">Einrichtung</a> ·
  <a href="#-sensoren">Sensoren</a> ·
  <a href="#-hilfe--faq">Hilfe & FAQ</a>
</p>

> **Envertech Solar** verbindet Home Assistant mit dem [Envertech Solar Portal](https://www.envertecportal.com/). Gib einmalig deine Station-ID ein und behalte Leistung, Ertrag und Anlageninformationen im Blick.

## ✨ Highlights

- ☀️ **Aktuelle Solarleistung** in Echtzeit
- 🔋 **Tages-, Monats-, Jahres- und Gesamtertrag**
- ⚡ **Tagesrekord** und **Allzeit-Spitzenleistung**
- 💶 **Einspeisevergütung** und **CO₂-Einsparung**, sofern im Portal hinterlegt
- 🔁 **Einstellbares Aktualisierungsintervall** direkt in Home Assistant
- 🌍 Oberfläche in Englisch, Deutsch, Niederländisch, Portugiesisch, Polnisch, Russisch und Chinesisch
- 🧩 Über **HACS** installierbar
- 🔌 Entwickelt für Envertech ECO-/SE-Wechselrichter, z. B. 2000SE

## 📦 Installation

### HACS · empfohlen

[![Diese Integration in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jimmybonesde&repository=envertech_solar&category=integration)

1. Öffne **HACS → Integrationen**.
2. Suche nach **Envertech Solar** und installiere die Integration.
3. Starte Home Assistant neu.
4. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
5. Suche nach **Envertech Solar** und gib deine Station-ID ein.

> 💡 Ein benutzerdefiniertes Repository ist nicht erforderlich.

### Manuell

1. Lade dieses Repository herunter oder klone es.
2. Kopiere `custom_components/envertech_solar` nach `config/custom_components/` deiner Home-Assistant-Installation.
3. Starte Home Assistant neu und richte die Integration wie oben beschrieben ein.

## ⚙️ Einrichtung

Die Integration benötigt die **Station-ID** deiner Anlage. Nach der Einrichtung kannst du das Aktualisierungsintervall in der Integration über **⚙️ Konfigurieren** einstellen (Standard: 30 Sekunden; möglich: 10–3.600 Sekunden).

<details>
<summary><strong>🔍 Wo finde ich meine Station-ID?</strong></summary>

1. Öffne das [Envertech Solar Portal](https://www.envertecportal.com/terminal/systemoverview).
2. Klicke auf eines deiner Solarpanels.
3. In der URL steht ein Wert nach `/systemhistory/` und vor `?sn=`:

```text
https://www.envertecportal.com/terminal/systemhistory/03GFF6E15154525DA16901EC7A4541G1?sn=3014511
                                                     └──────── Station-ID ────────┘
```

<img width="400" alt="Im Envertech Portal ein Solarpanel auswählen" src="https://github.com/user-attachments/assets/77d86a11-26fe-4db6-a985-79ca1fdd157b" />

</details>

## 📊 Sensoren

| Icon | Sensor | Portalwert | Einheit | Beschreibung |
| :--: | --- | --- | :--: | --- |
| ☀️ | Aktuelle Leistung | `Power` | W | Momentane Solarleistung |
| ⚡ | Tages-Spitzenleistung | `peak_power_today` | W | Höchster gemessener Leistungswert des laufenden Tages |
| 🏆 | Allzeit-Spitzenleistung | `StrPeakPower` | W | Höchster, vom Portal gemeldeter Leistungswert |
| 📐 | Anlagenleistung | `UnitCapacity` | kWp | Installierte Anlagenleistung |
| 🔋 | Tagesenergie | `UnitEToday` | kWh | Heute erzeugte Energie |
| 🗓️ | Monatsenergie | `UnitEMonth` | kWh | Im aktuellen Monat erzeugte Energie |
| 📆 | Jahresenergie | `UnitEYear` | kWh | Im aktuellen Jahr erzeugte Energie |
| ♾️ | Gesamtenergie | `UnitETotal` | kWh | Ertrag seit Inbetriebnahme |
| 🔌 | Wechselrichtermodell | `InvModel1` | — | Vom Portal gemeldetes Wechselrichtermodell |
| 💶 | Ertrag / Vergütung | `StrIncome` | EUR / PLN | Vergütung, sofern im Portal gepflegt |
| 🌱 | CO₂-Einsparung | `StrCO2` | t | Vom Portal berechnete CO₂-Einsparung |
| 📍 | Startdatum | `CreateTime` | — | Inbetriebnahmezeitpunkt der Anlage |

Die Energie-Sensoren eignen sich besonders für Verlaufskarten und das Home-Assistant-Energie-Dashboard.

## 🖼️ Beispiel

<img width="484" alt="Beispiel eines Envertech-Solar-Dashboards in Home Assistant" src="https://github.com/user-attachments/assets/4d6787c6-ac72-4726-8753-f7537e0836e3" />

Für eine aufgeräumte Ansicht eignen sich:

- **Gauge-Karten** für die aktuelle Leistung
- **Entities-Karten** für Tages-, Monats- und Jahresenergie
- **Grid- oder Vertical-Stack-Karten** für eine kompakte Anlagenübersicht

## ❓ Hilfe & FAQ

**Die Integration erscheint nicht in HACS.**  
Aktualisiere HACS und suche erneut nach **Envertech Solar**. Das Repository muss öffentlich erreichbar sein.

**Die Station-ID ist ungültig.**  
Prüfe, ob du exakt den Teil zwischen `/systemhistory/` und `?sn=` aus der Portal-URL kopiert hast.

**Sensoren zeigen `unknown`.**  
Stelle sicher, dass der Wechselrichter online ist und im Envertech Solar Portal Daten liefert. Prüfe anschließend die Home-Assistant-Protokolle auf Fehlermeldungen.

**Die Werte aktualisieren zu langsam oder zu schnell.**  
Passe das Aktualisierungsintervall über **Einstellungen → Geräte & Dienste → Envertech Solar → ⚙️ Konfigurieren** an.

## 🤝 Mitwirken

Fehlerberichte und Verbesserungsvorschläge sind willkommen:

- 🐛 [Issue erstellen](https://github.com/jimmybonesde/envertech_solar/issues)
- 🔀 [Pull Request öffnen](https://github.com/jimmybonesde/envertech_solar/pulls)
- ⭐ Das Repository markieren, wenn es dir hilft

## 🙏 Credits & Lizenz

Created with ☀️ by **JimmyBones**  
🌐 [JimmyBones.de](https://www.jimmybones.de)

Veröffentlicht unter der [MIT-Lizenz](LICENSE).
