# system_monitoring/windows_resources.py

from utils import common
import psutil
import time

def display_monitoring_menu():
    """Muestra el submenú de monitorización de recursos en Windows."""
    common.clear_screen()
    print("--- Gestión y Monitorización de Recursos (Windows) ---")
    print("1. Ver Uso de CPU")
    print("2. Ver Uso de Memoria")
    print("3. Ver Uso de Disco")
    print("4. Listar Procesos")
    print("5. Mostrar Información de Red")
    print("0. Volver al Menú Principal")

def view_cpu_usage():
    print("\n--- Uso de CPU (Windows) ---")
    print("Obteniendo uso de CPU (esto puede tardar unos segundos)...")
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"Uso de CPU: {cpu_percent}%")
        print(f"Número de núcleos lógicos: {psutil.cpu_count(logical=True)}")
        print(f"Número de núcleos físicos: {psutil.cpu_count(logical=False)}")
    except Exception as e:
        print(f"Error al obtener el uso de CPU: {e}")
    common.press_enter_to_continue()

def view_memory_usage():
    print("\n--- Uso de Memoria (Windows) ---")
    try:
        mem = psutil.virtual_memory()
        print(f"Total: {mem.total / (1024**3):.2f} GB")
        print(f"Disponible: {mem.available / (1024**3):.2f} GB")
        print(f"Usada: {mem.used / (1024**3):.2f} GB")
        print(f"Porcentaje: {mem.percent}%")
        
        swap = psutil.swap_memory()
        print("\n--- Uso de Memoria de Paginación (Swap) ---")
        print(f"Total: {swap.total / (1024**3):.2f} GB")
        print(f"Usada: {swap.used / (1024**3):.2f} GB")
        print(f"Porcentaje: {swap.percent}%")
    except Exception as e:
        print(f"Error al obtener el uso de memoria: {e}")
    common.press_enter_to_continue()

def view_disk_usage():
    print("\n--- Uso de Disco (Windows) ---")
    try:
        partitions = psutil.disk_partitions(all=False) # Solo particiones físicas
        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                print(f"  Unidad: {p.device}")
                print(f"  Punto de montaje: {p.mountpoint}")
                print(f"  Tipo de sistema de archivos: {p.fstype}")
                print(f"  Total: {usage.total / (1024**3):.2f} GB")
                print(f"  Usado: {usage.used / (1024**3):.2f} GB")
                print(f"  Libre: {usage.free / (1024**3):.2f} GB")
                print(f"  Porcentaje: {usage.percent}%")
                print("-" * 30)
            except Exception as e:
                print(f"Error al obtener uso de disco para {p.mountpoint}: {e}")
    except Exception as e:
        print(f"Error al listar las particiones de disco: {e}")
    common.press_enter_to_continue()

def list_processes():
    print("\n--- Listado de Procesos (Windows) ---")
    print("{:<7} {:<15} {:<8} {:<8} {:<30}".format("PID", "Usuario", "CPU%", "Mem%", "Nombre"))
    print("-" * 70)
    try:
        # Ordenar por uso de CPU para ver los procesos más activos
        processes = sorted(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']),
                           key=lambda p: p.info['cpu_percent'], reverse=True)
        for p in processes[:20]: # Mostrar los 20 procesos principales
            try:
                p_info = p.info
                print(f"{p_info['pid']:<7} {str(p_info['username'])[:15]:<15} {p_info['cpu_percent']:.1f}% {p_info['memory_percent']:.1f}% {p_info['name'][:30]:<30}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Proceso ya no existe o acceso denegado
                continue
    except Exception as e:
        print(f"Error al listar procesos: {e}")
    common.press_enter_to_continue()

def show_network_info():
    print("\n--- Información de Red (Windows) ---")
    print("Estadísticas de red:")
    try:
        net_io = psutil.net_io_counters(pernic=True)
        for interface, stats in net_io.items():
            print(f"  Interfaz: {interface}")
            print(f"    Bytes enviados: {stats.bytes_sent / (1024**2):.2f} MB")
            print(f"    Bytes recibidos: {stats.bytes_recv / (1024**2):.2f} MB")
            print(f"    Paquetes enviados: {stats.packets_sent}")
            print(f"    Paquetes recibidos: {stats.packets_recv}")
            print("-" * 30)
        
        print("\nDirecciones IP:")
        net_if_addrs = psutil.net_if_addrs()
        for interface, addrs in net_if_addrs.items():
            print(f"  Interfaz: {interface}")
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    print(f"    MAC: {addr.address}")
                elif addr.family == psutil.AF_INET:
                    print(f"    IPv4: {addr.address}/{addr.netmask} (Broadcast: {addr.broadcast})")
                elif addr.family == psutil.AF_INET6:
                    print(f"    IPv6: {addr.address}")
            print("-" * 30)

    except Exception as e:
        print(f"Error al obtener información de red: {e}")
    common.press_enter_to_continue()

def system_monitoring_menu():
    """Menú principal para la monitorización de recursos en Windows."""
    while True:
        common.clear_screen()
        display_monitoring_menu()
        choice = input("Su elección: ")

        if choice == '1':
            view_cpu_usage()
        elif choice == '2':
            view_memory_usage()
        elif choice == '3':
            view_disk_usage()
        elif choice == '4':
            list_processes()
        elif choice == '5':
            show_network_info()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()