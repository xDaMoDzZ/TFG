# proxy_management/system_proxy.py

from utils import common
import os

def display_system_proxy_menu(os_type):
    """Muestra el submenú de gestión de proxy a nivel de sistema."""
    common.clear_screen()
    print(f"--- Gestión de Proxy de Sistema ({os_type}) ---")
    print("1. Ver Configuración de Proxy Actual")
    print("2. Configurar Proxy HTTP/HTTPS (Variables de Entorno - Linux/Windows)")
    print("3. Deshabilitar Proxy HTTP/HTTPS (Variables de Entorno - Linux/Windows)")
    if os_type == "Windows":
        print("4. Configurar Proxy en Configuración de Internet de Windows")
        print("5. Deshabilitar Proxy en Configuración de Internet de Windows")
    print("0. Volver al Menú Principal")

def view_current_proxy():
    print("\n--- Configuración de Proxy Actual (Variables de Entorno) ---")
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    no_proxy = os.getenv("NO_PROXY") or os.getenv("no_proxy")

    if http_proxy:
        print(f"HTTP_PROXY: {http_proxy}")
    if https_proxy:
        print(f"HTTPS_PROXY: {https_proxy}")
    if no_proxy:
        print(f"NO_PROXY: {no_proxy}")

    if not http_proxy and not https_proxy:
        print("No se encontraron variables de entorno HTTP_PROXY/HTTPS_PROXY.")
        
    print("\n--- Configuración de Proxy de Internet de Windows (solo en Windows) ---")
    # Para Windows, esto requeriría leer del registro o usar PowerShell
    # Por simplicidad, se indica que es manual o con PowerShell
    print("La configuración de proxy a nivel de sistema de Windows (regedit) debe ser consultada manualmente o vía PowerShell.")
    # Ejemplo de PowerShell para leer: Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' | Select-Object ProxyEnable,ProxyServer
    
    common.press_enter_to_continue()

def configure_env_proxy():
    proxy_address = input("Introduce la dirección del proxy (ej. http://proxy.example.com:8080): ")
    # Opcional: lista de exclusiones
    no_proxy = input("Introduce hosts a excluir (separados por coma, ej. localhost,127.0.0.1): ").strip()

    os.environ["HTTP_PROXY"] = proxy_address
    os.environ["HTTPS_PROXY"] = proxy_address
    if no_proxy:
        os.environ["NO_PROXY"] = no_proxy
    else:
        # Si se borra, asegurarse de que no haya una variable antigua
        if "NO_PROXY" in os.environ:
            del os.environ["NO_PROXY"]
        if "no_proxy" in os.environ: # Para asegurar ambos casos
            del os.environ["no_proxy"]


    print(f"Proxy HTTP/HTTPS configurado a: {proxy_address}")
    if no_proxy:
        print(f"Exclusiones configuradas: {no_proxy}")
    print("¡Advertencia! Estas configuraciones son solo para la sesión actual del script y no son persistentes.")
    print("Para hacerlas persistentes, necesitarías editarlas en los archivos de configuración del shell (.bashrc, .zshrc) en Linux o en las variables de entorno del sistema en Windows.")
    common.press_enter_to_continue()

def disable_env_proxy():
    if "HTTP_PROXY" in os.environ:
        del os.environ["HTTP_PROXY"]
    if "http_proxy" in os.environ:
        del os.environ["http_proxy"]
    if "HTTPS_PROXY" in os.environ:
        del os.environ["HTTPS_PROXY"]
    if "https_proxy" in os.environ:
        del os.environ["https_proxy"]
    if "NO_PROXY" in os.environ:
        del os.environ["NO_PROXY"]
    if "no_proxy" in os.environ:
        del os.environ["no_proxy"]

    print("Variables de entorno HTTP_PROXY, HTTPS_PROXY y NO_PROXY eliminadas para la sesión actual.")
    print("¡Advertencia! Esto no afecta la configuración de proxy persistente o a nivel de sistema en Windows.")
    common.press_enter_to_continue()

def configure_windows_internet_proxy():
    print("\n--- Configurar Proxy en Configuración de Internet de Windows ---")
    proxy_address = input("Introduce la dirección del proxy (ej. proxy.example.com:8080): ")
    # Para configurar el proxy a nivel de sistema en Windows, necesitamos usar PowerShell o manipular el registro.
    # Usaremos PowerShell para mayor seguridad y facilidad.

    # Comando PowerShell para habilitar y establecer el proxy
    # Internet Settings están en HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings
    # ProxyEnable (DWORD): 1 para habilitar, 0 para deshabilitar
    # ProxyServer (REG_SZ): "proxy.example.com:8080"
    # ProxyOverride (REG_SZ): "<local>;*.example.com"
    
    # Este comando solo configura el proxy para el usuario actual.
    # Para un proxy a nivel de sistema (afecta a todos los usuarios), la configuración es más compleja y puede requerir GPO.
    
    ps_script = f"""
    $regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'
    Set-ItemProperty -Path $regPath -Name ProxyEnable -Value 1 -Force
    Set-ItemProperty -Path $regPath -Name ProxyServer -Value '{proxy_address}' -Force
    Write-Host "Proxy de Internet de Windows configurado."
    """
    
    print("\nEjecutando comando PowerShell para configurar el proxy...")
    result = common.run_command(["powershell", "-Command", ps_script])
    
    if result and result.returncode == 0:
        print("Proxy de Internet de Windows configurado exitosamente.")
        print("Puede que necesites reiniciar aplicaciones para que los cambios surtan efecto.")
    else:
        print("Error al configurar el proxy de Internet de Windows.")
        if result: print(result.stderr)
    common.press_enter_to_continue()

def disable_windows_internet_proxy():
    print("\n--- Deshabilitar Proxy en Configuración de Internet de Windows ---")
    # Comando PowerShell para deshabilitar el proxy
    ps_script = """
    $regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'
    Set-ItemProperty -Path $regPath -Name ProxyEnable -Value 0 -Force
    Remove-ItemProperty -Path $regPath -Name ProxyServer -ErrorAction SilentlyContinue -Force
    Remove-ItemProperty -Path $regPath -Name ProxyOverride -ErrorAction SilentlyContinue -Force
    Write-Host "Proxy de Internet de Windows deshabilitado."
    """
    
    print("\nEjecutando comando PowerShell para deshabilitar el proxy...")
    result = common.run_command(["powershell", "-Command", ps_script])
    
    if result and result.returncode == 0:
        print("Proxy de Internet de Windows deshabilitado exitosamente.")
        print("Puede que necesites reiniciar aplicaciones para que los cambios surtan efecto.")
    else:
        print("Error al deshabilitar el proxy de Internet de Windows.")
        if result: print(result.stderr)
    common.press_enter_to_continue()

def proxy_management_menu(os_type):
    """Menú principal para la gestión de proxy a nivel de sistema."""
    while True:
        common.clear_screen()
        display_system_proxy_menu(os_type)
        choice = input("Su elección: ")

        if choice == '1':
            view_current_proxy()
        elif choice == '2':
            configure_env_proxy()
        elif choice == '3':
            disable_env_proxy()
        elif os_type == "Windows" and choice == '4':
            configure_windows_internet_proxy()
        elif os_type == "Windows" and choice == '5':
            disable_windows_internet_proxy()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()