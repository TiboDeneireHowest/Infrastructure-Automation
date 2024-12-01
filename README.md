# Infrastructure-Automation

# Opdacht_01-Powershell

## Overview

`customize_firstrun.ps1` is a PowerShell script designed to automate the process of customizing the `firstrun.sh` script on an SD card's boot partition. The script performs the following tasks:

1. Detects the boot partition labeled `bootfs` of a mounted SD card.
2. Modifies the `firstrun.sh` script by inserting a custom network configuration.
3. Creates a backup of the original `firstrun.sh` file.
4. Ensures that the `firstrun.sh` file is converted to Linux format using `dos2unix`.

This script is particularly useful when preparing SD cards for Linux-based systems, where a first-run script is commonly used for initial configuration.

## Prerequisites

Before running the script, ensure the following:

1. **SD Card Mounted**: The SD card with the boot partition labeled `bootfs` should be mounted on your system.
2. **PowerShell**: The script is intended to be run in a Windows PowerShell environment.
3. **dos2unix Tool**: You must have the `dos2unix.exe` tool installed. The script assumes the tool is available at the path `C:\path\to\dos2unix.exe`. Modify this path in the script if necessary.

## Features

- **Backup Creation**: The script creates a backup of `firstrun.sh` before making any changes to prevent accidental data loss.
- **Network Configuration Insertion**: A predefined network configuration block for `MCT_APIPA` is inserted into `firstrun.sh` before the first `rm -f` command, ensuring that it is added correctly without disturbing the script's flow.
- **Linux Format Conversion**: The script ensures that the `firstrun.sh` file is in Linux-compatible format by converting it using the `dos2unix` utility.

## Usage

1. **Run the Script**: Open PowerShell as an Administrator and run the script.
   ```powershell
   .\customize_firstrun.ps1
   ```

# Switch Configuratie Automatiseringsscript layer 2 & 3

Dit Python-script automatiseert het configureren van netwerk-switches door gebruik te maken van gegevens uit een CSV-bestand. Het configureert VLAN's (zowel Layer-2 als Layer-3), trunk-poorten, management-IP's en andere instellingen. Het ondersteunt ook het downloaden van configuratiebestanden naar een TFTP-server.

---

## **Functionaliteiten**

1. **Automatische VLAN-configuratie**:
   - Layer-2 VLAN's met bijbehorende poorten.
   - Layer-3 VLAN's met IP-adressen en subnetmaskers.
2. **Trunk-poorten configuratie**:
   - Ondersteunt VLAN-filtering.
3. **Management VLAN Configuratie**:
   - Stelt het management-IP en de default gateway in.
4. **TFTP-server**:
   - Start een TFTP-server en slaat de configuratiebestanden van switches op.
5. **Logboekregistratie**:
   - Houdt activiteiten en fouten bij in een logbestand (`switch_config.log`).

---

## **Benodigdheden**

- Python 3.7+
- Bibliotheken:
  - `netmiko`
  - `tftpy`
- Een CSV-bestand met de volgende velden:
  - **Vlan**: Het VLAN-nummer.
  - **Description**: Beschrijving van het VLAN.
  - **IP Address**: IP-adres (voor Layer-3 VLAN's of management).
  - **Netmask**: Subnetmasker (voor Layer-3 VLAN's of management).
  - **Ports**: Poorten die aan het VLAN zijn toegewezen (bijvoorbeeld `1-4`).
  - **Switch**: Laatste segment van het IP-adres van de switch.
  - **vlan filtering** *(optioneel)*: Lijst van toegestane VLAN's voor trunk-poorten (bijvoorbeeld `10,20,30`).

---

## **Voorbeeld CSV**

```csv
Vlan,Description,IP Address,Netmask,Ports,Switch,vlan filtering
1982,CD-WIFI,,,1-4,1,
100,Management,192.168.1.100,255.255.255.0,,2,
101,Uplink,,,1-2,2,100,101,102
```

## **Hoe te gebruiken**

### **1. Installeer de benodigde bibliotheken**

Voer de volgende opdracht uit om de benodigde bibliotheken te installeren:

```bash
pip install netmiko tftpy
```
### **2. Start het script**
Zorg ervoor dat je een CSV-bestand hebt met de juiste gegevens. Start het script met:

```bash
python script.py
```
---

### **3. Aanpassen van variabelen**

Pas de volgende variabelen in het script aan:

- **`csv_file`**: Pad naar je CSV-bestand.
- **`tftp_server_ip`**: IP-adres van de machine waarop de TFTP-server draait.
- Andere benodigde configuratieparameters zoals **`username`**, **`password`**, en **`secret`**.

---
### **4. Logs**

Controleer de logbestanden (**`switch_config.log`**) voor fouten en statusupdates.

---

# Shelly Smart Plug Configurator

Dit Python-script configureert Shelly Smart Plugs die in AP-modus staan, door via hun lokale netwerk een aantal instellingen te wijzigen. Het script kan verschillende configuraties toepassen, zoals het instellen van de naam, de relaisstatus, MQTT-instellingen, Wi-Fi-instellingen en nog veel meer.

## Functies van het Script

- **Configureren van de Shelly Smart Plug**: Het script configureert de Shelly plug met een specifieke naam, relaisstatus, MQTT-instellingen en andere vereiste parameters.
- **Wi-Fi Configuratie**: Verbindt de Shelly plug met een opgegeven Wi-Fi-netwerk.
- **MQTT**: Stelt de plug in om gegevens via een MQTT-broker te verzenden.
- **Cloud Configuratie**: Schakelt de cloudverbinding in of uit, afhankelijk van de opgegeven argumenten.
- **Scannen naar Shelly-apparaten**: Het script kan zoeken naar Shelly-apparaten in AP-modus binnen het lokale netwerk.

## Benodigde Bestanden

Het script leest de Wi-Fi-wachtwoorden uit een bestand genaamd **`password.txt`**. Dit bestand moet de tekst bevatten van het wachtwoord dat je wilt gebruiken om verbinding te maken met je Wi-Fi-netwerk.

### Voorbeeld van `password.txt`:

```
JeWiFiWachtwoord
```

Zorg ervoor dat je dit bestand aanmaakt en in dezelfde directory plaatst als het script.

## Benodigde Bibliotheken

Dit script maakt gebruik van de volgende Python-pakketten:

- `requests` - Voor het communiceren met de Shelly API.
- `argparse` - Voor het verwerken van commandoregelargumenten.
- `subprocess` - Voor het uitvoeren van systeemcommando's (zoals het verbinden met Wi-Fi).
- `time` - Voor wachttijden tussen acties.

Installeer de benodigde bibliotheken met pip:

```bash
pip install requests
```

## Commandoregelargumenten

Het script accepteert de volgende argumenten via de commandoregel:

- `-family` (vereist): De familienaam die aan de plug wordt toegewezen.
- `-first_name` (vereist): De voornaam die aan de plug wordt toegewezen.
- `-cloud` (optie): Schakelt de cloudverbinding in voor de plug (standaard is dit uitgeschakeld).
- `-mqtt_broker` (optie): Het IP-adres van de MQTT-broker (standaard is `172.23.83.254`).

### Voorbeeld van het gebruik van het script

Om het script uit te voeren, gebruik je het volgende commando:

```bash
python configure_shelly.py --family "Achternaam" --first_name "Voornaam" --cloud --mqtt_broker "172.23.83.254
```

Dit zal de Shelly-plug configureren met de naam `Achternaam-Voornaam-Outlet1` en de cloudverbinding inschakelen, terwijl de MQTT-broker wordt ingesteld op `172.23.83.254`.

## Werking

1. **Verbinding maken met de Shelly Plug**: Het script zoekt naar beschikbare Shelly-apparaten in AP-modus via Wi-Fi en verbindt zich automatisch met het juiste apparaat.
2. **Configuratie van de Shelly Plug**: Nadat de verbinding is gemaakt, configureert het script de plug door de opgegeven instellingen toe te passen (zoals de naam, MQTT-configuratie, Wi-Fi-instellingen, enzovoort).
3. **Wachtwoord**: Het script leest het Wi-Fi-wachtwoord uit de **`password.txt`**file en gebruikt dit om verbinding te maken met het netwerk.

## Opmerkingen

- Zorg ervoor dat je de juiste Wi-Fi-netwerkinstellingen hebt (SSID en wachtwoord) en dat je toegang hebt tot de Shelly plug in AP-modus.
- Het IP-adres van de Shelly-plug in AP-modus is standaard `192.168.33.1`. Het script gebruikt dit IP-adres voor de configuratie.
- Het script maakt gebruik van `netsh` om Wi-Fi-profielen toe te voegen en verbinding te maken met de Shelly-plug. Dit werkt alleen op Windows-systemen.

## Problemen oplossen

- **Geen Shelly-plug gevonden**: Het script kan de plug mogelijk niet vinden als deze niet in AP-modus staat of als er een probleem is met de Wi-Fi-configuratie.
- **Verbindingsproblemen**: Controleer of je apparaat verbonden is met hetzelfde netwerk en dat er geen firewalls of netwerkbeperkingen zijn die de communicatie met de Shelly-plug blokkeren.

## Licentie

Dit project is beschikbaar onder de MIT-licentie. Zie het bestand `LICENSE` voor meer informatie.