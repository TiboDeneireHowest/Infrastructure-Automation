import csv
import time
import logging
import threading
import os
from netmiko import ConnectHandler
from datetime import datetime
import tftpy

# Configuratie van logging
logging.basicConfig(
    filename='switch_config.log',  # Logbestandnaam
    level=logging.DEBUG,  # Minimum loggingniveau (DEBUG voor alles)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Logformaat
)

# Zet het pad voor het TFTP-downloadpad in
TFTP_DIR = 'tftp'

# Zorg ervoor dat de map bestaat
if not os.path.exists(TFTP_DIR):
    os.makedirs(TFTP_DIR)

# Zet de TFTP-server op
def start_tftp_server():
    print("Starting TFTP server...")
    server = tftpy.TftpServer(TFTP_DIR)
    server.listen('0.0.0.0', 69)  # Luistert op alle interfaces, poort 69 voor TFTP

# Functie om verbinding te maken met de switch
def connect_to_switch(ip, username, password, secret):
    try:
        logging.info(f'Verbinden met switch: {ip}')
        device = {
            'device_type': 'cisco_ios',
            'host': ip,
            'username': username,
            'password': password,
            'secret': secret,
        }
        connection = ConnectHandler(**device)
        connection.enable()  # Ga naar de enable modus
        logging.info(f'Verbinding met switch {ip} is succesvol!')
        return connection
    except Exception as e:
        logging.error(f'Fout bij verbinden met switch {ip}: {e}')
        raise

# Functie om Layer-2 VLAN te configureren
def configure_layer2_vlan(vlan, description, ports):
    logging.info(f'Configureren Layer-2 VLAN {vlan} met beschrijving "{description}"')
    config_commands = []

    # Controleer of VLAN bestaat en maak het indien nodig aan
    config_commands.append(f'vlan {vlan}')
    config_commands.append(f'name {description}')
    
    # Splits de poorten en configureer deze
    for port in ports.split('-'):
        config_commands.append(f'interface {port}')
        config_commands.append('switchport mode access')
        config_commands.append(f'switchport access vlan {vlan}')

    logging.debug(f'Layer-2 VLAN configuratie commando\'s: {config_commands}')
    return config_commands

# Functie om Layer-3 VLAN te configureren
def configure_layer3_vlan(vlan, description, ip_address, subnetmask):
    logging.info(f'Configureren Layer-3 VLAN {vlan} met IP {ip_address}/{subnetmask}')
    config_commands = [
        f'vlan {vlan}',
        f'name {description}',
        f'interface vlan {vlan}',
        f'ip address {ip_address} {subnetmask}',
        'no shutdown',  # Zorg ervoor dat de interface aan staat
    ]
    logging.debug(f'Layer-3 VLAN configuratie commando\'s: {config_commands}')
    return config_commands

# Functie om de default gateway in te stellen
def configure_gateway(gateway_ip):
    logging.info(f'Instellen van default gateway: {gateway_ip}')
    return [f'ip default-gateway {gateway_ip}']

# Functie om de management VLAN IP te configureren
def configure_management_ip(ip_address, subnetmask):
    logging.info(f'Configureren van management IP {ip_address}/{subnetmask}')
    return [
        'interface vlan 1',  # Typisch is VLAN 1 het management VLAN
        f'ip address {ip_address} {subnetmask}',
        'no shutdown',
    ]

# Functie om VLAN filtering in trunk poorten in te stellen
def configure_trunk(ports, vlan_filtering):
    logging.info(f'Configureren van trunk-poorten: {ports} met VLAN filtering: {vlan_filtering}')
    config_commands = []
    for port in ports.split(','):
        config_commands.append(f'interface {port}')
        config_commands.append('switchport mode trunk')
        config_commands.append(f'switchport trunk allowed vlan {vlan_filtering}')
    logging.debug(f'Trunk configuratie commando\'s: {config_commands}')
    return config_commands

# Functie om TFTP-server te starten en configuratie te downloaden
def start_tftp_and_download_config(connection, tftp_server_ip, filename):
    logging.info(f'Configureren van TFTP-server voor configuratiedownload: {tftp_server_ip}/{filename}')
    try:
        connection.send_command(f'copy running-config tftp://{tftp_server_ip}/{filename}', expect_string=r'#')
        logging.info(f'Configuratie succesvol gedownload naar TFTP-server: {tftp_server_ip}/{filename}')
    except Exception as e:
        logging.error(f'Fout bij het downloaden van de configuratie naar TFTP-server: {e}')

# CSV-bestand inlezen en configureren
def configure_switch_from_csv(csv_file, username, password, secret, tftp_server_ip):
    try:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file, delimiter=';')  # Gebruik puntkomma als scheidingsteken
            logging.info(f'Starten met configureren van switches uit CSV-bestand: {csv_file}')

            for row in csv_reader:
                try:
                    vlan = row['Vlan'].strip()
                    description = row['Description'].strip()
                    ip_address = row.get('IP Address', '').strip()
                    subnetmask = row.get('Netmask', '').strip()
                    ports = row.get('Ports', '').strip()
                    switch_id = row['Switch'].strip()
                    vlan_filtering = row.get('vlan filtering', '').strip()

                    # IP-adres van de switch instellen
                    switch_ip = f"192.168.1.{switch_id}"

                    # Maak verbinding met de switch
                    connection = connect_to_switch(switch_ip, username, password, secret)

                    # Configureer VLAN afhankelijk van de aanwezigheid van IP-gegevens
                    all_config_commands = []
                    if ip_address and subnetmask:  # Layer-3 VLAN
                        all_config_commands.extend(configure_layer3_vlan(vlan, description, ip_address, subnetmask))
                    else:  # Layer-2 VLAN
                        all_config_commands.extend(configure_layer2_vlan(vlan, description, ports))

                    # Configureer management VLAN en gateway indien van toepassing
                    if 'management' in description.lower():
                        all_config_commands.extend(configure_management_ip(ip_address, subnetmask))
                        gateway_ip = ip_address.rsplit('.', 1)[0] + '.1'
                        all_config_commands.extend(configure_gateway(gateway_ip))

                    # Trunk configuratie (indien nodig)
                    if vlan_filtering:
                        all_config_commands.extend(configure_trunk(ports, vlan_filtering))

                    # Verstuur configuratie naar de switch
                    connection.send_config_set(all_config_commands)
                    logging.info(f'Configuratie succesvol uitgevoerd op switch {switch_ip}')

                    # Start TFTP-server en download configuratie
                    start_tftp_and_download_config(connection, tftp_server_ip, f'switch_config_{switch_id}.cfg')

                    # Sluit de verbinding met de switch
                    connection.disconnect()
                    logging.info(f'Verbinding met switch {switch_ip} afgesloten')

                except Exception as e:
                    logging.error(f'Fout bij configureren van switch met ID {switch_id}: {e}')

    except Exception as e:
        logging.error(f'Fout bij het verwerken van het CSV-bestand: {e}')

# Hoofdfunctie
if __name__ == "__main__":
    # Start TFTP-server in een aparte thread
    tftp_thread = threading.Thread(target=start_tftp_server, daemon=True)
    tftp_thread.start()

    csv_file = 'BST-D-1-242.csv'  # Pad naar je CSV-bestand
    username = 'username'  # SSH gebruikersnaam (met admin-rechten)
    password = 'password'  # SSH wachtwoord
    secret = 'secret'  # Enable wachtwoord
    tftp_server_ip = '192.168.1.2'  # IP-adres van de TFTP-server
    
    # Start de configuratie
    configure_switch_from_csv(csv_file, username, password, secret, tftp_server_ip)
