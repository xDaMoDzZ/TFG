# network_management/linux_networking.py

from utils import common

def display_network_menu():
    """Muestra el submenú de gestión de red en Linux."""
    common.clear_screen()
    print("--- Gestión de Redes (Linux) ---")
    print("1. Ver Configuración de Interfaces")
    print("2. Configurar IP Estática")
    print("3. Configurar IP Dinámica (DHCP)")
    print("4. Añadir Ruta Estática")
    print("5. Eliminar Ruta Estática")
    print("6. Ver Tabla de Rutas")
    print("7. Configurar Servidores DNS")
    print("8. Ver Configuración DNS")
    print("0. Volver al Menú Principal")

def view_interface_config():
    print("\n--- Configuración de Interfaces de Red (Linux) ---")
    command = ["ip", "a"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la configuración de interfaces.")
    common.press_enter_to_continue()

def configure_static_ip():
    interface = input("Introduce el nombre de la interfaz (ej. eth0, enp0s3): ")
    ip_address = input("Introduce la dirección IP (ej. 192.168.1.100/24): ")
    gateway = input("Introduce la puerta de enlace (ej. 192.168.1.1): ")

    # Eliminar cualquier configuración IP existente para la interfaz
    common.run_command(["sudo", "ip", "addr", "flush", "dev", interface], check=False)

    # Configurar IP estática
    command_ip = ["sudo", "ip", "addr", "add", ip_address, "dev", interface]
    result_ip = common.run_command(command_ip)

    # Levantar la interfaz
    command_up = ["sudo", "ip", "link", "set", interface, "up"]
    result_up = common.run_command(command_up)

    # Configurar puerta de enlace (si se proporciona y es diferente de la ruta por defecto existente)
    if gateway:
        # Eliminar ruta por defecto existente
        common.run_command(["sudo", "ip", "route", "del", "default"], check=False)
        command_gateway = ["sudo", "ip", "route", "add", "default", "via", gateway]
        result_gateway = common.run_command(command_gateway)
    else:
        result_gateway = True # No hay puerta de enlace para configurar

    if result_ip and result_up and (result_gateway is True or (result_gateway and result_gateway.returncode == 0)):
        print(f"IP estática {ip_address} configurada en {interface}.")
        if gateway:
            print(f"Puerta de enlace {gateway} configurada.")
        print("Recuerda que esta configuración puede ser temporal y se perderá al reiniciar. "
              "Para persistencia, edita /etc/network/interfaces o Netplan.")
    else:
        print(f"Error al configurar IP estática en {interface}.")

def configure_dhcp():
    interface = input("Introduce el nombre de la interfaz (ej. eth0, enp0s3): ")

    # Eliminar cualquier configuración IP existente para la interfaz
    common.run_command(["sudo", "ip", "addr", "flush", "dev", interface], check=False)

    # Baja la interfaz
    common.run_command(["sudo", "ip", "link", "set", interface, "down"], check=False)

    # Levanta la interfaz con DHCP
    command = ["sudo", "dhclient", interface] # O 'sudo systemctl restart NetworkManager' o 'sudo systemctl restart systemd-networkd'
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Interfaz '{interface}' configurada para DHCP.")
        print("Recuerda que esta configuración puede ser temporal. Para persistencia, edita /etc/network/interfaces o Netplan.")
    else:
        print(f"Error al configurar DHCP en '{interface}'. Asegúrate de tener 'dhclient' o 'dhcpcd' instalado.")


def add_static_route():
    destination = input("Introduce la red de destino (ej. 192.168.2.0/24): ")
    gateway = input("Introduce la puerta de enlace (ej. 192.168.1.1): ")
    command = ["sudo", "ip", "route", "add", destination, "via", gateway]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Ruta estática a {destination} via {gateway} añadida.")
    else:
        print(f"Error al añadir la ruta estática.")

def delete_static_route():
    destination = input("Introduce la red de destino a eliminar (ej. 192.168.2.0/24): ")
    gateway = input("Introduce la puerta de enlace de la ruta a eliminar (ej. 192.168.1.1): ")
    command = ["sudo", "ip", "route", "del", destination, "via", gateway]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Ruta estática a {destination} via {gateway} eliminada.")
    else:
        print(f"Error al eliminar la ruta estática.")

def view_routing_table():
    print("\n--- Tabla de Rutas (Linux) ---")
    command = ["ip", "route"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la tabla de rutas.")
    common.press_enter_to_continue()

def configure_dns_servers():
    print("¡Advertencia! Esta operación sobrescribirá el archivo /etc/resolv.conf.")
    confirm = input("¿Deseas continuar? (s/n): ").lower()
    if confirm != 's':
        print("Operación cancelada.")
        return

    dns_servers_input = input("Introduce los servidores DNS separados por comas (ej. 8.8.8.8,8.8.4.4): ")
    dns_servers = [ip.strip() for ip in dns_servers_input.split(',')]

    content = ""
    for dns in dns_servers:
        content += f"nameserver {dns}\n"

    try:
        # Se requiere sudo para escribir en /etc/resolv.conf
        # Es mejor usar un comando de shell para esto para evitar problemas de permisos de Python
        command = ["sudo", "sh", "-c", f"echo '{content}' > /etc/resolv.conf"]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print("Servidores DNS configurados correctamente en /etc/resolv.conf.")
        else:
            print("Error al configurar los servidores DNS.")
    except Exception as e:
        print(f"Error al configurar DNS: {e}")
    common.press_enter_to_continue()

def view_dns_config():
    print("\n--- Configuración DNS (Linux - /etc/resolv.conf) ---")
    try:
        with open("/etc/resolv.conf", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("/etc/resolv.conf no encontrado.")
    except Exception as e:
        print(f"Error al leer /etc/resolv.conf: {e}")
    common.press_enter_to_continue()

def network_management_menu():
    """Menú principal para la gestión de redes en Linux."""
    while True:
        common.clear_screen()
        display_network_menu()
        choice = input("Su elección: ")

        if choice == '1':
            view_interface_config()
        elif choice == '2':
            configure_static_ip()
        elif choice == '3':
            configure_dhcp()
        elif choice == '4':
            add_static_route()
        elif choice == '5':
            delete_static_route()
        elif choice == '6':
            view_routing_table()
        elif choice == '7':
            configure_dns_servers()
        elif choice == '8':
            view_dns_config()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()