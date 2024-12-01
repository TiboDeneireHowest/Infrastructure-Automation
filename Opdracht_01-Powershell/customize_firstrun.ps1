#customize_firstrun.ps1
# This script detects the boot partition of a mounted SD card, modifies 'firstrun.sh', and ensures the file remains in Linux format.

# Locate the partition with the label 'bootfs' (the boot partition)
$bootPartition = Get-Volume | Where-Object { $_.FileSystemLabel -eq "bootfs" }

if (-not $bootPartition) {
    Write-Output "Boot partition labeled 'bootfs' was not found. Ensure the SD card is mounted and try again."
    exit
}

# Define the path to the boot partition
$bootPath = $bootPartition.DriveLetter + ":\"

# Step 1: Define the Downloads folder path
##$downloadsPath = [System.IO.Path]::Combine([System.Environment]::GetFolderPath("UserProfile"), "Downloads")

# Step 2: Search for the 'bootfs' folder within Downloads
##$bootfsPath = Get-ChildItem -Path $downloadsPath -Directory -Recurse | Where-Object { $_.Name -eq "bootfs" }

##if (-not $bootfsPath) {
##    Write-Output "No 'bootfs' folder found in the Downloads directory. Please check if the folder exists and try again."
##    exit
##}

# Define the full path to the bootfs folder
##$bootPath = $bootfsPath.FullName

# Check if the 'firstrun.sh' file exists and create a backup
$firstrunFile = Join-Path -Path $bootPath -ChildPath "firstrun.sh"
$backupFile = Join-Path -Path $bootPath -ChildPath "firstrun_backup.sh"

if (Test-Path -Path $firstrunFile) {
    Copy-Item -Path $firstrunFile -Destination $backupFile -Force
    Write-Output "Backup of 'firstrun.sh' created as 'firstrun_backup.sh'."
} else {
    Write-Output "'firstrun.sh' not found on the boot partition. Please check the file and try again."
    exit
}

# Read the contents of 'firstrun.sh'
$firstrunContent = Get-Content -Path $firstrunFile -Raw

# Define the custom network configuration block
$networkConfig = @"

# Network configuration for MCT_APIPA
cat >/etc/NetworkManager/system-connections/MCT_APIPA.nmconnection <<'MCT_APIPA'
[connection]
id=MCT_APIPA
type=ethernet
interface-name=eth0
[ethernet]
[ipv4]
method=link-local
[ipv6]
addr-gen-mode=default
method=disabled
[proxy]
MCT_APIPA
chmod 0600 /etc/NetworkManager/system-connections/*
chown root:root /etc/NetworkManager/system-connections/*
# End of network configuration

"@

# Insert the network configuration before any 'rm -f' line in 'firstrun.sh'
if ($firstrunContent -notmatch [regex]::Escape($networkConfig)) {
    # Find the position to insert the configuration just before 'rm -f'
    $firstrunContent = $firstrunContent -replace "(?<=`n)(rm -f /boot/firstrun.sh
*)", "$networkConfig`n$1"

    # Write the updated content back to 'firstrun.sh'
    Set-Content -Path $firstrunFile -Value $firstrunContent -Force
    Write-Output "Network configuration has been added before the 'rm -f /boot/firstrun.sh' command in 'firstrun.sh'."
} else {
    Write-Output "Network configuration already exists in 'firstrun.sh'. No changes made."
}


# Convert the file to Linux format
# Ensure 'dos2unix' is available
$dos2unixPath = "C:\path\to\dos2unix.exe"  # Adjust this path to the location of dos2unix.exe


if (Test-Path -Path $dos2unixPath) {
    & $dos2unixPath $firstrunFile
    Write-Output "'firstrun.sh' has been successfully converted to Linux file format."
} else {
    Write-Output "Warning: dos2unix not found on this system. Ensure it is installed and try again."
}