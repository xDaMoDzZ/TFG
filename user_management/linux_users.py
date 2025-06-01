import subprocess
import sys
import os

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
            pass
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

# --- Funciones de Gestión de Usuarios ---

def add_user(username, password):
    """Añade un nuevo usuario al sistema Linux."""
    print(f"Intentando añadir usuario: {username}")
    
    result_useradd = _run_command(["sudo", "useradd", "-m", "-s", "/bin/bash", username], check_success=False)
    
    if result_useradd and result_useradd.returncode == 0:
        print(f"Usuario '{username}' creado exitosamente.")
        try:
            passwd_process = subprocess.run(
                ["sudo", "chpasswd"],
                input=f"{username}:{password}".encode('utf-8'),
                capture_output=True,
                check=True
            )
            print(f"Contraseña establecida para '{username}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error al establecer la contraseña para '{username}':", file=sys.stderr)
            print(f"STDOUT: {e.stdout.strip()}", file=sys.stderr)
            print(f"STDERR: {e.stderr.strip()}", file=sys.stderr)
            _run_command(["sudo", "userdel", "-r", username], check_success=False)
            sys.exit(1)
        except Exception as e:
            print(f"Error inesperado al establecer la contraseña: {e}", file=sys.stderr)
            _run_command(["sudo", "userdel", "-r", username], check_success=False)
            sys.exit(1)

    elif result_useradd:
        print(f"Falló la creación del usuario '{username}'. Código de salida: {result_useradd.returncode}", file=sys.stderr)
        if result_useradd.stderr:
            print(f"Detalles del error: {result_useradd.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def delete_user(username):
    """Elimina un usuario del sistema Linux."""
    print(f"Intentando eliminar usuario: {username}")
    result = _run_command(["sudo", "userdel", "-r", username], check_success=False)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' eliminado exitosamente.")
    elif result:
        print(f"Falló la eliminación del usuario '{username}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def change_password(username, new_password):
    """Cambia la contraseña de un usuario existente."""
    print(f"Intentando cambiar contraseña para usuario: {username}")
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
        print(f"STDOUT: {e.stdout.strip()}", file=sys.stderr)
        print(f"STDERR: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al cambiar la contraseña: {e}", file=sys.stderr)
        sys.exit(1)

def list_local_users():
    """Lista los usuarios existentes en el sistema Linux."""
    print("Listando usuarios locales del sistema:")
    result = _run_command(["getent", "passwd"])
    if result:
        users = []
        for line in result.stdout.splitlines():
            parts = line.split(':')
            if len(parts) > 0:
                username = parts[0]
                uid = int(parts[2])
                shell = parts[6]
                # Filter out system users (UID < 1000) and users with nologin/false shells
                if uid >= 1000 and not shell.endswith("nologin") and not shell.endswith("false"):
                    users.append(username)
        
        if users:
            for user in users:
                print(f"- {user}")
        else:
            print("No se encontraron usuarios locales regulares del sistema.")
    else:
        print("No se pudieron listar los usuarios locales.")

# --- Nuevas Funciones de Gestión de Grupos (Linux) ---

def create_group(groupname):
    """Crea un nuevo grupo local en el sistema Linux."""
    print(f"Intentando crear grupo: {groupname}")
    result = _run_command(["sudo", "groupadd", groupname], check_success=False)
    if result and result.returncode == 0:
        print(f"Grupo '{groupname}' creado exitosamente.")
    elif result:
        print(f"Falló la creación del grupo '{groupname}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def delete_group(groupname):
    """Elimina un grupo local del sistema Linux."""
    print(f"Intentando eliminar grupo: {groupname}")
    result = _run_command(["sudo", "groupdel", groupname], check_success=False)
    if result and result.returncode == 0:
        print(f"Grupo '{groupname}' eliminado exitosamente.")
    elif result:
        print(f"Falló la eliminación del grupo '{groupname}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def add_user_to_group(username, groupname):
    """Añade un usuario a un grupo local en el sistema Linux."""
    print(f"Intentando añadir usuario '{username}' al grupo '{groupname}'")
    # -aG: append to supplementary groups
    result = _run_command(["sudo", "usermod", "-aG", groupname, username], check_success=False)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' añadido al grupo '{groupname}' exitosamente.")
    elif result:
        print(f"Falló al añadir usuario '{username}' al grupo '{groupname}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def remove_user_from_group(username, groupname):
    """Elimina un usuario de un grupo local en el sistema Linux."""
    print(f"Intentando eliminar usuario '{username}' del grupo '{groupname}'")
    # gpasswd -d: removes a user from a group
    result = _run_command(["sudo", "gpasswd", "-d", username, groupname], check_success=False)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' eliminado del grupo '{groupname}' exitosamente.")
    elif result:
        print(f"Falló al eliminar usuario '{username}' del grupo '{groupname}'. Código de salida: {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"Detalles del error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def list_local_groups():
    """Lista los grupos locales existentes en el sistema Linux."""
    print("Listando grupos locales del sistema:")
    result = _run_command(["getent", "group"])
    if result:
        groups = []
        for line in result.stdout.splitlines():
            parts = line.split(':')
            if len(parts) > 0:
                groupname = parts[0]
                gid = int(parts[2])
                # Filter out system groups (GID < 1000 typically)
                if gid >= 1000: # Heuristic for non-system groups
                    groups.append(groupname)
        
        if groups:
            for group in groups:
                print(f"- {group}")
        else:
            print("No se encontraron grupos locales regulares del sistema.")
    else:
        print("No se pudieron listar los grupos locales.")

def manage_linux_users_and_groups():
    """Menú principal para la gestión de usuarios y grupos Linux."""
    while True:
        print("\n--- Gestión de Usuarios y Grupos (Linux) ---")
        print("1. Crear Usuario")
        print("2. Eliminar Usuario")
        print("3. Modificar Contraseña de Usuario")
        print("4. Crear Grupo Local")
        print("5. Eliminar Grupo Local")
        print("6. Añadir Usuario a Grupo Local")
        print("7. Eliminar Usuario de Grupo Local")
        print("8. Listar Usuarios Locales")
        print("9. Listar Grupos Locales")
        print("0. Volver al Menú Principal") # Changed from '7' to '0' for consistency

        choice = input("Seleccione una opción: ")

        if choice == '1':
            username = input("Ingrese el nombre de usuario a añadir: ")
            password = input("Ingrese la contraseña para el usuario: ")
            add_user(username, password)
        elif choice == '2':
            username = input("Ingrese el nombre de usuario a eliminar: ")
            delete_user(username)
        elif choice == '3':
            username = input("Ingrese el nombre de usuario cuya contraseña desea modificar: ")
            new_password = input("Ingrese la nueva contraseña: ")
            change_password(username, new_password)
        elif choice == '4':
            groupname = input("Ingrese el nombre del grupo a crear: ")
            create_group(groupname)
        elif choice == '5':
            groupname = input("Ingrese el nombre del grupo a eliminar: ")
            delete_group(groupname)
        elif choice == '6':
            username = input("Ingrese el nombre de usuario a añadir al grupo: ")
            groupname = input("Ingrese el nombre del grupo: ")
            add_user_to_group(username, groupname)
        elif choice == '7':
            username = input("Ingrese el nombre de usuario a eliminar del grupo: ")
            groupname = input("Ingrese el nombre del grupo: ")
            remove_user_from_group(username, groupname)
        elif choice == '8':
            list_local_users()
        elif choice == '9':
            list_local_groups()
        elif choice == '0': # Changed from '7' to '0'
            break
        else:
            print("Opción no válida. Intente de nuevo.")