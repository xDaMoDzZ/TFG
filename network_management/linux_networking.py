import subprocess
import sys
import re # For regular expressions

# --- Helper function for command execution (_run_command) ---
def _run_command(command, check_success=True, capture_output=True, shell=False):
    """
    Executes a system command and handles its output and errors.
    (Same helper function as above, duplicated for self-contained files)
    """
    try:
        result = subprocess.run(
            command,
            check=check_success,
            capture_output=capture_output,
            text=True,
            shell=shell
        )
        return result
    except FileNotFoundError:
        cmd_name = command[0] if isinstance(command, list) else command.split()[0]
        print(f"Error: Command '{cmd_name}' not found. Make sure it's installed and in your PATH.", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        print(f"STDOUT: {e.stdout.strip()}", file=sys.stderr)
        print(f"STDERR: {e.stderr.strip()}", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None
    except Exception as e:
        print(f"Unexpected error when executing command: {e}", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None

# --- Networking Functions ---

def get_network_interfaces():
    """Lists available network interfaces."""
    print("Listing network interfaces...")
    # Using 'ip a' which is standard on modern Linux systems
    result = _run_command(["ip", "a"])
    if result and result.returncode == 0:
        interfaces = []
        # Regex to find interface names (e.g., 1: lo: <LOOPBACK,UP,LOWER_UP> or 2: eth0: <BROADCAST,MULTICAST,UP)
        matches = re.findall(r"^\d+: ([a-zA-Z0-9]+):", result.stdout, re.MULTILINE)
        if matches:
            for iface in matches:
                # Exclude loopback unless explicitly needed
                if iface != "lo":
                    interfaces.append(iface)
            print("Available interfaces:")
            for iface in interfaces:
                print(f"- {iface}")
            return interfaces
        else:
            print("No network interfaces found.")
            return []
    elif result:
        print(f"Failed to list interfaces. Exit code: {result.returncode}", file=sys.stderr)
        return []
    return []

def set_static_ip(interface, ip_address, netmask, gateway, dns_servers=None):
    """Sets a static IP address for a network interface."""
    print(f"Attempting to set static IP {ip_address}/{netmask} on {interface}...")
    
    # Example using 'ip' command for temporary setting
    # For persistent setting, network manager config files should be edited (e.g., /etc/netplan for Ubuntu, /etc/sysconfig/network-scripts for CentOS)
    # This example focuses on immediate application via 'ip' commands.
    
    # Bring down interface
    _run_command(["sudo", "ip", "link", "set", interface, "down"], check_success=False)
    
    # Set IP address and netmask
    result_ip = _run_command(["sudo", "ip", "addr", "add", f"{ip_address}/{netmask}", "dev", interface])
    
    # Bring up interface
    _run_command(["sudo", "ip", "link", "set", interface, "up"], check_success=False)

    if result_ip and result_ip.returncode == 0:
        print(f"Static IP {ip_address}/{netmask} set for {interface}.")
        
        # Set gateway
        result_gateway = _run_command(["sudo", "ip", "route", "add", "default", "via", gateway, "dev", interface], check_success=False)
        if result_gateway and result_gateway.returncode == 0:
            print(f"Default gateway set to {gateway}.")
        else:
            print(f"Warning: Failed to set default gateway. Exit code: {result_gateway.returncode}", file=sys.stderr)
            if result_gateway.stderr:
                print(f"Details: {result_gateway.stderr.strip()}", file=sys.stderr)
            
        # Set DNS servers (by modifying /etc/resolv.conf, often handled by NetworkManager/systemd-resolved)
        # Directly editing resolv.conf might be overwritten by NetworkManager.
        # For persistent DNS, consider network manager config files or systemd-resolved.
        if dns_servers:
            print("Attempting to set DNS servers (may be overwritten by NetworkManager/systemd-resolved)...")
            try:
                # Backup existing resolv.conf
                _run_command(["sudo", "cp", "/etc/resolv.conf", "/etc/resolv.conf.bak"], check_success=False)
                with open("/tmp/resolv.conf.tmp", "w") as f: # Write to a temp file first
                    for dns in dns_servers:
                        f.write(f"nameserver {dns}\n")
                _run_command(["sudo", "mv", "/tmp/resolv.conf.tmp", "/etc/resolv.conf"])
                print(f"DNS servers set to: {', '.join(dns_servers)}")
            except Exception as e:
                print(f"Warning: Failed to set DNS servers: {e}", file=sys.stderr)
    elif result_ip:
        print(f"Failed to set static IP. Exit code: {result_ip.returncode}", file=sys.stderr)

def set_dhcp(interface):
    """Configures a network interface to use DHCP."""
    print(f"Attempting to set DHCP on {interface}...")
    
    # Remove existing IP configurations
    _run_command(["sudo", "ip", "addr", "flush", "dev", interface], check_success=False)
    
    # Bring down and up interface (can sometimes re-trigger DHCP)
    _run_command(["sudo", "ip", "link", "set", interface, "down"], check_success=False)
    _run_command(["sudo", "ip", "link", "set", interface, "up"], check_success=False)
    
    # Initiate DHCP client (e.g., using dhclient)
    # Note: 'dhclient' might not be installed by default on all systems.
    # For persistent DHCP, network manager configuration files are the way to go.
    result = _run_command(["sudo", "dhclient", interface], check_success=False) # dhclient might exit with non-zero if already running/no lease
    
    if result and result.returncode == 0:
        print(f"DHCP configured successfully for {interface}.")
    elif result:
        print(f"DHCP command might have failed or encountered issues. Check network status.", file=sys.stderr)
        if result.stderr:
            print(f"Details: {result.stderr.strip()}", file=sys.stderr)
    else: # If dhclient not found
        print("Consider checking your network manager configuration for DHCP.", file=sys.stderr)

def release_renew_dhcp(interface, action="release"):
    """Releases or renews DHCP lease for an interface."""
    print(f"Attempting to {action} DHCP lease on {interface}...")
    result = _run_command(["sudo", "dhclient", f"-r", interface] if action == "release" else ["sudo", "dhclient", interface], check_success=False)
    
    if result and result.returncode == 0:
        print(f"DHCP lease {action}d for {interface}.")
    elif result:
        print(f"Failed to {action} DHCP lease. Exit code: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Details: {result.stderr.strip()}", file=sys.stderr)

def display_network_info():
    """Displays current network configuration (IP, gateway, DNS)."""
    print("--- Current Network Information ---")
    
    # IP Addresses and Interfaces
    print("\n--- IP Addresses and Interfaces ---")
    result_ip = _run_command(["ip", "a"])
    if result_ip and result_ip.returncode == 0:
        print(result_ip.stdout)
    else:
        print("Failed to get IP address information.")

    # Routing Table
    print("\n--- Routing Table ---")
    result_route = _run_command(["ip", "r"])
    if result_route and result_route.returncode == 0:
        print(result_route.stdout)
    else:
        print("Failed to get routing table information.")

    # DNS Servers
    print("\n--- DNS Servers (/etc/resolv.conf) ---")
    try:
        with open("/etc/resolv.conf", "r") as f:
            resolv_content = f.read()
            print(resolv_content)
    except FileNotFoundError:
        print("/etc/resolv.conf not found.")
    except Exception as e:
        print(f"Error reading /etc/resolv.conf: {e}")

def manage_linux_networking():
    """Main menu for Linux networking management."""
    while True:
        print("\n--- Gestión de Red Linux ---")
        print("1. Listar Interfaces de Red")
        print("2. Configurar IP Estática")
        print("3. Configurar DHCP")
        print("4. Liberar/Renovar Lease DHCP")
        print("5. Mostrar Información de Red Actual")
        print("6. Volver al menú principal")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            get_network_interfaces()
        elif choice == '2':
            interface = input("Ingrese el nombre de la interfaz (ej. eth0, enpXsY): ")
            ip_address = input("Ingrese la dirección IP (ej. 192.168.1.100): ")
            netmask = input("Ingrese la máscara de red (ej. 24 para /24, o 255.255.255.0): ")
            gateway = input("Ingrese la dirección del gateway (ej. 192.168.1.1): ")
            dns_input = input("Ingrese los servidores DNS (separados por coma, ej. 8.8.8.8,8.8.4.4): ")
            dns_servers = [d.strip() for d in dns_input.split(',') if d.strip()] if dns_input else None
            set_static_ip(interface, ip_address, netmask, gateway, dns_servers)
        elif choice == '3':
            interface = input("Ingrese el nombre de la interfaz (ej. eth0, enpXsY): ")
            set_dhcp(interface)
        elif choice == '4':
            interface = input("Ingrese el nombre de la interfaz (ej. eth0, enpXsY): ")
            action = input("¿Liberar (release) o Renovar (renew) el lease DHCP?: ").lower()
            if action not in ["release", "renew"]:
                print("Acción no válida. Debe ser 'release' o 'renew'.")
                continue
            release_renew_dhcp(interface, action)
        elif choice == '5':
            display_network_info()
        elif choice == '6':
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    if sys.platform.startswith("linux"):
        manage_linux_networking()
    else:
        print("Este script está diseñado para sistemas operativos Linux.")