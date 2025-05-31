# user_management/linux_users.py

from utils import common

def display_user_menu():
    """Muestra el submenú de gestión de usuarios en Linux."""
    common.clear_screen()
    print("--- Gestión de Usuarios y Grupos (Linux) ---")
    print("1. Crear Usuario")
    print("2. Eliminar Usuario")
    print("3. Modificar Contraseña de Usuario")
    print("4. Crear Grupo")
    print("5. Eliminar Grupo")
    print("6. Añadir Usuario a Grupo")
    print("7. Eliminar Usuario de Grupo")
    print("8. Listar Usuarios")
    print("9. Listar Grupos")
    print("0. Volver al Menú Principal")

def create_user():
    username = input("Introduce el nombre de usuario a crear: ")
    password = input("Introduce la contraseña para el usuario: ")
    # Podrías pedir más detalles como el directorio home, shell, etc.
    command = ["sudo", "useradd", "-m", username]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' creado. Estableciendo contraseña...")
        # Usa 'chpasswd' para establecer la contraseña de forma segura
        passwd_command = ['sudo', 'chpasswd']
        process = common.run_command(passwd_command, input=f"{username}:{password}\n".encode(), check=False, capture_output=True)
        if process and process.returncode == 0:
            print(f"Contraseña para '{username}' establecida.")
        else:
            print(f"Error al establecer la contraseña para '{username}'.")
            if process: print(process.stderr)
    else:
        print(f"Error al crear el usuario '{username}'.")

def delete_user():
    username = input("Introduce el nombre de usuario a eliminar: ")
    confirm = input(f"¿Estás seguro de que quieres eliminar a '{username}'? (s/n): ").lower()
    if confirm == 's':
        command = ["sudo", "userdel", "-r", username] # -r para eliminar el directorio home
        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Usuario '{username}' eliminado correctamente.")
        else:
            print(f"Error al eliminar el usuario '{username}'.")
    else:
        print("Operación cancelada.")

def change_user_password():
    username = input("Introduce el nombre de usuario para cambiar la contraseña: ")
    new_password = input("Introduce la nueva contraseña: ")
    confirm_password = input("Confirma la nueva contraseña: ")
    if new_password == confirm_password:
        passwd_command = ['sudo', 'chpasswd']
        process = common.run_command(passwd_command, input=f"{username}:{new_password}\n".encode(), check=False, capture_output=True)
        if process and process.returncode == 0:
            print(f"Contraseña para '{username}' cambiada exitosamente.")
        else:
            print(f"Error al cambiar la contraseña para '{username}'.")
            if process: print(process.stderr)
    else:
        print("Las contraseñas no coinciden.")

def create_group():
    groupname = input("Introduce el nombre del grupo a crear: ")
    command = ["sudo", "groupadd", groupname]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Grupo '{groupname}' creado correctamente.")
    else:
        print(f"Error al crear el grupo '{groupname}'.")

def delete_group():
    groupname = input("Introduce el nombre del grupo a eliminar: ")
    confirm = input(f"¿Estás seguro de que quieres eliminar el grupo '{groupname}'? (s/n): ").lower()
    if confirm == 's':
        command = ["sudo", "groupdel", groupname]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Grupo '{groupname}' eliminado correctamente.")
        else:
            print(f"Error al eliminar el grupo '{groupname}'.")
    else:
        print("Operación cancelada.")

def add_user_to_group():
    username = input("Introduce el nombre de usuario: ")
    groupname = input("Introduce el nombre del grupo: ")
    command = ["sudo", "usermod", "-aG", groupname, username] # -aG para añadir a grupos suplementarios sin eliminar los existentes
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' añadido al grupo '{groupname}'.")
    else:
        print(f"Error al añadir el usuario '{username}' al grupo '{groupname}'.")

def remove_user_from_group():
    username = input("Introduce el nombre de usuario: ")
    groupname = input("Introduce el nombre del grupo: ")
    # Para eliminar un usuario de un grupo en Linux, necesitamos modificar el grupo o usar gpasswd
    # Una forma simple es usar 'gpasswd -d'
    command = ["sudo", "gpasswd", "-d", username, groupname]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' eliminado del grupo '{groupname}'.")
    else:
        print(f"Error al eliminar el usuario '{username}' del grupo '{groupname}'.")

def list_users():
    print("\n--- Listado de Usuarios (Linux) ---")
    # 'cut -d: -f1 /etc/passwd' muestra solo el nombre de usuario
    command = ["cut", "-d:", "-f1", "/etc/passwd"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudieron listar los usuarios.")
    common.press_enter_to_continue()

def list_groups():
    print("\n--- Listado de Grupos (Linux) ---")
    # 'cut -d: -f1 /etc/group' muestra solo el nombre del grupo
    command = ["cut", "-d:", "-f1", "/etc/group"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        print(result.stdout)
    else:
        print("No se pudieron listar los grupos.")
    common.press_enter_to_continue()

def user_management_menu():
    """Menú principal para la gestión de usuarios y grupos en Linux."""
    while True:
        common.clear_screen()
        display_user_menu()
        choice = input("Su elección: ")

        if choice == '1':
            create_user()
        elif choice == '2':
            delete_user()
        elif choice == '3':
            change_user_password()
        elif choice == '4':
            create_group()
        elif choice == '5':
            delete_group()
        elif choice == '6':
            add_user_to_group()
        elif choice == '7':
            remove_user_from_group()
        elif choice == '8':
            list_users()
        elif choice == '9':
            list_groups()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()