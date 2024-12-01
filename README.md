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
