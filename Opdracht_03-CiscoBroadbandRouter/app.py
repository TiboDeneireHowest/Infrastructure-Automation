import csv
import os

def parse_csv(csv_file, delimiter=';'):
    """
    Parse the CSV file and return the rows as a list of dictionaries.
    """
    try:
        with open(csv_file, 'r') as file:
            return list(csv.DictReader(file, delimiter=delimiter))
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        raise
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        raise


def configure_interface(interface, description, vlan, ip_address, subnetmask):
    """
    Generate configuration for an interface.
    """
    try:
        config = [f"interface {interface}"]
        if description:
            config.append(f" description {description}")
        if vlan and int(vlan) != 0:
            config.append(f" encapsulation dot1Q {vlan}")
        if ip_address:
            config.append(
                " ip address dhcp" if ip_address.lower() == 'dhcp' else f" ip address {ip_address} {subnetmask}")
        config.append(" no shutdown")
        config.append(" exit")
        return config
    except ValueError as e:
        print(f"Error: Invalid VLAN value '{vlan}' for interface {interface}.")
        raise
    except Exception as e:
        print(f"An error occurred while configuring the interface {interface}: {e}")
        raise


def configure_vlan(vlan, description):
    """
    Generate configuration for a VLAN.
    """
    try:
        config = [f"vlan {vlan}"]
        if description:
            config.append(f" name {description}")
        config.append(" exit")
        return config
    except Exception as e:
        print(f"An error occurred while configuring VLAN {vlan}: {e}")
        raise


def configure_nat(network, interface):
    """
    Generate NAT configuration for WAN or LAN networks.
    """
    try:
        if network.lower() == 'wan' and interface:
            return [f"interface {interface}", " ip nat outside", " exit"]
        elif network.lower() == 'lan' and interface:
            return [f"interface {interface}", " ip nat inside", " exit"]
        return []
    except Exception as e:
        print(f"An error occurred while configuring NAT for {network}: {e}")
        raise


def configure_static_route(ip_address, subnetmask, default_gateway):
    """
    Generate static route configuration.
    """
    try:
        if ip_address and subnetmask and default_gateway:
            network_address = f"{ip_address}/{subnetmask}"
            return [f"ip route {network_address} {default_gateway}"]
        return []
    except Exception as e:
        print(f"An error occurred while configuring static route: {e}")
        raise


def generate_cisco_config(csv_file, output_file):
    """
    Generate Cisco configuration commands based on a CSV file.
    """
    try:
        rows = parse_csv(csv_file)
        config_lines = []

        for row in rows:
            network = row.get('network', '')
            interface = row.get('interface', '')
            description = row.get('description', '')
            vlan = row.get('vlan', '0')
            ip_address = row.get('ipaddress', '')
            subnetmask = row.get('subnetmask', '')
            default_gateway = row.get('defaultgateway', '')

            if interface:
                config_lines.extend(configure_interface(interface, description, vlan, ip_address, subnetmask))

            if not interface and vlan and int(vlan) != 0:
                config_lines.extend(configure_vlan(vlan, description))

            config_lines.extend(configure_nat(network, interface))

            if default_gateway:
                config_lines.extend(configure_static_route(ip_address, subnetmask, default_gateway))

        # Add NAT overload configuration
        config_lines.extend([
            "access-list 1 permit any",
            "ip nat inside source list 1 interface gi0/0 overload"
        ])

        # Ensure the directory exists before writing to the output file
        # Check if output_file includes a path or not
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write to the output file
        with open(output_file, 'w') as output:
            output.write("\n".join(config_lines))

        print(f"Configuration generated and saved to {output_file}")

    except Exception as e:
        print(f"An error occurred while generating the Cisco configuration: {e}")
        raise


if __name__ == "__main__":
    # Path to CSV file and output file
    csv_file = "config.csv"  # Replace with your CSV file
    output_file = "cisco_config.txt"  # This is just the filename, change if you want a specific path

    # Generate configuration
    generate_cisco_config(csv_file, output_file)
