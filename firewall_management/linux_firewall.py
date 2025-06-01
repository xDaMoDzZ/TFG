import subprocess
import sys
import os

# --- Helper function for command execution (_run_command) ---
def _run_command(command, check_success=True, capture_output=True, shell=False):
    """
    Executes a system command and handles its output and errors.

    Args:
        command (list or str): The command to execute. If a list, shell=False is recommended.
                               If a string, shell=True is recommended (less secure).
        check_success (bool): If True, raises a CalledProcessError if command returns non-zero.
        capture_output (bool): If True, captures stdout and stderr.
        shell (bool): If True, command is executed via the shell. Less secure for user input.

    Returns:
        subprocess.CompletedProcess: Object with execution results (stdout, stderr, returncode).
    Raises:
        subprocess.CalledProcessError: If check_success is True and command fails.
        FileNotFoundError: If the command is not found.
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

# --- Firewall Functions ---

def _get_firewall_command():
    """Detects and returns the appropriate firewall command (ufw or firewall-cmd)."""
    if _run_command(["which", "ufw"], check_success=False, capture_output=False).returncode == 0:
        return "ufw"
    elif _run_command(["which", "firewall-cmd"], check_success=False, capture_output=False).returncode == 0:
        return "firewall-cmd"
    return None

def enable_firewall():
    """Enables the system firewall."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No supported firewall command (ufw or firewall-cmd) found.", file=sys.stderr)
        return

    print(f"Attempting to enable firewall using {firewall_cmd}...")
    if firewall_cmd == "ufw":
        # Enable ufw, auto-confirm
        result = _run_command(["sudo", "ufw", "--force", "enable"])
    elif firewall_cmd == "firewall-cmd":
        # Start and enable firewalld service
        result = _run_command(["sudo", "systemctl", "start", "firewalld"])
        if result and result.returncode == 0:
            result = _run_command(["sudo", "systemctl", "enable", "firewalld"])
    
    if result and result.returncode == 0:
        print("Firewall enabled successfully.")
    elif result:
        print(f"Failed to enable firewall. Exit code: {result.returncode}", file=sys.stderr)

def disable_firewall():
    """Disables the system firewall."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No supported firewall command (ufw or firewall-cmd) found.", file=sys.stderr)
        return

    print(f"Attempting to disable firewall using {firewall_cmd}...")
    if firewall_cmd == "ufw":
        # Disable ufw, auto-confirm
        result = _run_command(["sudo", "ufw", "disable"])
    elif firewall_cmd == "firewall-cmd":
        # Stop and disable firewalld service
        result = _run_command(["sudo", "systemctl", "stop", "firewalld"])
        if result and result.returncode == 0:
            result = _run_command(["sudo", "systemctl", "disable", "firewalld"])

    if result and result.returncode == 0:
        print("Firewall disabled successfully.")
    elif result:
        print(f"Failed to disable firewall. Exit code: {result.returncode}", file=sys.stderr)

def add_firewall_rule(port, protocol, action="allow"):
    """Adds a firewall rule to allow/deny traffic on a specific port/protocol."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No supported firewall command (ufw or firewall-cmd) found.", file=sys.stderr)
        return

    print(f"Attempting to {action} traffic on port {port}/{protocol} using {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        result = _run_command(["sudo", "ufw", action, str(port), "/", protocol])
    elif firewall_cmd == "firewall-cmd":
        # Add rule to permanent and then reload
        result = _run_command(["sudo", "firewall-cmd", "--permanent", f"--{action}-port={port}/{protocol}"])
        if result and result.returncode == 0:
            _run_command(["sudo", "firewall-cmd", "--reload"]) # Reload to apply changes immediately
    
    if result and result.returncode == 0:
        print(f"Firewall rule to {action} {port}/{protocol} added successfully.")
    elif result:
        print(f"Failed to add firewall rule. Exit code: {result.returncode}", file=sys.stderr)

def delete_firewall_rule(port, protocol, action="allow"):
    """Deletes a firewall rule."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No supported firewall command (ufw or firewall-cmd) found.", file=sys.stderr)
        return

    print(f"Attempting to delete rule for {action} traffic on port {port}/{protocol} using {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        result = _run_command(["sudo", "ufw", "delete", action, str(port), "/", protocol])
    elif firewall_cmd == "firewall-cmd":
        # Remove rule from permanent and then reload
        result = _run_command(["sudo", "firewall-cmd", "--permanent", f"--remove-{action}-port={port}/{protocol}"])
        if result and result.returncode == 0:
            _run_command(["sudo", "firewall-cmd", "--reload"]) # Reload to apply changes immediately
    
    if result and result.returncode == 0:
        print(f"Firewall rule for {action} {port}/{protocol} deleted successfully.")
    elif result:
        print(f"Failed to delete firewall rule. Exit code: {result.returncode}", file=sys.stderr)

def list_firewall_rules():
    """Lists current firewall rules."""
    firewall_cmd = _get_firewall_command()
    if not firewall_cmd:
        print("No supported firewall command (ufw or firewall-cmd) found.", file=sys.stderr)
        return

    print(f"Listing firewall rules using {firewall_cmd}...")
    result = None
    if firewall_cmd == "ufw":
        result = _run_command(["sudo", "ufw", "status", "verbose"])
    elif firewall_cmd == "firewall-cmd":
        result = _run_command(["sudo", "firewall-cmd", "--list-all"])
    
    if result and result.returncode == 0:
        print(result.stdout)
    elif result:
        print(f"Failed to list firewall rules. Exit code: {result.returncode}", file=sys.stderr)

def manage_linux_firewall():
    """Main menu for Linux firewall management."""
    while True:
        print("\n--- Gestión de Firewall Linux ---")
        print("1. Habilitar Firewall")
        print("2. Deshabilitar Firewall")
        print("3. Añadir Regla (Permitir/Denegar)")
        print("4. Eliminar Regla")
        print("5. Listar Reglas")
        print("6. Volver al menú principal")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            enable_firewall()
        elif choice == '2':
            disable_firewall()
        elif choice == '3':
            port = input("Ingrese el número de puerto: ")
            protocol = input("Ingrese el protocolo (tcp/udp): ").lower()
            action = input("Ingrese la acción (allow/deny, por defecto 'allow'): ").lower() or "allow"
            if protocol not in ['tcp', 'udp']:
                print("Protocolo no válido. Debe ser 'tcp' o 'udp'.")
                continue
            try:
                int(port) # Check if port is a valid number
            except ValueError:
                print("Puerto no válido. Debe ser un número.")
                continue
            add_firewall_rule(port, protocol, action)
        elif choice == '4':
            port = input("Ingrese el número de puerto de la regla a eliminar: ")
            protocol = input("Ingrese el protocolo (tcp/udp): ").lower()
            action = input("Ingrese la acción (allow/deny, por defecto 'allow'): ").lower() or "allow"
            if protocol not in ['tcp', 'udp']:
                print("Protocolo no válido. Debe ser 'tcp' o 'udp'.")
                continue
            try:
                int(port) # Check if port is a valid number
            except ValueError:
                print("Puerto no válido. Debe ser un número.")
                continue
            delete_firewall_rule(port, protocol, action)
        elif choice == '5':
            list_firewall_rules()
        elif choice == '6':
            break
        else:
            print("Opción no válida. Intente de nuevo.")