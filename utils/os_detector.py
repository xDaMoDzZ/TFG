import sys

def detect_os():
    """
    Detecta el sistema operativo actual (Linux o Windows).
    """
    if sys.platform.startswith('linux'):
        return "Linux"
    elif sys.platform.startswith('win'):
        return "Windows"
    else:
        return "Unknown"

if __name__ == "__main__":
    # Pequeña prueba para verificar la detección
    print(f"Sistema Operativo detectado: {detect_os()}")