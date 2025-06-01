import subprocess
import sys
import re # For regular expressions
import os # For clearing screen

from utils import common

def _run_command(command, check_success=True, capture_output=True, shell=False):
    """
    Ejecuta un comando del sistema y maneja su salida y errores.
    
    Args:
        command (list o str): El comando a ejecutar. Si es una lista, se recomienda
                              shell=False para evitar inyección de comandos.
                              Si es una cadena, se recomienda shell=True.
        check_success (bool): Si es True, lanza una excepción CalledProcessError
                              si el comando devuelve un código de salida distinto de cero.
        capture_output (bool): Si es True, captura stdout y stderr.
        shell (bool): Si es True, el comando se ejecuta a través del shell.
                      Esto es menos seguro si el comando contiene entradas de usuario.
                      Se recomienda False y pasar el comando como una lista.

    Returns:
        subprocess.CompletedProcess: Objeto que contiene el resultado de la ejecución.
                                     (stdout, stderr, returncode).
    Raises:
        subprocess.CalledProcessError: Si check_success es True y el comando falla.
        FileNotFoundError: Si el comando no se encuentra.
    """
    try:
        result = subprocess.run(
            command,
            check=check_success,
            capture_output=capture_output,
            text=True,  # Decodifica stdout/stderr como texto usando la codificación por defecto
            shell=shell
        )
        if capture_output:
            pass # Output already captured, no need to print here
        return result
    except FileNotFoundError:
        cmd_name = command[0] if isinstance(command, list) else command.split()[0]
        print(f"Error: Comando '{cmd_name}' no encontrado. Asegúrate de que esté instalado y en tu PATH.", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar comando: {e}", file=sys.stderr)
        print(f"STDOUT: {e.stdout.strip()}", file=sys.stderr)
        print(f"STDERR: {e.stderr.strip()}", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None
    except Exception as e:
        print(f"Error inesperado al ejecutar el comando: {e}", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None

def _clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def _press_enter_to_continue():
    """Pauses execution until the user presses Enter."""
    input("\nPresione Enter para continuar...")

## Gestión de Redes (Linux)

def display_network_menu_linux():
    """Muestra el submenú de gestión de red en Linux."""
    _clear_screen()
    print("--- Gestión de Redes (Linux) ---")
    print("1. Ver Configuración de Interfaces")
    print("2. Configurar IP Estática")
    print("3. Configurar IP Dinámica (DHCP)")
    print("4. Añadir Ruta Estática")
    print("5. Eliminar Ruta Estática")
    print("6. Ver Tabla de Rutas")
    print("7. Configurar Servidores DNS")
    print("8. Liberar/Renovar Lease DHCP") 
    print("0. Volver al Menú Principal")

def get_network_interfaces_names():
    """Lists available network interface names (excluding loopback)."""
    result = _run_command(["ip", "a"], check_success=False)
    if result and result.returncode == 0:
        interfaces = []
        matches = re.findall(r"^\d+: ([a-zA-Z0-9]+):", result.stdout, re.MULTILINE)
        if matches:
            for iface in matches:
                if iface != "lo":
                    interfaces.append(iface)
            return interfaces
    return []

def view_interface_config_linux():
    """Displays current network configuration (IP addresses and interfaces)."""
    print("\n--- Configuración de Interfaces de Red (Linux) ---")
    result_ip = _run_command(["ip", "a"], capture_output=True)
    if result_ip and result_ip.returncode == 0:
        print(result_ip.stdout)
    else:
        print("No se pudo obtener la configuración de interfaces.")
    _press_enter_to_continue()

def set_static_ip_linux():
    """Sets a static IP address for a network interface."""
    interfaces = get_network_interfaces_names()
    if not interfaces:
        print("No se encontraron interfaces de red disponibles.")
        _press_enter_to_continue()
        return

    print("Interfaces disponibles: " + ", ".join(interfaces))
    interface = input("Ingrese el nombre de la interfaz (ej. eth0, enpXsY): ")

    if interface not in interfaces:
        print(f"Error: La interfaz '{interface}' no existe o no está activa.")
        _press_enter_to_continue()
        return

    ip_address = input("Ingrese la dirección IP (ej. 192.168.1.100): ")
    netmask = input("Ingrese la máscara de red (ej. 24 para /24, o 255.255.255.0): ") 
    gateway = input("Ingrese la dirección del gateway (ej. 192.168.1.1): ")

    print(f"Intentando configurar IP estática {ip_address}/{netmask} en {interface}...")
    
    # NOTE: These 'ip' commands are for IMMEDIATE, NON-PERSISTENT configuration.
    # For persistent setup, you typically need to edit network manager configuration files
    # (e.g., /etc/netplan for Ubuntu, /etc/sysconfig/network-scripts for CentOS/RHEL).

    _run_command(["sudo", "ip", "addr", "flush", "dev", interface], check_success=False)

    result_ip = _run_command(["sudo", "ip", "addr", "add", f"{ip_address}/{netmask}", "dev", interface])
    
    _run_command(["sudo", "ip", "link", "set", interface, "up"], check_success=False)

    if result_ip and result_ip.returncode == 0:
        print(f"IP estática {ip_address}/{netmask} configurada para {interface}.")
        
        print("Configurando puerta de enlace...")
        _run_command(["sudo", "ip", "route", "del", "default", "dev", interface], check_success=False)
        result_gateway = _run_command(["sudo", "ip", "route", "add", "default", "via", gateway, "dev", interface], check_success=False)
        
        if result_gateway and result_gateway.returncode == 0:
            print(f"Puerta de enlace predeterminada establecida a {gateway}.")
        else:
            print(f"Advertencia: Falló al establecer la puerta de enlace predeterminada. Código de salida: {result_gateway.returncode}", file=sys.stderr)
            if result_gateway and result_gateway.stderr:
                print(f"Detalles: {result_gateway.stderr.strip()}", file=sys.stderr)
    else:
        print(f"Falló al configurar la IP estática. Código de salida: {result_ip.returncode}", file=sys.stderr)
    _press_enter_to_continue()

def configure_dhcp_linux():
    """Configures a network interface to use DHCP."""
    interfaces = get_network_interfaces_names()
    if not interfaces:
        print("No se encontraron interfaces de red disponibles.")
        _press_enter_to_continue()
        return

    print("Interfaces disponibles: " + ", ".join(interfaces))
    interface = input("Ingrese el nombre de la interfaz (ej. eth0, enpXsY): ")

    if interface not in interfaces:
        print(f"Error: La interfaz '{interface}' no existe o no está activa.")
        _press_enter_to_continue()
        return

    print(f"Intentando configurar DHCP en {interface}...")
    
    # NOTE: These 'ip' and 'dhclient' commands are for IMMEDIATE, NON-PERSISTENT configuration.

    _run_command(["sudo", "ip", "addr", "flush", "dev", interface], check_success=False)
    
    _run_command(["sudo", "ip", "link", "set", interface, "down"], check_success=False)
    _run_command(["sudo", "ip", "link", "set", interface, "up"], check_success=False)
    
    result = _run_command(["sudo", "dhclient", interface], check_success=False) 
    
    if result and result.returncode == 0:
        print(f"DHCP configurado exitosamente para {interface}.")
    elif result:
        print(f"El comando DHCP pudo haber fallado o encontrado problemas. Verifique el estado de la red.", file=sys.stderr)
        if result.stderr:
            print(f"Detalles: {result.stderr.strip()}", file=sys.stderr)
    else: 
        print("Considere verificar la configuración de su gestor de red para DHCP.", file=sys.stderr)
    _press_enter_to_continue()

def add_static_route_linux():
    """Adds a static route to the routing table."""
    destination = input("Introduce la red de destino (ej. 192.168.2.0/24): ")
    gateway = input("Introduce la puerta de enlace (ej. 192.168.1.1): ")
    
    # For persistent static routes, you typically need to edit network manager configuration files
    command = ["sudo", "ip", "route", "add", destination, "via", gateway]
    result = _run_command(command)
    
    if result and result.returncode == 0:
        print(f"Ruta estática a {destination} vía {gateway} añadida.")
    else:
        print(f"Error al añadir la ruta estática.")
    _press_enter_to_continue()

def delete_static_route_linux():
    """Deletes a static route from the routing table."""
    destination = input("Introduce la red de destino de la ruta a eliminar (ej. 192.168.2.0/24): ")
    
    command = ["sudo", "ip", "route", "del", destination]
    result = _run_command(command)
    
    if result and result.returncode == 0:
        print(f"Ruta estática a {destination} eliminada.")
    else:
        print(f"Error al eliminar la ruta estática. Asegúrate de que la ruta exista.")
    _press_enter_to_continue()

def view_routing_table_linux():
    """Displays the current kernel routing table."""
    print("\n--- Tabla de Rutas (Linux) ---")
    result_route = _run_command(["ip", "r"], capture_output=True)
    if result_route and result_route.returncode == 0:
        print(result_route.stdout)
    else:
        print("No se pudo obtener la tabla de rutas.")
    _press_enter_to_continue()

def configure_dns_servers_linux():
    """Sets DNS servers by modifying /etc/resolv.conf."""
    print("\n--- Configurar Servidores DNS (Linux) ---")
    print("Advertencia: La modificación directa de /etc/resolv.conf puede ser sobrescrita por NetworkManager o systemd-resolved.")
    print("Para una configuración persistente, considere usar la herramienta de su gestor de red (ej. netplan, nmcli).")

    dns_input = input("Ingrese los servidores DNS (separados por coma, ej. 8.8.8.8,8.8.4.4): ")
    dns_servers = [d.strip() for d in dns_input.split(',') if d.strip()]

    if not dns_servers:
        print("No se ingresaron servidores DNS.")
        _press_enter_to_continue()
        return

    try:
        print("Creando copia de seguridad de /etc/resolv.conf a /etc/resolv.conf.bak...")
        _run_command(["sudo", "cp", "/etc/resolv.conf", "/etc/resolv.conf.bak"], check_success=False)
        
        temp_resolv_path = "/tmp/resolv.conf.tmp"
        with open(temp_resolv_path, "w") as f:
            for dns in dns_servers:
                f.write(f"nameserver {dns}\n")
        
        print(f"Aplicando nuevos servidores DNS: {', '.join(dns_servers)}...")
        result_mv = _run_command(["sudo", "mv", temp_resolv_path, "/etc/resolv.conf"])
        
        if result_mv and result_mv.returncode == 0:
            print("Servidores DNS configurados con éxito.")
        else:
            print("Error al aplicar los servidores DNS.")

    except Exception as e:
        print(f"Error inesperado al configurar DNS: {e}", file=sys.stderr)
    _press_enter_to_continue()

def release_renew_dhcp_linux(action="release"):
    """Releases or renews DHCP lease for an interface."""
    interfaces = get_network_interfaces_names()
    if not interfaces:
        print("No se encontraron interfaces de red disponibles.")
        _press_enter_to_continue()
        return

    print("Interfaces disponibles: " + ", ".join(interfaces))
    interface = input("Ingrese el nombre de la interfaz (ej. eth0, enpXsY): ")

    if interface not in interfaces:
        print(f"Error: La interfaz '{interface}' no existe o no está activa.")
        _press_enter_to_continue()
        return

    print(f"Intentando {action} lease DHCP en {interface}...")
    command = ["sudo", "dhclient", f"-r", interface] if action == "release" else ["sudo", "dhclient", interface]
    result = _run_command(command, check_success=False)
    
    if result and result.returncode == 0:
        print(f"Lease DHCP {action}d para {interface}.")
    elif result:
        print(f"Falló al {action} lease DHCP. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles: {result.stderr.strip()}", file=sys.stderr)
    _press_enter_to_continue()

def network_management_menu_linux():
    """Menú principal para la gestión de redes en Linux."""
    while True:
        common.clear_screen()
        display_network_menu_linux()
        choice = input("Su elección: ")

        if choice == '1':
            view_interface_config_linux()
        elif choice == '2':
            set_static_ip_linux()
        elif choice == '3':
            configure_dhcp_linux()
        elif choice == '4':
            add_static_route_linux()
        elif choice == '5':
            delete_static_route_linux()
        elif choice == '6':
            view_routing_table_linux()
        elif choice == '7':
            configure_dns_servers_linux()
        elif choice == '8':
            action = input("¿Liberar (release) o Renovar (renew) el lease DHCP?: ").lower()
            if action not in ["release", "renew"]:
                print("Acción no válida. Debe ser 'release' o 'renew'.")
                common.press_enter_to_continue()
                continue
            release_renew_dhcp_linux(action)
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()