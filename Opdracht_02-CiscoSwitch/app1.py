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
    filename='switch_config.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Functie voor verbinden met de switch
def connect_to_switch(ip, username, password, secret):
    """Verbind met de switch en retourneer een actieve sessie."""
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
        connection.enable()
        logging.info(f'Verbinding met switch {ip} is succesvol!')
        return connection
    except Exception as e:
        logging.error(f'Fout bij verbinden met switch {ip}: {e}')
        raise

# Functie voor VLAN-configuratie
def configure_vlan_and_ports(connection, vlan, description, ip_address, netmask, ports, ip_routing):
    """Configureer VLAN en poorten op de switch."""
    config_commands = [
        f'vlan {vlan}',
        f'name {description}',
    ]
    if ip_address and netmask:  # Layer-3 VLAN
        config_commands.extend([
            f'interface vlan {vlan}',
            f'ip address {ip_address} {netmask}',
            'no shutdown',
        ])
    else:  # Layer-2 VLAN
        config_commands.extend([
            f'interface vlan {vlan}',
            'no shutdown',
        ])

    if ports:
        if "-" in ports:
            start_port, end_port = map(int, ports.split("-"))
            for port in range(start_port, end_port + 1):
                config_commands.extend([
                    f'interface FastEthernet0/{port}',
                    'switchport mode access',
                    f'switchport access vlan {vlan}',
                    'no shutdown',
                ])
        else:
            config_commands.extend([
                f'interface FastEthernet0/{ports}',
                'switchport mode access',
                f'switchport access vlan {vlan}',
                'no shutdown',
            ])

    if "trunk" in description.lower() or "uplink" in description.lower():
        config_commands.extend([
            'interface range FastEthernet0/1 - 24',
            'switchport mode trunk',
            f'switchport trunk allowed vlan {vlan}',
        ])

    if ip_routing:
        config_commands.append('ip routing')

    # Voer de configuratie uit
    logging.info(f'Uitvoeren van configuratiecommando\'s: {config_commands}')
    connection.send_config_set(config_commands)
    logging.info('Configuratie voltooid!')

# Functie om TFTP-server te starten
def start_tftp_server(tftp_root):
    """Start een TFTP-server."""
    if not os.path.exists(tftp_root):
        os.makedirs(tftp_root)

    server = tftpy.TftpServer(tftp_root)
    server_thread = threading.Thread(target=server.listen, kwargs={'listenip': '0.0.0.0', 'listenport': 69})
    server_thread.daemon = True
    server_thread.start()
    logging.info(f'TFTP-server gestart en luistert in {tftp_root}')

# Functie om configuratie te downloaden via TFTP
def download_switch_config(connection, tftp_server_ip, filename):
    """Download de configuratie van de switch naar een TFTP-server."""
    try:
        connection.send_command(f'copy running-config tftp://{tftp_server_ip}/{filename}', expect_string=r'#')
        logging.info(f'Configuratie succesvol gedownload naar TFTP-server: {tftp_server_ip}/{filename}')
    except Exception as e:
        logging.error(f'Fout bij het downloaden van de configuratie: {e}')

# Functie voor het configureren van switches op basis van CSV
def configure_switch(csv_file, username, password, secret, tftp_server_ip, tftp_root):
    """Lees een CSV-bestand en configureer switches."""
    with open(csv_file, mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=";")
        data = list(csv_reader)

    ip_routing = any(row["IP Address"] for row in data)

    start_tftp_server(tftp_root)

    for row in data:
        vlan = row["Vlan"]
        description = row["Description"]
        ip_address = row["IP Address"]
        netmask = row["Netmask"]
        switch_ip = row["Switch"]
        ports = row["Ports"]

        switch_host = f"192.168.1.{switch_ip}"

        try:
            # Maak verbinding met de switch
            connection = connect_to_switch(switch_host, username, password, secret)

            # Configureer VLAN en poorten
            configure_vlan_and_ports(connection, vlan, description, ip_address, netmask, ports, ip_routing)

            # Download configuratie naar TFTP-server
            filename = f'switch_{switch_ip}_config.cfg'
            download_switch_config(connection, tftp_server_ip, filename)

            # Sluit de verbinding met de switch
            connection.disconnect()
            logging.info(f'Verbinding met switch {switch_host} afgesloten.')

        except Exception as e:
            logging.error(f'Fout bij configureren van switch {switch_host}: {e}')

# Hoofdfunctie
if __name__ == "__main__":
    csv_file = 'BST-D-1-242.csv'  # Pad naar je CSV-bestand
    username = 'admin'  # SSH gebruikersnaam (met admin-rechten)
    password = 'Tibo1234!'  # SSH wachtwoord
    secret = 'secret'  # Enable wachtwoord
    tftp_server_ip = '192.168.1.2'  # IP-adres van de TFTP-server
    tftp_root = 'tftp'  # Pad voor TFTP-bestanden

    configure_switch(csv_file, username, password, secret, tftp_server_ip, tftp_root)
