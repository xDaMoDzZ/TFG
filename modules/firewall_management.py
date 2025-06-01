from utils.display import clear_screen, print_menu, print_header, print_info, print_success, print_error, get_user_input
from utils.system_info import get_os_type, execute_command
from utils.logger import log_action
import os

def firewall_menu():
    while True:
        clear_screen()
        print_header("Gestión de Firewall")
        options = {
            "1": "Ver Estado del Firewall",
            "2": "Habilitar Firewall (Requiere Privilegios)",
            "3": "Deshabilitar Firewall (Requiere Privilegios)",
            "4": "Listar Reglas del Firewall",
            "5": "Añadir Regla (Permitir Puerto) (Requiere Privilegios)",
            "6": "Eliminar Regla (Permitir Puerto) (Requiere Privilegios)",
            "9": "Generar Log de Firewall",
            "0": "Volver al Menú Principal"
        }
        print_menu(options)

        choice = get_user_input("Seleccione una opción")

        if choice == '1':
            view_firewall_status()
        elif choice == '2':
            enable_firewall()
        elif choice == '3':
            disable_firewall()
        elif choice == '4':
            list_firewall_rules()
        elif choice == '5':
            add_allow_port_rule()
        elif choice == '6':
            delete_allow_port_rule()
        elif choice == '9':
            generate_firewall_log()
        elif choice == '0':
            break
        else:
            print_error("Opción inválida. Por favor, intente de nuevo.")
        get_user_input("Presione Enter para continuar...")

def view_firewall_status():
    print_header("Ver Estado del Firewall")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall show allprofiles state"
    else: # linux (ufw es común en Debian/Ubuntu, iptables en otros)
        command = "ufw status"
        output, status = execute_command(command, sudo=True)
        if status != 0:
            print_info("UFW no encontrado o no activo. Intentando con iptables...")
            command = "sudo iptables -L -n -v"
            output, status = execute_command(command, sudo=True)

    if status == 0:
        print_info("Estado del Firewall:")
        print(output)
        log_action("Firewall", "View Status", "Estado del firewall listado exitosamente.")
    else:
        print_error(f"Error al ver estado del firewall: {output}")
        log_action("Firewall", "View Status", f"Error al ver estado del firewall: {output}")

def enable_firewall():
    print_header("Habilitar Firewall")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall set allprofiles state on"
    else: # linux
        command = "ufw enable"
        print_info("Si UFW no está instalado o en uso, esta operación puede fallar.")
        print_info("Considere 'sudo systemctl enable firewalld' y 'sudo systemctl start firewalld' para RHEL/CentOS, o 'sudo iptables -P INPUT ACCEPT' etc. para reglas directas.")
    
    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input("¿Está seguro que desea habilitar el firewall? Esto podría afectar la conectividad. (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success("Firewall habilitado exitosamente.")
            log_action("Firewall", "Enable Firewall", "Firewall habilitado.")
        else:
            print_error(f"Error al habilitar firewall: {output}")
            log_action("Firewall", "Enable Firewall", f"Error al habilitar firewall: {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Firewall", "Enable Firewall", "Habilitación de firewall cancelada.")

def disable_firewall():
    print_header("Deshabilitar Firewall")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall set allprofiles state off"
    else: # linux
        command = "ufw disable"
        print_info("Si UFW no está instalado o en uso, esta operación puede fallar.")
        print_info("Considere 'sudo systemctl stop firewalld' y 'sudo systemctl disable firewalld' para RHEL/CentOS, o 'sudo iptables -F' y 'sudo iptables -X' para limpiar reglas.")
    
    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input("¿Está seguro que desea deshabilitar el firewall? Esto podría dejar el sistema vulnerable. (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success("Firewall deshabilitado exitosamente.")
            log_action("Firewall", "Disable Firewall", "Firewall deshabilitado.")
        else:
            print_error(f"Error al deshabilitar firewall: {output}")
            log_action("Firewall", "Disable Firewall", f"Error al deshabilitar firewall: {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Firewall", "Disable Firewall", "Deshabilitación de firewall cancelada.")

def list_firewall_rules():
    print_header("Listar Reglas del Firewall")
    os_type = get_os_type()
    if os_type == 'windows':
        command = "netsh advfirewall firewall show rule name=all"
    else: # linux
        command = "ufw status verbose"
        output, status = execute_command(command, sudo=True)
        if status != 0:
            print_info("UFW no encontrado o no activo. Intentando con iptables...")
            command = "sudo iptables -L -n -v"
            output, status = execute_command(command, sudo=True)
    
    if status == 0:
        print_info("Reglas del Firewall:")
        print(output)
        log_action("Firewall", "List Rules", "Reglas del firewall listadas exitosamente.")
    else:
        print_error(f"Error al listar reglas del firewall: {output}")
        log_action("Firewall", "List Rules", f"Error al listar reglas del firewall: {output}")

def add_allow_port_rule():
    print_header("Añadir Regla (Permitir Puerto)")
    print_info("Esta operación requiere privilegios de administrador/root.")
    rule_name = get_user_input("Ingrese un nombre para la regla (ej. 'Permitir_SSH')")
    port = get_user_input("Ingrese el número de puerto a permitir (ej. 22, 8080)")
    protocol = get_user_input("Ingrese el protocolo (tcp/udp/any, dejar en blanco para 'any')").lower() or "any"
    direction = get_user_input("Ingrese la dirección (in/out, dejar en blanco para 'in')").lower() or "in"

    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall add rule name="{rule_name}" dir={direction} action=allow protocol={protocol} localport={port}'
    else: # linux (ufw)
        if direction == 'in':
            command = f"ufw allow {port}/{protocol}"
        elif direction == 'out':
            command = f"ufw allow out {port}/{protocol}"
        else:
            print_error("Dirección inválida. Use 'in' o 'out'.")
            return
        print_info("Si UFW no está en uso, necesitará reglas de iptables.")
        # Ejemplo iptables: sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    
    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input("¿Está seguro que desea añadir esta regla? (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Regla '{rule_name}' (permitir puerto {port}/{protocol}, {direction}) añadida exitosamente.")
            log_action("Firewall", "Add Rule", f"Regla '{rule_name}' (permitir puerto {port}/{protocol}, {direction}) añadida.")
        else:
            print_error(f"Error al añadir regla: {output}")
            log_action("Firewall", "Add Rule", f"Error al añadir regla '{rule_name}': {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Firewall", "Add Rule", "Adición de regla cancelada.")

def delete_allow_port_rule():
    print_header("Eliminar Regla (Permitir Puerto)")
    print_info("Esta operación requiere privilegios de administrador/root.")
    rule_name = get_user_input("Ingrese el nombre de la regla a eliminar (ej. 'Permitir_SSH')")
    
    os_type = get_os_type()
    if os_type == 'windows':
        command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
    else: # linux (ufw)
        # UFW no permite eliminar por nombre directo, hay que buscar la regla
        print_info("En Linux (UFW), la eliminación de reglas por nombre exacto no es directa. Se recomienda 'ufw status numbered' y eliminar por número.")
        print_info("Este script intentará eliminar una regla UFW basada en el nombre que se le dio al añadirla (menos fiable).")
        port = get_user_input("Ingrese el número de puerto de la regla a eliminar (ej. 22, 8080)")
        protocol = get_user_input("Ingrese el protocolo de la regla (tcp/udp/any, dejar en blanco para 'any')").lower() or "any"
        command = f"ufw delete allow {port}/{protocol}"

    print_info(f"Comando a ejecutar: {command}")
    confirm = get_user_input("¿Está seguro que desea eliminar esta regla? (s/N)").lower()
    if confirm == 's':
        output, status = execute_command(command, sudo=True)
        if status == 0:
            print_success(f"Regla '{rule_name}' eliminada exitosamente.")
            log_action("Firewall", "Delete Rule", f"Regla '{rule_name}' eliminada.")
        else:
            print_error(f"Error al eliminar regla: {output}")
            log_action("Firewall", "Delete Rule", f"Error al eliminar regla '{rule_name}': {output}")
    else:
        print_info("Operación cancelada.")
        log_action("Firewall", "Delete Rule", "Eliminación de regla cancelada.")

def generate_firewall_log():
    print_header("Generar Log de Firewall")
    log_action("Firewall", "Generate Log", "Generando log de gestión de firewall.")
    print_info("Generando informe de Estado del Firewall...")
    view_firewall_status()
    print_info("\nGenerando informe de Reglas del Firewall...")
    list_firewall_rules()
    print_success(f"Log de firewall generado en {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')}")