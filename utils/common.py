# utils/common.py

import os
import sys

def clear_screen():
    """
    Limpia la pantalla de la consola.
    """
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        # Asume sistemas tipo Unix/Linux
        os.system('clear')

def press_enter_to_continue():
    """
    Pide al usuario que presione Enter para continuar.
    """
    input("\nPresiona Enter para continuar...")

def run_command(command, check=True, capture_output=False, text=True):
    """
    Ejecuta un comando del sistema y maneja posibles errores.
    Args:
        command (list): Lista de strings que representan el comando y sus argumentos.
        check (bool): Si es True, lanza una CalledProcessError si el comando retorna un código de salida no cero.
        capture_output (bool): Si es True, la salida estándar y de error se capturan.
        text (bool): Si es True, la salida se decodifica como texto.

    Returns:
        subprocess.CompletedProcess: Objeto que contiene el resultado del comando.
    """
    import subprocess
    try:
        result = subprocess.run(command, check=check, capture_output=capture_output, text=text, shell=False)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {' '.join(command)}")
        print(f"Código de salida: {e.returncode}")
        if e.stdout:
            print(f"Salida estándar: {e.stdout}")
        if e.stderr:
            print(f"Salida de error: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"Error: El comando '{command[0]}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None

def is_admin():
    """
    Comprueba si el script se está ejecutando con permisos de administrador/root.
    """
    if sys.platform.startswith('win'):
        try:
            # Importa solo si es Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    else:
        # Asume sistemas tipo Unix/Linux
        return os.geteuid() == 0