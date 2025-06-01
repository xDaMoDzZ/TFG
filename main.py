# main.py

import sys
from utils import os_detector, common
from user_management import linux_users, windows_users
from network_management import linux_networking, windows_networking
from firewall_management import linux_firewall, windows_firewall
from proxy_management import browser_proxy, system_proxy # Aunque browser_proxy será más un placeholder
from system_management import linux_resources, windows_resources

def display_main_menu(os_type):
    """
    Muestra el menú principal al usuario.
    """
    common.clear_screen()
    print(f"--- Administración de Redes y Sistema ({os_type}) ---")
    print("\nSeleccione una opción:")
    print("1. Gestión de Usuarios y Grupos")
    print("2. Gestión de Redes")
    print("3. Gestión de Firewalls")
    print("4. Gestión de Proxy de Navegador")
    print("5. Gestión y Monitorización de Recursos del Sistema")
    print("0. Salir")

    choice = input("Su elección: ")
    return choice

def main():
    """
    Función principal que orquesta el script.
    """
    os_type = os_detector.detect_os()
    print(f"Detectando sistema operativo: {os_type}")

    if not common.is_admin():
        print("\n¡ADVERTENCIA: Este script requiere permisos de administrador/root para funcionar correctamente!")
        print("Algunas funciones podrían no operar como se espera sin los permisos adecuados.")
        common.press_enter_to_continue()
        common.clear_screen() # Limpiar la advertencia

    while True:
        choice = display_main_menu(os_type)

        if choice == '1':
            if os_type == "Linux":
                linux_users.manage_linux_users()
            elif os_type == "Windows":
                windows_users.user_management_menu()
            else:
                print("Gestión de usuarios no disponible para este SO.")
        elif choice == '2':
            if os_type == "Linux":
                linux_networking.network_management_menu_linux()
            elif os_type == "Windows":
                windows_networking.network_management_menu()
            else:
                print("Gestión de redes no disponible para este SO.")
        elif choice == '3':
            if os_type == "Linux":
                linux_firewall.manage_linux_firewall()
            elif os_type == "Windows":
                windows_firewall.firewall_management_menu()
            else:
                print("Gestión de firewall no disponible para este SO.")
        elif choice == '4':
            system_proxy.proxy_management_menu(os_type)
        elif choice == '5':
            if os_type == "Linux":
                linux_resources.manage_linux_resources()
            elif os_type == "Windows":
                windows_resources.system_monitoring_menu()
            else:
                print("Monitorización de recursos no disponible para este SO.")
        elif choice == '0':
            print("Saliendo del script...")
            break
        else:
            print("Opción no válida. Por favor, selecciona una opción del menú.")
            common.press_enter_to_continue()

if __name__ == "__main__":
    main()