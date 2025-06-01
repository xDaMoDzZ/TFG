import subprocess
import sys
import os

from utils import common

def _run_command(command, check_success=True, capture_output=True, shell=False):
    """
    Ejecuta un comando del sistema y maneja su salida y errores.
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

def display_firewall_menu():
    """Muestra el submenú de gestión de firewall en Linux."""
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

def _get_firewall_command():
    """Detecta y devuelve el comando de firewall apropiado (ufw o firewall-cmd)."""
    if _run_command(["which", "ufw"], check_success=False, capture_output=False).returncode == 0:
        return "ufw"
    elif _run_command(["which", "firewall-cmd"], check_success=False, capture_output=False).returncode == 0:
        return "firewall-cmd"
    return None

def view_firewall_status():
    """Muestra el estado actual del firewall."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"--- Estado del Firewall ({firewall_cmd}) ---")
    if firewall_cmd == "ufw":
        result = _run_command(["sudo", "ufw", "status", "verbose"])
    elif firewall_cmd == "firewall-cmd":
        print("Estado del servicio:")
        _run_command(["sudo", "systemctl", "status", "firewalld"], check_success=False)
        print("\nConfiguración actual:")
        result = _run_command(["sudo", "firewall-cmd", "--list-all"])
    
    if result and result.returncode == 0:
        print(result.stdout)
    elif result:
        print(f"Falló al obtener el estado del firewall. Código de salida: {result.returncode}", file=sys.stderr)

def enable_firewall():
    """Habilita el firewall del sistema (generalmente para todos los perfiles activos)."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"Intentando habilitar el firewall usando {firewall_cmd}...")
    if firewall_cmd == "ufw":
        # Enable ufw, auto-confirm
        result = _run_command(["sudo", "ufw", "--force", "enable"])
    elif firewall_cmd == "firewall-cmd":
        # Start and enable firewalld service
        result = _run_command(["sudo", "systemctl", "start", "firewalld"])
        if result and result.returncode == 0:
            result = _run_command(["sudo", "systemctl", "enable", "firewalld"])
    
    if result and result.returncode == 0:
        print("Firewall habilitado exitosamente.")
    elif result:
        print(f"Falló la habilitación del firewall. Código de salida: {result.returncode}", file=sys.stderr)

def disable_firewall():
    """Deshabilita el firewall del sistema (generalmente para todos los perfiles)."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"Intentando deshabilitar el firewall usando {firewall_cmd}...")
    if firewall_cmd == "ufw":
        # Disable ufw, auto-confirm
        result = _run_command(["sudo", "ufw", "disable"])
    elif firewall_cmd == "firewall-cmd":
        # Stop and disable firewalld service
        result = _run_command(["sudo", "systemctl", "stop", "firewalld"])
        if result and result.returncode == 0:
            result = _run_command(["sudo", "systemctl", "disable", "firewalld"])

    if result and result.returncode == 0:
        print("Firewall deshabilitado exitosamente.")
    elif result:
        print(f"Falló la deshabilitación del firewall. Código de salida: {result.returncode}", file=sys.stderr)

def add_input_rule(port, protocol, action="allow"):
    """Añade una regla de entrada (inbound) para permitir/denegar tráfico en un puerto/protocolo."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"Intentando añadir regla de entrada para {action} tráfico en puerto {port}/{protocol} usando {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        # UFW rules are usually ingress by default unless 'out' specified
        result = _run_command(["sudo", "ufw", action, str(port), "/", protocol])
    elif firewall_cmd == "firewall-cmd":
        # Add rule to permanent and then reload
        # --add-port implies inbound
        result = _run_command(["sudo", "firewall-cmd", "--permanent", f"--add-port={port}/{protocol}"])
        if result and result.returncode == 0:
            _run_command(["sudo", "firewall-cmd", "--reload"]) # Reload to apply changes immediately
    
    if result and result.returncode == 0:
        print(f"Regla de entrada para {action} {port}/{protocol} añadida exitosamente.")
    elif result:
        print(f"Falló la adición de la regla de entrada. Código de salida: {result.returncode}", file=sys.stderr)

def delete_input_rule(port, protocol, action="allow"):
    """Elimina una regla de entrada (inbound)."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"Intentando eliminar regla de entrada para {action} tráfico en puerto {port}/{protocol} usando {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        result = _run_command(["sudo", "ufw", "delete", action, str(port), "/", protocol])
    elif firewall_cmd == "firewall-cmd":
        result = _run_command(["sudo", "firewall-cmd", "--permanent", f"--remove-port={port}/{protocol}"])
        if result and result.returncode == 0:
            _run_command(["sudo", "firewall-cmd", "--reload"])
    
    if result and result.returncode == 0:
        print(f"Regla de entrada para {action} {port}/{protocol} eliminada exitosamente.")
    elif result:
        print(f"Falló la eliminación de la regla de entrada. Código de salida: {result.returncode}", file=sys.stderr)

def add_output_rule(port, protocol, action="allow"):
    """Añade una regla de salida (outbound) para permitir/denegar tráfico en un puerto/protocolo."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"Intentando añadir regla de salida para {action} tráfico en puerto {port}/{protocol} usando {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        # UFW requires explicit 'out' for output rules
        result = _run_command(["sudo", "ufw", action, "out", str(port), "/", protocol])
    elif firewall_cmd == "firewall-cmd":
        # firewall-cmd generally focuses on inbound. Outbound rules are more complex
        # and usually managed through rich rules or direct nftables/iptables.
        # For simplicity, we'll try a basic rich rule for OUTPUT
        print("FirewallD (firewall-cmd) tiene un manejo de reglas de salida más complejo.")
        print("Esta función intentará añadir una 'rich rule' para permitir tráfico de salida.")
        # Example rich rule: allow all outbound from this host to a specific port
        # This is a simplification; true outbound filtering requires more context.
        rich_rule = f'rule family="ipv4" destination address="0.0.0.0/0" port port="{port}" protocol="{protocol}" accept'
        result = _run_command(["sudo", "firewall-cmd", "--permanent", "--add-rich-rule", rich_rule])
        if result and result.returncode == 0:
            _run_command(["sudo", "firewall-cmd", "--reload"])
    
    if result and result.returncode == 0:
        print(f"Regla de salida para {action} {port}/{protocol} añadida exitosamente.")
    elif result:
        print(f"Falló la adición de la regla de salida. Código de salida: {result.returncode}", file=sys.stderr)

def delete_output_rule(port, protocol, action="allow"):
    """Elimina una regla de salida (outbound)."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"Intentando eliminar regla de salida para {action} tráfico en puerto {port}/{protocol} usando {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        result = _run_command(["sudo", "ufw", "delete", action, "out", str(port), "/", protocol])
    elif firewall_cmd == "firewall-cmd":
        print("FirewallD (firewall-cmd) tiene un manejo de reglas de salida más complejo.")
        print("Esta función intentará eliminar una 'rich rule' existente.")
        rich_rule = f'rule family="ipv4" destination address="0.0.0.0/0" port port="{port}" protocol="{protocol}" accept'
        result = _run_command(["sudo", "firewall-cmd", "--permanent", "--remove-rich-rule", rich_rule])
        if result and result.returncode == 0:
            _run_command(["sudo", "firewall-cmd", "--reload"])
    
    if result and result.returncode == 0:
        print(f"Regla de salida para {action} {port}/{protocol} eliminada exitosamente.")
    elif result:
        print(f"Falló la eliminación de la regla de salida. Código de salida: {result.returncode}", file=sys.stderr)

def reset_firewall_to_defaults():
    """Restablece el firewall a los valores predeterminados (resetea todas las reglas)."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No se encontró ningún comando de firewall compatible (ufw o firewall-cmd).", file=sys.stderr)
        return

    print(f"ADVERTENCIA: Esto restablecerá el firewall a sus valores predeterminados y eliminará todas las reglas existentes.")
    confirm = input("¿Está seguro de que desea continuar? (sí/no): ").lower()
    if confirm != 'sí':
        print("Operación de restablecimiento cancelada.")
        return

    print(f"Intentando restablecer el firewall usando {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        # UFW reset requires confirmation, --force bypasses it
        result = _run_command(["sudo", "ufw", "--force", "reset"])
        if result and result.returncode == 0:
            # Re-enable ufw after reset, as reset disables it
            _run_command(["sudo", "ufw", "--force", "enable"])
    elif firewall_cmd == "firewall-cmd":
        # Remove all permanent rules from the public zone (common default)
        # and then reload. This simulates a reset.
        result = _run_command(["sudo", "firewall-cmd", "--zone=public", "--permanent", "--remove-all"], check_success=False)
        if result and result.returncode == 0:
            result = _run_command(["sudo", "firewall-cmd", "--reload"])
        else:
            print("Pudo haber un problema al eliminar todas las reglas de la zona pública. Intentando resetear el servicio.")
            result = _run_command(["sudo", "systemctl", "restart", "firewalld"]) # Restart service to clear state

    if result and result.returncode == 0:
        print("Firewall restablecido a los valores predeterminados exitosamente.")
    elif result:
        print(f"Falló el restablecimiento del firewall. Código de salida: {result.returncode}", file=sys.stderr)

def manage_linux_firewall():
    """Menú principal para la gestión de Firewall Linux."""
    while True:
        common.clear_screen()
        display_firewall_menu()
        choice = input("Seleccione una opción: ")

        if choice == '1':
            view_firewall_status()
        elif choice == '2':
            enable_firewall()
        elif choice == '3':
            disable_firewall()
        elif choice == '4':
            port = input("Ingrese el número de puerto: ")
            protocol = input("Ingrese el protocolo (tcp/udp): ").lower()
            if protocol not in ['tcp', 'udp']:
                print("Protocolo no válido. Debe ser 'tcp' o 'udp'.")
                continue
            try:
                int(port) # Check if port is a valid number
            except ValueError:
                print("Puerto no válido. Debe ser un número.")
                continue
            add_input_rule(port, protocol)
        elif choice == '5':
            port = input("Ingrese el número de puerto de la regla de entrada a eliminar: ")
            protocol = input("Ingrese el protocolo (tcp/udp): ").lower()
            if protocol not in ['tcp', 'udp']:
                print("Protocolo no válido. Debe ser 'tcp' o 'udp'.")
                continue
            try:
                int(port)
            except ValueError:
                print("Puerto no válido. Debe ser un número.")
                continue
            delete_input_rule(port, protocol)
        elif choice == '6':
            port = input("Ingrese el número de puerto: ")
            protocol = input("Ingrese el protocolo (tcp/udp): ").lower()
            if protocol not in ['tcp', 'udp']:
                print("Protocolo no válido. Debe ser 'tcp' o 'udp'.")
                continue
            try:
                int(port)
            except ValueError:
                print("Puerto no válido. Debe ser un número.")
                continue
            add_output_rule(port, protocol)
        elif choice == '7':
            port = input("Ingrese el número de puerto de la regla de salida a eliminar: ")
            protocol = input("Ingrese el protocolo (tcp/udp): ").lower()
            if protocol not in ['tcp', 'udp']:
                print("Protocolo no válido. Debe ser 'tcp' o 'udp'.")
                continue
            try:
                int(port)
            except ValueError:
                print("Puerto no válido. Debe ser un número.")
                continue
            delete_output_rule(port, protocol)
        elif choice == '8':
            reset_firewall_to_defaults()
        elif choice == '0':
            break
        else:
            print("Opción no válida. Intente de nuevo.")
        common.press_enter_to_continue()