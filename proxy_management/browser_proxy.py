# proxy_management/browser_proxy.py

from utils import common

def display_browser_proxy_message():
    """Muestra un mensaje sobre la complejidad de la gestión de proxy de navegador."""
    common.clear_screen()
    print("--- Gestión de Proxy de Navegador ---")
    print("\nLa configuración de proxy para navegadores específicos es compleja y varía mucho entre ellos.")
    print("La mayoría de los navegadores modernos utilizan la configuración de proxy del sistema operativo.")
    print("Se recomienda configurar el proxy a nivel del sistema operativo para que los navegadores lo adopten.")
    print("\nConsidera usar las opciones de 'Gestión de Proxy de Sistema' para una configuración más efectiva.")
    common.press_enter_to_continue()

def browser_proxy_management_menu():
    """
    Menú de gestión de proxy de navegador.
    Solo muestra un mensaje informativo, ya que la gestión directa es inviable.
    """
    display_browser_proxy_message()