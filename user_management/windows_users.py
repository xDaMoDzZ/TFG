# user_management/windows_users.py

from utils import common

def display_user_menu():
    """Muestra el submenú de gestión de usuarios en Windows."""
    common.clear_screen()
    print("--- Gestión de Usuarios y Grupos (Windows) ---")
    print("1. Crear Usuario")
    print("2. Eliminar Usuario")
    print("3. Modificar Contraseña de Usuario")
    print("4. Crear Grupo Local")
    print("5. Eliminar Grupo Local")
    print("6. Añadir Usuario a Grupo Local")
    print("7. Eliminar Usuario de Grupo Local")
    print("8. Listar Usuarios Locales")
    print("9. Listar Grupos Locales")
    print("0. Volver al Menú Principal")

def create_user():
    username = input("Introduce el nombre de usuario a crear: ")
    password = input("Introduce la contraseña para el usuario: ")
    # La opción '/ADD' crea el usuario. '/PASSWORDREQ:NO' permite no pedir contraseña al login.
    command = ["net", "user", username, password, "/ADD"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' creado correctamente.")
    else:
        print(f"Error al crear el usuario '{username}'.")

def delete_user():
    username = input("Introduce el nombre de usuario a eliminar: ")
    confirm = input(f"¿Estás seguro de que quieres eliminar a '{username}'? (s/n): ").lower()
    if confirm == 's':
        command = ["net", "user", username, "/DELETE"]
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
        command = ["net", "user", username, new_password]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Contraseña para '{username}' cambiada exitosamente.")
        else:
            print(f"Error al cambiar la contraseña para '{username}'.")
    else:
        print("Las contraseñas no coinciden.")

def create_local_group():
    groupname = input("Introduce el nombre del grupo local a crear: ")
    command = ["net", "localgroup", groupname, "/ADD"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Grupo local '{groupname}' creado correctamente.")
    else:
        print(f"Error al crear el grupo local '{groupname}'.")

def delete_local_group():
    groupname = input("Introduce el nombre del grupo local a eliminar: ")
    confirm = input(f"¿Estás seguro de que quieres eliminar el grupo local '{groupname}'? (s/n): ").lower()
    if confirm == 's':
        command = ["net", "localgroup", groupname, "/DELETE"]
        result = common.run_command(command)
        if result and result.returncode == 0:
            print(f"Grupo local '{groupname}' eliminado correctamente.")
        else:
            print(f"Error al eliminar el grupo local '{groupname}'.")
    else:
        print("Operación cancelada.")

def add_user_to_local_group():
    username = input("Introduce el nombre de usuario: ")
    groupname = input("Introduce el nombre del grupo local: ")
    command = ["net", "localgroup", groupname, username, "/ADD"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' añadido al grupo local '{groupname}'.")
    else:
        print(f"Error al añadir el usuario '{username}' al grupo local '{groupname}'.")

def remove_user_from_local_group():
    username = input("Introduce el nombre de usuario: ")
    groupname = input("Introduce el nombre del grupo local: ")
    command = ["net", "localgroup", groupname, username, "/DELETE"]
    result = common.run_command(command)
    if result and result.returncode == 0:
        print(f"Usuario '{username}' eliminado del grupo local '{groupname}'.")
    else:
        print(f"Error al eliminar el usuario '{username}' del grupo local '{groupname}'.")

def list_local_users():
    print("\n--- Listado de Usuarios Locales (Windows) ---")
    command = ["net", "user"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        # La salida de 'net user' es un poco sucia, necesitarás parsearla si quieres solo nombres
        print(result.stdout)
    else:
        print("No se pudieron listar los usuarios locales.")
    common.press_enter_to_continue()

def list_local_groups():
    print("\n--- Listado de Grupos Locales (Windows) ---")
    command = ["net", "localgroup"]
    result = common.run_command(command, capture_output=True)
    if result and result.returncode == 0:
        # La salida de 'net localgroup' también necesita parseo si solo quieres los nombres
        print(result.stdout)
    else:
        print("No se pudieron listar los grupos locales.")
    common.press_enter_to_continue()

def user_management_menu():
    """Menú principal para la gestión de usuarios y grupos en Windows."""
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
            create_local_group()
        elif choice == '5':
            delete_local_group()
        elif choice == '6':
            add_user_to_local_group()
        elif choice == '7':
            remove_user_from_local_group()
        elif choice == '8':
            list_local_users()
        elif choice == '9':
            list_local_groups()
        elif choice == '0':
            print("Volviendo al menú principal...")
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")
        common.press_enter_to_continue()