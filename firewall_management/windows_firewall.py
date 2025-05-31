# firewall_management/windows_firewall.py

from utils import common

def display_firewall_menu():
    """Muestra el submenú de gestión de firewall en Windows."""
    common.clear_screen()
    print("--- Gestión de Firewall (Windows Defender Firewall) ---")
    print("1. Ver Estado del Firewall")
    print("2. Habilitar Firewall (Perfiles)")
    print("3. Deshabilitar Firewall (Perfiles)")
    print("4. Añadir Regla de Entrada (Permitir Puerto)")
    print("5. Eliminar Regla de Entrada")
    print("6. Añadir Regla de Salida (Permitir Puerto)")
    print("7. Eliminar Regla de Salida")
    print("8. Restablecer Firewall a valores predeterminados")
    print("0. Volver al Menú Principal")

def view_firewall_status():
    print("\n--- Estado del Firewall de Windows Defender ---")
    command = ["netsh", "advfirewall", "show", "allprofiles"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("Error al obtener el estado del firewall.")
    common.press_enter_to_continue()

def enable_firewall_profile():
    profile = input("Introduce el perfil a habilitar (Domain, Private, Public, o All): ").capitalize()
    if profile not in ["Domain", "Private", "Public", "All"]:
        print("Perfil no válido. Opciones: Domain, Private, Public, All.")
        return

    command = ["netsh", "advfirewall", "set", profile, "state", "on"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Firewall habilitado para el perfil '{profile}'.")
    else:
        print(f"Error al habilitar el firewall para el perfil '{profile}'.")
    common.press_enter_to_continue()

def disable_firewall_profile():
    profile = input("Introduce el perfil a deshabilitar (Domain, Private, Public, o All): ").capitalize()
    if profile not in ["Domain", "Private", "Public", "All"]:
        print("Perfil no válido. Opciones: Domain, Private, Public, All.")
        return

    command = ["netsh", "advfirewall", "set", profile, "state", "off"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Firewall deshabilitado para el perfil '{profile}'.")
    else:
        print(f"Error al deshabilitar el firewall para el perfil '{profile}'.")
    common.press_enter_to_continue()

def add_inbound_port_rule():
    name = input("Introduce el nombre de la regla (ej. 'Permitir HTTP'): ")
    port = input("Introduce el número de puerto (ej. 80): ")
    protocol = input("Introduce el protocolo (TCP/UDP, o dejar vacío para ambos): ").upper().strip()
    action = "allow" # Por defecto, la regla será de permiso
    direction = "in"

    if not protocol:
        protocol = "ANY"

    command = ["netsh", "advfirewall", "firewall", "add", "rule",
               f"name=\"{name}\"", "dir=in", f"action={action}", f"protocol={protocol}", f"localport={port}"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Regla de entrada para el puerto '{port}' ({protocol}) añadida con éxito.")
    else:
        print(f"Error al añadir la regla de entrada para el puerto '{port}'.")
    common.press_enter_to_continue()

def delete_inbound_rule():
    name = input("Introduce el nombre de la regla de entrada a eliminar: ")
    command = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name=\"{name}\"", "dir=in"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Regla de entrada '{name}' eliminada con éxito.")
    else:
        print(f"Error al eliminar la regla de entrada '{name}'.")
    common.press_enter_to_continue()

def add_outbound_port_rule():
    name = input("Introduce el nombre de la regla (ej. 'Permitir FTP Salida'): ")
    port = input("Introduce el número de puerto (ej. 21): ")
    protocol = input("Introduce el protocolo (TCP/UDP, o dejar vacío para ambos): ").upper().strip()
    action = "allow" # Por defecto, la regla será de permiso
    direction = "out"

    if not protocol:
        protocol = "ANY"

    command = ["netsh", "advfirewall", "firewall", "add", "rule",
               f"name=\"{name}\"", "dir=out", f"action={action}", f"protocol={protocol}", f"localport={port}"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Regla de salida para el puerto '{port}' ({protocol}) añadida con éxito.")
    else:
        print(f"Error al añadir la regla de salida para el puerto '{port}'.")
    common.press_enter_to_continue()

def delete_outbound_rule():
    name = input("Introduce el nombre de la regla de salida a eliminar: ")
    command = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name=\"{name}\"", "dir=out"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Regla de salida '{name}' eliminada con éxito.")
    else:
        print(f"Error al eliminar la regla de salida '{name}'.")
    common.press_enter_to_continue()

def reset_firewall():
    confirm = input("¡ADVERTENCIA! Esto restablecerá todas las configuraciones del Firewall de Windows Defender a los valores predeterminados. ¿Continuar? (s/n): ").lower()
    if confirm == 's':
        command = ["netsh", "advfirewall", "reset"]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print("Firewall de Windows Defender restablecido correctamente.")
        else:
            print("Error al restablecer el firewall.")
    else:
        print("Operación cancelada.")
    common.press_enter_to_continue()

def firewall_management_menu():
    """Menú principal para la gestión de firewalls en Windows."""
    while True:
        common.clear_screen()
        display_firewall_menu()
        choice = input("Su elección: ")

        if choice == '1':
            view_firewall_status()
        elif choice == '2':
            enable_firewall_profile()
        elif choice == '3':
            disable_firewall_profile()
        elif choice == '4':
            add_inbound_port_rule()
        elif choice == '5':
            delete_inbound_rule()
        elif choice == '6':
            add_outbound_port_rule()
        elif choice == '7':
            delete_outbound_rule()
        elif choice == '8':
            reset_firewall()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()