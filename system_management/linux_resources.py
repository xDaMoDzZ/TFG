import subprocess
import sys
import psutil # Keep psutil as it's a dedicated library for system info

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

# --- Resource Functions ---

def get_cpu_info():
    """Displays CPU information using psutil and lscpu."""
    print("--- Información de CPU ---")
    print(f"Número de CPUs (físicos): {psutil.cpu_count(logical=False)}")
    print(f"Número de CPUs (lógicos/hilos): {psutil.cpu_count(logical=True)}")
    print(f"Uso de CPU (último segundo): {psutil.cpu_percent(interval=1)}%")

    # More detailed info with lscpu
    print("\n--- Detalles de CPU (lscpu) ---")
    result = _run_command(["lscpu"], check_success=False)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la información detallada de la CPU (lscpu no encontrado o error).")


def get_memory_info():
    """Displays memory information using psutil and free."""
    print("\n--- Información de Memoria ---")
    mem = psutil.virtual_memory()
    print(f"Total: {mem.total / (1024**3):.2f} GB")
    print(f"Disponible: {mem.available / (1024**3):.2f} GB")
    print(f"Usado: {mem.used / (1024**3):.2f} GB")
    print(f"Porcentaje de uso: {mem.percent}%")

    # More detailed info with free -h
    print("\n--- Detalles de Memoria (free -h) ---")
    result = _run_command(["free", "-h"], check_success=False)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la información detallada de la memoria (free no encontrado o error).")


def get_disk_info():
    """Displays disk usage information using psutil and df -h."""
    print("\n--- Información de Disco ---")
    partitions = psutil.disk_partitions()
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            print(f"Dispositivo: {p.device}, Montaje: {p.mountpoint}")
            print(f"  Total: {usage.total / (1024**3):.2f} GB")
            print(f"  Usado: {usage.used / (1024**3):.2f} GB")
            print(f"  Disponible: {usage.free / (1024**3):.2f} GB")
            print(f"  Porcentaje de uso: {usage.percent}%")
        except PermissionError:
            print(f"  Permiso denegado para {p.mountpoint}")
        except Exception as e:
            print(f"  Error al obtener información de {p.mountpoint}: {e}")

    # More detailed info with df -h
    print("\n--- Detalles de Disco (df -h) ---")
    result = _run_command(["df", "-h"], check_success=False)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la información detallada del disco (df no encontrado o error).")


def list_running_processes():
    """Lists running processes using psutil and top/htop."""
    print("\n--- Procesos en Ejecución (Top 10 por CPU/Memoria) ---")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass # Ignore processes that disappear or deny access

    # Sort by CPU usage and then by memory usage
    processes.sort(key=lambda x: (x['cpu_percent'], x['memory_percent']), reverse=True)

    for i, p in enumerate(processes[:10]): # Top 10
        print(f"PID: {p['pid']}, Nombre: {p['name']}, CPU: {p['cpu_percent']}%, Memoria: {p['memory_percent']:.2f}%")

    # Offer to display more with a system command
    print("\n--- Información detallada de procesos (top/htop si está disponible) ---")
    if _run_command(["which", "htop"], check_success=False, capture_output=False).returncode == 0:
        print("Para ver una lista interactiva, use 'htop' en su terminal.")
    elif _run_command(["which", "top"], check_success=False, capture_output=False).returncode == 0:
        print("Para ver una lista interactiva, use 'top' en su terminal.")
    else:
        print("Instale 'htop' o 'top' para una visualización interactiva de procesos.")


def kill_process():
    """Kills a process by PID."""
    pid = input("Ingrese el PID del proceso a terminar: ")
    try:
        pid = int(pid)
    except ValueError:
        print("PID no válido. Debe ser un número.")
        return

    print(f"Attempting to kill process with PID: {pid}")
    # Use 'kill' command which is standard
    result = _run_command(["sudo", "kill", "-9", str(pid)], check_success=False) # -9 for forceful kill
    
    if result and result.returncode == 0:
        print(f"Proceso {pid} terminado exitosamente.")
    elif result:
        print(f"Falló la terminación del proceso {pid}. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles: {result.stderr.strip()}", file=sys.stderr)

def manage_linux_resources():
    """Main menu for Linux resource management."""
    while True:
        print("\n--- Gestión de Recursos Linux ---")
        print("1. Información de CPU")
        print("2. Información de Memoria")
        print("3. Información de Disco")
        print("4. Listar Procesos en Ejecución")
        print("5. Terminar un Proceso (PID)")
        print("6. Volver al menú principal")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            get_cpu_info()
        elif choice == '2':
            get_memory_info()
        elif choice == '3':
            get_disk_info()
        elif choice == '4':
            list_running_processes()
        elif choice == '5':
            kill_process()
        elif choice == '6':
            break
        else:
            print("Opción no válida. Intente de nuevo.")
