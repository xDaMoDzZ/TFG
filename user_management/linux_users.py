import subprocess
import sys
import os

# Eliminamos la importación de 'common'

def _run_command(command, check_success=True, capture_output=True, shell=False):
    """
    Ejecuta un comando del sistema y maneja su salida y errores.
    
    Args:
        command (list o str): El comando a ejecutar. Si es una lista, se recomienda
                              shell=False para evitar inyección de comandos.
                              Si es una cadena, se recomienda shell=True.
        check_success (bool): Si es True, lanza una excepción CalledProcessError
                              si el comando devuelve un código de salida distinto de cero.
        capture_output (bool): Si es True, captura stdout y stderr.
        shell (bool): Si es True, el comando se ejecuta a través del shell.
                      Esto es menos seguro si el comando contiene entradas de usuario.
                      Se recomienda False y pasar el comando como una lista.

    Returns:
        subprocess.CompletedProcess: Objeto que contiene el resultado de la ejecución.
                                     (stdout, stderr, returncode).
    Raises:
        subprocess.CalledProcessError: Si check_success es True y el comando falla.
        FileNotFoundError: Si el comando no se encuentra.
    """
    try:
        result = subprocess.run(
            command,
            check=check_success,
            capture_output=capture_output,
            text=True,  # Decodifica stdout/stderr como texto usando la codificación por defecto
            shell=shell
        )
        if capture_output:
            # print(f"STDOUT: {result.stdout.strip()}") # Para depuración
            # print(f"STDERR: {result.stderr.strip()}") # Para depuración
            pass
        return result
    except FileNotFoundError:
        print(f"Error: Comando '{command[0] if isinstance(command, list) else command.split()[0]}' no encontrado. Asegúrate de que esté instalado y en tu PATH.", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None # Devuelve None si el comando no se encuentra y no se debe lanzar excepción
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar comando: {e}", file=sys.stderr)
        print(f"STDOUT: {e.stdout}", file=sys.stderr)
        print(f"STDERR: {e.stderr}", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None # Devuelve None si el comando falla y no se debe lanzar excepción
    except Exception as e:
        print(f"Error inesperado al ejecutar el comando: {e}", file=sys.stderr)
        if check_success:
            sys.exit(1)
        return None

def add_user(username, password):
    """Añade un nuevo usuario al sistema Linux."""
    print(f"Intentando añadir usuario: {username}")
    
    # Crear el usuario
    # -m: crea el directorio home
    # -s /bin/bash: establece bash como shell por defecto
    result_useradd = _run_command(["sudo", "useradd", "-m", "-s", "/bin/bash", username], check_success=False)
    
    if result_useradd and result_useradd.returncode == 0:
        print(f"Usuario '{username}' creado exitosamente.")
        # Establecer la contraseña
        # -p: especifica la contraseña (usar 'passwd' para mayor seguridad en sistemas interactivos)
        # En sistemas no interactivos, echo y passwd pueden ser complicados
        # Una forma común para scripts es con `chpasswd` o `passwd --stdin`
        # Aquí usamos echo y passwd --stdin. Esto requiere sudo para passwd.
        try:
            # Aseguramos que el stdin se envíe correctamente.
            # No usamos shell=True aquí por seguridad.
            passwd_process = subprocess.run(
                ["sudo", "chpasswd"],
                input=f"{username}:{password}".encode('utf-8'), # Envía usuario:contraseña como bytes
                capture_output=True,
                check=True
            )
            print(f"Contraseña establecida para '{username}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error al establecer la contraseña para '{username}':", file=sys.stderr)
            print(f"STDOUT: {e.stdout}", file=sys.stderr)
            print(f"STDERR: {e.stderr}", file=sys.stderr)
            # Intentar limpiar el usuario si la contraseña falla
            _run_command(["sudo", "userdel", "-r", username], check_success=False)
            sys.exit(1)
        except Exception as e:
            print(f"Error inesperado al establecer la contraseña: {e}", file=sys.stderr)
            _run_command(["sudo", "userdel", "-r", username], check_success=False)
            sys.exit(1)

    elif result_useradd:
        # El comando useradd falló. El error ya se imprimió por _run_command si check_success=True.
        # Si returncode no es 0, hubo un error.
        print(f"Falló la creación del usuario '{username}'. Código de salida: {result_useradd.returncode}", file=sys.stderr)
        if result_useradd.stderr:
            print(f"Detalles del error: {result_useradd.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def delete_user(username):
    """Elimina un usuario del sistema Linux."""
    print(f"Intentando eliminar usuario: {username}")
    # -r: elimina también el directorio home del usuario
    result = _run_command(["sudo", "userdel", "-r", username], check_success=False)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' eliminado exitosamente.")
    elif result:
        print(f"Falló la eliminación del usuario '{username}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def list_users():
    """Lista los usuarios existentes en el sistema Linux."""
    print("Listando usuarios del sistema:")
    # Puedes usar 'cut' para extraer solo el nombre de usuario
    result = _run_command(["getent", "passwd"])
    if result:
        users = []
        for line in result.stdout.splitlines():
            parts = line.split(':')
            if len(parts) > 0:
                username = parts[0]
                # Filtrar usuarios del sistema, generalmente UID < 1000,
                # o por shell (no /sbin/nologin, /bin/false, etc.)
                uid = int(parts[2])
                shell = parts[6]
                if uid >= 1000 and not shell.endswith("nologin") and not shell.endswith("false"):
                    users.append(username)
        
        if users:
            for user in users:
                print(f"- {user}")
        else:
            print("No se encontraron usuarios regulares del sistema.")
    else:
        print("No se pudieron listar los usuarios.")


def change_password(username, new_password):
    """Cambia la contraseña de un usuario existente."""
    print(f"Intentando cambiar contraseña para usuario: {username}")
    # Usa 'chpasswd' con sudo y stdin para establecer la contraseña de forma no interactiva
    try:
        passwd_process = subprocess.run(
            ["sudo", "chpasswd"],
            input=f"{username}:{new_password}".encode('utf-8'),
            capture_output=True,
            check=True
        )
        print(f"Contraseña cambiada exitosamente para '{username}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error al cambiar la contraseña para '{username}':", file=sys.stderr)
        print(f"STDOUT: {e.stdout}", file=sys.stderr)
        print(f"STDERR: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al cambiar la contraseña: {e}", file=sys.stderr)
        sys.exit(1)

def enable_user(username):
    """Habilita un usuario (desbloquea una cuenta si está bloqueada)."""
    # En Linux, no hay un comando 'enable_user' directo como tal.
    # Se suele hacer quitando el '!' del campo de la contraseña en /etc/shadow
    # o usando `usermod -U`.
    print(f"Intentando habilitar usuario: {username}")
    result = _run_command(["sudo", "usermod", "-U", username], check_success=False)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' habilitado exitosamente (si estaba deshabilitado).")
    elif result:
        print(f"Falló la habilitación del usuario '{username}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def disable_user(username):
    """Deshabilita un usuario (bloquea la cuenta para que no pueda iniciar sesión)."""
    # En Linux, esto se hace con 'usermod -L' (bloquea la contraseña)
    print(f"Intentando deshabilitar usuario: {username}")
    result = _run_command(["sudo", "usermod", "-L", username], check_success=False)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' deshabilitado exitosamente.")
    elif result:
        print(f"Falló la deshabilitación del usuario '{username}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def manage_linux_users():
    """Menú principal para la gestión de usuarios Linux."""
    while True:
        print("\n--- Gestión de Usuarios Linux ---")
        print("1. Añadir usuario")
        print("2. Eliminar usuario")
        print("3. Listar usuarios")
        print("4. Cambiar contraseña de usuario")
        print("5. Habilitar usuario")
        print("6. Deshabilitar usuario")
        print("7. Volver al menú principal")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            username = input("Ingrese el nombre de usuario a añadir: ")
            password = input("Ingrese la contraseña para el usuario: ")
            add_user(username, password)
        elif choice == '2':
            username = input("Ingrese el nombre de usuario a eliminar: ")
            delete_user(username)
        elif choice == '3':
            list_users()
        elif choice == '4':
            username = input("Ingrese el nombre de usuario cuya contraseña desea cambiar: ")
            new_password = input("Ingrese la nueva contraseña: ")
            change_password(username, new_password)
        elif choice == '5':
            username = input("Ingrese el nombre de usuario a habilitar: ")
            enable_user(username)
        elif choice == '6':
            username = input("Ingrese el nombre de usuario a deshabilitar: ")
            disable_user(username)
        elif choice == '7':
            break
        else:
            print("Opción no válida. Intente de nuevo.")

# Para pruebas directas (no se ejecutará si se importa como módulo)
if __name__ == "__main__":
    if sys.platform.startswith("linux"):
        manage_linux_users()
    else:
        print("Este script está diseñado para sistemas operativos Linux.")