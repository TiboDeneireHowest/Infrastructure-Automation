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

# **Switch Configuratie Automatiseringsscript layer 2 & 3**

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