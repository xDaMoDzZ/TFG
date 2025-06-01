# network_management/windows_networking.py

from utils import common

def display_network_menu():
    """Muestra el submenú de gestión de red en Windows."""
    common.clear_screen()
    print("--- Gestión de Redes (Windows) ---")
    print("1. Ver Configuración de Interfaces")
    print("2. Configurar IP Estática")
    print("3. Configurar IP Dinámica (DHCP)")
    print("4. Añadir Ruta Estática")
    print("5. Eliminar Ruta Estática")
    print("6. Ver Tabla de Rutas")
    print("7. Configurar Servidores DNS")
    print("0. Volver al Menú Principal")

def view_interface_config():
    print("\n--- Configuración de Interfaces de Red (Windows) ---")
    command = ["ipconfig", "/all"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la configuración de interfaces.")
    common.press_enter_to_continue()

def configure_static_ip():
    interface_name = input("Introduce el nombre de la interfaz (ej. 'Ethernet', 'Wi-Fi'): ")
    ip_address = input("Introduce la dirección IP (ej. 192.168.1.100): ")
    subnet_mask = input("Introduce la máscara de subred (ej. 255.255.255.0): ")
    gateway = input("Introduce la puerta de enlace (ej. 192.168.1.1): ")

    # Configurar IP estática
    command = ["netsh", "interface", "ip", "set", "address",
               f"name=\"{interface_name}\"", "static", ip_address, subnet_mask, gateway]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"IP estática {ip_address} configurada en '{interface_name}'.")
    else:
        print(f"Error al configurar IP estática en '{interface_name}'.")

def configure_dhcp():
    interface_name = input("Introduce el nombre de la interfaz (ej. 'Ethernet', 'Wi-Fi'): ")
    command = ["netsh", "interface", "ip", "set", "address",
               f"name=\"{interface_name}\"", "dhcp"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Interfaz '{interface_name}' configurada para DHCP.")
    else:
        print(f"Error al configurar DHCP en '{interface_name}'.")

def add_static_route():
    destination = input("Introduce la red de destino (ej. 192.168.2.0): ")
    mask = input("Introduce la máscara de subred para el destino (ej. 255.255.255.0): ")
    gateway = input("Introduce la puerta de enlace (ej. 192.168.1.1): ")
    command = ["route", "ADD", destination, "MASK", mask, gateway]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Ruta estática a {destination} vía {gateway} añadida.")
    else:
        print(f"Error al añadir la ruta estática.")

def delete_static_route():
    destination = input("Introduce la red de destino de la ruta a eliminar (ej. 192.168.2.0): ")
    command = ["route", "DELETE", destination]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Ruta estática a {destination} eliminada.")
    else:
        print(f"Error al eliminar la ruta estática. Asegúrate de que la ruta exista.")

def view_routing_table():
    print("\n--- Tabla de Rutas (Windows) ---")
    command = ["route", "PRINT"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la tabla de rutas.")
    common.press_enter_to_continue()

def configure_dns_servers():
    interface_name = input("Introduce el nombre de la interfaz (ej. 'Ethernet', 'Wi-Fi'): ")
    dns_servers_input = input("Introduce los servidores DNS separados por comas (ej. 8.8.8.8,8.8.4.4): ")
    dns_servers = [ip.strip() for ip in dns_servers_input.split(',')]

    # Configurar el primer DNS
    command_primary_dns = ["netsh", "interface", "ip", "set", "dns",
                           f"name=\"{interface_name}\"", "static", dns_servers[0], "primary"]
    result_primary = common.run_command(command_primary_dns)

    if result_primary and result_primary.returncode == 0:
        print(f"DNS primario '{dns_servers[0]}' configurado en '{interface_name}'.")
        # Añadir DNS secundarios si existen
        for i, dns in enumerate(dns_servers[1:], start=2):
            command_secondary_dns = ["netsh", "interface", "ip", "add", "dns",
                                     f"name=\"{interface_name}\"", dns, f"index={i}"]
            result_secondary = common.run_command(command_secondary_dns)
            if result_secondary and result_secondary.returncode == 0:
                print(f"DNS secundario '{dns}' configurado en '{interface_name}'.")
            else:
                print(f"Error al configurar DNS secundario '{dns}'.")
    else:
        print(f"Error al configurar DNS primario en '{interface_name}'.")

    common.press_enter_to_continue()

def network_management_menu():
    """Menú principal para la gestión de redes en Windows."""
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
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()