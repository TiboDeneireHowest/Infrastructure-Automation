import requests
import time
import argparse
import os
from requests.exceptions import RequestException
import subprocess

# **Configureer de SSID en het wachtwoord hier bovenaan**
SSID = "Howest-IoT"  # Pas dit aan naar de gewenste SSID
MAX_POWER = 2200
DEFAULT_STATE="off"
led_status_disable="true"
mqtt_enable = "true"
mqtt_server = "172.23.83.254:1883"
wifi_ap_enabled = "false"
wifi_sta_enabled = True
wifi_ip_method = "dhcp"
# read password from file
with open("password2.txt", "r") as file:
    WIFI_PASSWORD = file.read()
    print(f"Password: {WIFI_PASSWORD}")


# Functie om te communiceren met de Shelly Smart Plug API
def send_post_request(url, data):
    try:
        # Data als `x-www-form-urlencoded` payload versturen
        response = requests.post(url, data=data, timeout=10)
        print(f"Verzonden naar {url} met status: {response.status_code}")
        if response.status_code == 200:
            print(f"Succesvol verzonden naar {url}")
        else:
            print(f"Fout bij het verzenden naar {url}: {response.status_code}, Response: {response.text}")
    except RequestException as e:
        print(f"Fout tijdens communicatie met {url}: {e}")

# Functie om de Shelly plug te configureren
def configure_shelly_plug(ip, family_name, first_name, outlet_number, cloud_enabled, mqtt_broker_ip):
    plug_name = f"{family_name}-{first_name}-Outlet{outlet_number}"
    
    # 1. Naam van de plug instellen
    send_post_request(f"http://{ip}/settings/device/", data=f"name={plug_name}")

    # 2. Zet de plug uit bij herstart
    send_post_request(f"http://{ip}/settings/relay/0", data=f"power_on_state={DEFAULT_STATE}")  

    # 3. Zet alle LED's uit
    send_post_request(f"http://{ip}/settings/relay/0", data=f"led_status={DEFAULT_STATE}")  

    # 4. Zet de maximum belasting in op 2200W
    send_post_request(f"http://{ip}/settings/relay/0", data=f'max_power={MAX_POWER}')

    # 5. MQTT configuratie
    send_post_request(f"http://{ip}/settings/mqtt", data=f'mqtt_enable={mqtt_enable}')
    send_post_request(f"http://{ip}/settings/mqtt", data=f'mqtt_server={mqtt_broker_ip}')
    send_post_request(f"http://{ip}/settings/mqtt", data=f'mqtt_id={plug_name}')
    send_post_request(f"http://{ip}/settings/mqtt", data=f'mqtt_id={plug_name}')
    #send_post_request(f"http://{ip}/settings/mqtt", data=f"user=")  # Lege waarde voor user
    #send_post_request(f"http://{ip}/settings/mqtt", data=f"password=")  # Lege waarde voor password

    # 6. Cloud instellen
    send_post_request(f"http://{ip}/settings/coiot", data=f'enabled=false')

    # 7. Zet de maximum belasting in op 2200W
    send_post_request(f"http://{ip}/settings", data="max_power=2200")

    # 8. Uitschakelen van niet gebruikte services
    
    send_post_request(f"http://{ip}/settings/sntp", data=f'enabled=false')


    # 9. Wi-Fi configuratie
    json = {"ssid": SSID, "key": WIFI_PASSWORD, "ipv4_method": wifi_ip_method, "enabled": wifi_sta_enabled}

    send_post_request(f"http://{ip}/settings/sta", data=json)
   

    print(f"Configuratie voltooid voor {plug_name}!")

# Functie om alle beschikbare Wi-Fi-netwerken te scannen op Windows
def scan_wifi_networks():
    print("Scannen van beschikbare Wi-Fi-netwerken...")

    # Voer een netsh commando uit om netwerken te scannen
    result = subprocess.run(['netsh', 'wlan', 'show', 'network'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Verkrijg de output van het scancommando
    output = result.stdout.decode()

    # Zoek naar netwerken die "Shelly" in de naam bevatten
    shelly_aps = []
    for line in output.splitlines():
        if "SSID" in line and "shellyplug" in line:  # Zoek naar netwerken met 'Shelly' in de naam
            ssid = line.split(":")[1].strip()
            shelly_aps.append(ssid)

    return shelly_aps
# Functie om te verbinden met een specifieke Shelly plug via zijn AP modus
def add_wifi_profile(shellyplug, password):
    wifi_profile = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
        <name>{shellyplug}</name>
        <SSIDConfig>
            <SSID>
                <name>{shellyplug}</name>
            </SSID>
        </SSIDConfig>
        <connectionType>ESS</connectionType>
        <connectionMode>auto</connectionMode>
        <authentication>WPAPSK</authentication>
        <encryption>TKIP</encryption>
        <sharedKey>
            <keyType>passPhrase</keyType>
            <protected>false</protected>
            <keyMaterial>{password}</keyMaterial>
        </sharedKey>
    </WLANProfile>
    """
    # Sla het profiel op in een tijdelijk XML-bestand
    with open("temp_wifi_profile.xml", "w") as file:
        file.write(wifi_profile)

    # Voeg het profiel toe aan Windows Wi-Fi-profielen
    result = subprocess.run(
        ['netsh', 'wlan', 'connect', f'name={shellyplug}', 'interface', 'Wi-Fi'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        print(f"Profiel voor {shellyplug} succesvol toegevoegd.")
    else:
        print(f"Fout bij het toevoegen van Wi-Fi-profiel voor {shellyplug}: {result.stderr.decode()}")

    # Verwijder tijdelijk het profielbestand
    os.remove("temp_wifi_profile.xml")


# Functie om te verbinden met een specifieke Shelly plug via zijn AP modus
def connect_to_shelly(shellyplug):
    print(f"Probeer verbinding te maken met Shelly AP netwerk: {shellyplug}")

    # Voeg eerst het Wi-Fi-profiel toe (indien nog niet toegevoegd)
    add_wifi_profile(shellyplug, "")

    # Wacht even om te zorgen dat het profiel correct is toegevoegd
    time.sleep(3)

    # Verbinden met Shelly plug via de juiste netwerkinterface
    result = subprocess.run(
        ['netsh', 'wlan', 'connect', f'name={shellyplug}', 'interface=Wi-Fi'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        print(f"Succesvol verbonden met {shellyplug}")
    else:
        print(f"Fout bij verbinding met {shellyplug}: {result.stderr.decode()}")
        print(f"stdout: {result.stdout.decode()}")

    # Wacht 5 seconden om de verbinding te stabiliseren
    time.sleep(5)

    # Controleer of de verbinding succesvol is
    check_connection = subprocess.run(
        ['ping', '-n', '1', '192.168.33.1'],  # Shelly IP in AP-modus
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if check_connection.returncode == 0:
        print("Verbonden met Shelly-plug IP (192.168.33.1)")
        return True
    else:
        print("Geen reactie van Shelly-plug na verbinding.")
        return False

# Functie om te zoeken naar Shelly-pluggen in AP-modus
def search_to_shelly_ap():
    print("Zoeken naar Shelly plug in AP modus...")
    shelly_aps = scan_wifi_networks()
    print(f"Gevonden Shelly-pluggen: {shelly_aps}")
    return shelly_aps

# Functie voor het verwerken van commandoregelargumenten
def parse_args():
    parser = argparse.ArgumentParser(
        description="Configureer Shelly Smart Plug na factory default")
    parser.add_argument("--family", required=True, help="Familienaam")
    parser.add_argument("--first_name", required=True, help="Voornaam")
    parser.add_argument("--cloud", default=False, action='store_true', help="Cloudverbinding in- of uitschakelen")
    parser.add_argument("--mqtt_broker", default="172.23.83.254", help="IP van de MQTT broker")
    return parser.parse_args()

# Hoofdprogramma
def main():
    # Verkrijg de argumenten
    args = parse_args()

    # Verbinden met de Shelly plug in AP-modus
    shellyplugs = search_to_shelly_ap()
    if not shellyplugs:
        print("Geen Shelly plug gevonden in AP-modus.")
        return

    # Voor elke gevonden Shelly-plug, probeer verbinding te maken en configureer deze
    outlet_number = 1  # Begin met Outlet1
    for shellyplug in shellyplugs:
        if connect_to_shelly(shellyplug):
            shelly_ip = "192.168.33.1"  # Standaard IP voor Shelly AP-modus
            configure_shelly_plug(
                ip=shelly_ip,
                family_name=args.family,
                first_name=args.first_name,
                outlet_number=outlet_number,
                cloud_enabled=args.cloud,
                mqtt_broker_ip=args.mqtt_broker
            )
            outlet_number += 1  # Verhoog het outlet-nummer voor de volgende plug

if __name__ == "__main__":
    main()