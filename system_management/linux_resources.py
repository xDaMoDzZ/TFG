import subprocess
import sys
import os
import re
import psutil
from utils import common

# --- Helper function for command execution (_run_command) ---
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

def display_monitoring_menu():
    """Muestra el submenú de monitorización de recursos en Linux."""
    common.clear_screen()
    print("--- Gestión y Monitorización de Recursos (Windows) ---")
    print("1. Ver Uso de CPU")
    print("2. Ver Uso de Memoria")
    print("3. Ver Uso de Disco")
    print("4. Listar Procesos")
    print("5. Mostrar Información de Red")
    print("0. Volver al Menú Principal")

def _clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def _press_enter_to_continue():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    input("\nPresione Enter para continuar...")

def get_cpu_info():
    """Muestra información de la CPU usando psutil y lscpu."""
    _clear_screen()
    print("--- Información de CPU ---")
    print(f"Número de CPUs (físicos): {psutil.cpu_count(logical=False)}")
    print(f"Número de CPUs (lógicos/hilos): {psutil.cpu_count(logical=True)}")
    print(f"Uso de CPU (último segundo): {psutil.cpu_percent(interval=1)}%")

    print("\n--- Detalles de CPU (lscpu) ---")
    result = _run_command(["lscpu"], check_success=False)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la información detallada de la CPU (lscpu no encontrado o error).")
    _press_enter_to_continue()

def get_memory_info():
    """Muestra información de la memoria usando psutil y free."""
    _clear_screen()
    print("\n--- Información de Memoria ---")
    mem = psutil.virtual_memory()
    print(f"Total: {mem.total / (1024**3):.2f} GB")
    print(f"Disponible: {mem.available / (1024**3):.2f} GB")
    print(f"Usado: {mem.used / (1024**3):.2f} GB")
    print(f"Porcentaje de uso: {mem.percent}%")

    print("\n--- Detalles de Memoria (free -h) ---")
    result = _run_command(["free", "-h"], check_success=False)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la información detallada de la memoria (free no encontrado o error).")
    _press_enter_to_continue()

def get_disk_info():
    """Muestra información del uso de disco usando psutil y df -h."""
    _clear_screen()
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

    print("\n--- Detalles de Disco (df -h) ---")
    result = _run_command(["df", "-h"], check_success=False)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudo obtener la información detallada del disco (df no encontrado o error).")
    _press_enter_to_continue()

def list_running_processes():
    """Lista los procesos en ejecución usando psutil y top/htop."""
    _clear_screen()
    print("\n--- Procesos en Ejecución (Top 10 por CPU/Memoria) ---")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    processes.sort(key=lambda x: (x['cpu_percent'], x['memory_percent']), reverse=True)

    for i, p in enumerate(processes[:10]):
        print(f"PID: {p['pid']}, Nombre: {p['name']}, CPU: {p['cpu_percent']}%, Memoria: {p['memory_percent']:.2f}%")

    print("\n--- Información detallada de procesos (top/htop si está disponible) ---")
    if _run_command(["which", "htop"], check_success=False, capture_output=False).returncode == 0:
        print("Para ver una lista interactiva, use 'htop' en su terminal.")
    elif _run_command(["which", "top"], check_success=False, capture_output=False).returncode == 0:
        print("Para ver una lista interactiva, use 'top' en su terminal.")
    else:
        print("Instale 'htop' o 'top' para una visualización interactiva de procesos.")
    _press_enter_to_continue()

def get_network_info():
    """Muestra información de red del sistema Linux (interfaces, direcciones IP)."""
    _clear_screen()
    print("\n--- Información de Red ---")
    result_ip = _run_command(["ip", "a"], capture_output=True, check_success=False)
    if result_ip and result_ip.returncode == 0:
        print("--- Detalles de Interfaces de Red (ip a) ---")
        print(result_ip.stdout)
    else:
        print("No se pudo obtener la configuración de interfaces de red (ip a no encontrado o error).")

    print("\n--- Estadísticas de Red (netstat -s) ---")
    result_netstat = _run_command(["netstat", "-s"], capture_output=True, check_success=False)
    if result_netstat and result_netstat.returncode == 0:
        print(result_netstat.stdout)
    else:
        print("No se pudieron obtener las estadísticas de red (netstat -s no encontrado o error).")
    
    print("\n--- Conexiones de Red Abiertas (netstat -tuln) ---")
    result_connections = _run_command(["netstat", "-tuln"], capture_output=True, check_success=False)
    if result_connections and result_connections.returncode == 0:
        print(result_connections.stdout)
    else:
        print("No se pudieron obtener las conexiones de red (netstat -tuln no encontrado o error).")

    _press_enter_to_continue()

def manage_linux_resources():
    """Menú principal para la gestión y monitorización de recursos Linux."""
    while True:
        common._clear_screen()
        display_monitoring_menu()
        choice = input("Seleccione una opción: ")

        if choice == '1':
            get_cpu_info()
        elif choice == '2':
            get_memory_info()
        elif choice == '3':
            get_disk_info()
        elif choice == '4':
            list_running_processes()
        elif choice == '5': # Nueva opción
            get_network_info()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")
        common.press_enter_to_continue()