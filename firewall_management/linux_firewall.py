# firewall_management/linux_firewall.py

from utils import common

def display_firewall_menu():
    """Muestra el submenú de gestión de firewall en Linux."""
    common.clear_screen()
    print("--- Gestión de Firewall (Linux - ufw/firewalld) ---")
    print("1. Ver Estado del Firewall")
    print("2. Habilitar Firewall")
    print("3. Deshabilitar Firewall")
    print("4. Añadir Regla (Permitir Puerto/Servicio)")
    print("5. Eliminar Regla")
    print("6. Restablecer Firewall (ufw)")
    print("7. Recargar Firewall (firewalld)")
    print("0. Volver al Menú Principal")

def get_firewall_type():
    """Detecta si ufw o firewalld está activo."""
    ufw_check = common.run_command(["systemctl", "is-active", "ufw"], capture_output=True, check=False)
    if ufw_check and ufw_check.returncode == 0 and "active" in ufw_check.stdout:
        return "ufw"
    
    firewalld_check = common.run_command(["systemctl", "is-active", "firewalld"], capture_output=True, check=False)
    if firewalld_check and firewalld_check.returncode == 0 and "active" in firewalld_check.stdout:
        return "firewalld"
        
    return "none" # Ninguno de los dos está activo o no se pudo determinar

def view_firewall_status():
    firewall_type = get_firewall_type()
    if firewall_type == "ufw":
        print("\n--- Estado del Firewall (ufw) ---")
        command = ["sudo", "ufw", "status", "verbose"]
    elif firewall_type == "firewalld":
        print("\n--- Estado del Firewall (firewalld) ---")
        command = ["sudo", "firewall-cmd", "--state"]
        result = common.run_command(command, capture_output=True)
        if result and result.returncode == 0:
            print(result.stdout)
            print("\n--- Reglas de Firewall (firewalld - Zona pública) ---")
            command = ["sudo", "firewall-cmd", "--list-all"]
        else:
            print("Firewalld no está corriendo o no se pudo obtener el estado.")
            return
    else:
        print("No se detectó UFW ni Firewalld activo. No se puede verificar el estado.")
        return

    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error al obtener el estado del firewall ({firewall_type}).")
    common.press_enter_to_continue()

def enable_firewall():
    firewall_type = get_firewall_type()
    if firewall_type == "ufw":
        command = ["sudo", "ufw", "enable"]
    elif firewall_type == "firewalld":
        command = ["sudo", "systemctl", "start", "firewalld"]
        result = common.run_command(["sudo", "systemctl", "enable", "firewalld"]) # Para que sea persistente
        if result and result.returncode == 0:
            print("Firewalld habilitado al inicio del sistema.")
    else:
        print("No se detectó UFW ni Firewalld. No se puede habilitar.")
        return

    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Firewall ({firewall_type}) habilitado.")
    else:
        print(f"Error al habilitar el firewall ({firewall_type}).")
    common.press_enter_to_continue()


def disable_firewall():
    firewall_type = get_firewall_type()
    if firewall_type == "ufw":
        command = ["sudo", "ufw", "disable"]
    elif firewall_type == "firewalld":
        command = ["sudo", "systemctl", "stop", "firewalld"]
        result = common.run_command(["sudo", "systemctl", "disable", "firewalld"]) # Para que no inicie automáticamente
        if result and result.returncode == 0:
            print("Firewalld deshabilitado al inicio del sistema.")
    else:
        print("No se detectó UFW ni Firewalld. No se puede deshabilitar.")
        return

    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Firewall ({firewall_type}) deshabilitado.")
    else:
        print(f"Error al deshabilitar el firewall ({firewall_type}).")
    common.press_enter_to_continue()

def add_firewall_rule():
    firewall_type = get_firewall_type()
    if firewall_type == "ufw":
        port = input("Introduce el número de puerto o nombre de servicio (ej. 80, ssh): ")
        protocol = input("Introduce el protocolo (tcp/udp, o dejar vacío para ambos): ").strip()
        direction = input("Introduce la dirección (in/out, o dejar vacío para in): ").strip()

        if protocol and direction:
            command = ["sudo", "ufw", "allow", "from", "any", "to", "any", "port", port, "proto", protocol, "in", direction]
        elif protocol:
            command = ["sudo", "ufw", "allow", port, "/tcp" if protocol == "tcp" else "/udp" if protocol == "udp" else "", "comment", f"Allow {port}/{protocol}"]
            if not protocol:
                command = ["sudo", "ufw", "allow", port]
        else:
            command = ["sudo", "ufw", "allow", port]

        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Regla de ufw para puerto/servicio '{port}' añadida.")
        else:
            print(f"Error al añadir regla de ufw para '{port}'.")
    elif firewall_type == "firewalld":
        port = input("Introduce el número de puerto (ej. 80/tcp): ")
        service = input("Introduce el nombre de servicio (ej. http, ssh) o dejar vacío si es un puerto: ").strip()
        zone = input("Introduce la zona (ej. public, home, o dejar vacío para public): ").strip() or "public"

        if service:
            command = ["sudo", "firewall-cmd", "--zone", zone, "--add-service", service, "--permanent"]
            description = f"servicio '{service}'"
        else:
            command = ["sudo", "firewall-cmd", "--zone", zone, "--add-port", port, "--permanent"]
            description = f"puerto '{port}'"

        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Regla de firewalld para {description} añadida a la zona '{zone}'. ¡Recuerda recargar el firewall!")
        else:
            print(f"Error al añadir regla de firewalld para {description}.")
    else:
        print("No se detectó UFW ni Firewalld. No se puede añadir reglas.")
    common.press_enter_to_continue()

def delete_firewall_rule():
    firewall_type = get_firewall_type()
    if firewall_type == "ufw":
        # Para eliminar una regla en ufw, lo más fácil es por número
        print("\nPara eliminar una regla de ufw, primero ve el estado detallado (opción 1) y anota el número de la regla.")
        rule_number = input("Introduce el número de la regla a eliminar: ")
        command = ["sudo", "ufw", "delete", rule_number]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Regla de ufw número '{rule_number}' eliminada.")
        else:
            print(f"Error al eliminar regla de ufw número '{rule_number}'.")
    elif firewall_type == "firewalld":
        port = input("Introduce el número de puerto a eliminar (ej. 80/tcp) o dejar vacío si es un servicio: ").strip()
        service = input("Introduce el nombre de servicio a eliminar (ej. http, ssh) o dejar vacío si es un puerto: ").strip()
        zone = input("Introduce la zona (ej. public, home, o dejar vacío para public): ").strip() or "public"

        if service:
            command = ["sudo", "firewall-cmd", "--zone", zone, "--remove-service", service, "--permanent"]
            description = f"servicio '{service}'"
        elif port:
            command = ["sudo", "firewall-cmd", "--zone", zone, "--remove-port", port, "--permanent"]
            description = f"puerto '{port}'"
        else:
            print("Debes especificar un puerto o un servicio a eliminar.")
            common.press_enter_to_continue()
            return

        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Regla de firewalld para {description} eliminada de la zona '{zone}'. ¡Recuerda recargar el firewall!")
        else:
            print(f"Error al eliminar regla de firewalld para {description}.")
    else:
        print("No se detectó UFW ni Firewalld. No se puede eliminar reglas.")
    common.press_enter_to_continue()

def reset_ufw():
    firewall_type = get_firewall_type()
    if firewall_type == "ufw":
        confirm = input("¡ADVERTENCIA! Esto restablecerá UFW a su configuración por defecto y eliminará todas las reglas. ¿Continuar? (s/n): ").lower()
        if confirm == 's':
            command = ["sudo", "ufw", "reset"]
            result = common.run_command(command)
            if result and result.returncode == 0:
                print("UFW restablecido a la configuración por defecto.")
            else:
                print("Error al restablecer UFW.")
        else:
            print("Operación cancelada.")
    else:
        print("Esta opción es solo para UFW. Firewalld no tiene una función de 'reset' directa similar.")
    common.press_enter_to_continue()

def reload_firewalld():
    firewall_type = get_firewall_type()
    if firewall_type == "firewalld":
        command = ["sudo", "firewall-cmd", "--reload"]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print("Firewalld recargado correctamente. Los cambios permanentes se han aplicado.")
        else:
            print("Error al recargar Firewalld.")
    else:
        print("Esta opción es solo para Firewalld. UFW aplica los cambios instantáneamente.")
    common.press_enter_to_continue()


def firewall_management_menu():
    """Menú principal para la gestión de firewalls en Linux."""
    while True:
        common.clear_screen()
        display_firewall_menu()
        choice = input("Su elección: ")

        if choice == '1':
            view_firewall_status()
        elif choice == '2':
            enable_firewall()
        elif choice == '3':
            disable_firewall()
        elif choice == '4':
            add_firewall_rule()
        elif choice == '5':
            delete_firewall_rule()
        elif choice == '6':
            reset_ufw()
        elif choice == '7':
            reload_firewalld()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()