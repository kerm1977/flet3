import flet as ft
import sqlite3
import hashlib
import os

DATABASE_FILE = "users.db"

def create_tables():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expiry_timestamp REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)

def insert_user(username, email, phone, password):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                       (username, email, phone, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Registro exitoso"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El nombre de usuario o el correo electrónico ya existen."

def fetch_user(username):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# --- Funciones para la sesión (simulado para la versión 0.27.2) ---
# En una aplicación real, se usaría un manejo de sesiones más robusto.
current_user_id = None
logged_in_username = None
remember_me = False

def set_session(user_id, username, remember=False):
    global current_user_id, logged_in_username, remember_me
    current_user_id = user_id
    logged_in_username = username
    remember_me = remember

def clear_session():
    global current_user_id, logged_in_username, remember_me
    current_user_id = None
    logged_in_username = None
    remember_me = False

def is_logged_in():
    return current_user_id is not None

class MainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Flet App"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.logged_in = is_logged_in()
        self.logged_in_username = logged_in_username
        self.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
                ft.NavigationBarDestination(icon=ft.Icons.EVENT, label="Eventos"),
                ft.NavigationBarDestination(icon=ft.Icons.CONTACTS, label="Contactos"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Mi cuenta"),
            ],
            on_change=self.navigation_change,
            visible=True,
        )
        self.home_view = self.build_home_view()
        self.login_form = self.build_login_form()
        self.registration_form = self.build_registration_form()
        self.current_view = ft.Container(expand=True)
        self.user_icon_button = ft.IconButton(ft.Icons.PERSON, on_click=lambda _: self.page.go("/login"))
        self.logout_button = ft.ElevatedButton("Salir", on_click=self.logout)
        self.update_navigation_bar()
        self.update_view()
        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [ft.Text(self.page.title, weight=ft.FontWeight.BOLD)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.current_view,
                ],
                expand=True,
            ),
            self.navigation_bar,
        )
        self.page.on_route_change = self.route_change
        self.page.go(self.page.route)

    def build_login_form(self):
        self.username_field = ft.TextField(label="Usuario")
        self.password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
        self.remember_me_checkbox = ft.Checkbox(label="Recordarme")
        self.login_button = ft.ElevatedButton("Iniciar Sesión", on_click=self.login)
        self.register_link = ft.TextButton("¿No tienes cuenta? Regístrate aquí", on_click=lambda _: self.page.go("/register"))
        self.error_message = ft.Text("", color=ft.colors.RED)
        self.success_message = ft.Text("", color=ft.colors.GREEN)
        return ft.Column(
            [
                self.username_field,
                self.password_field,
                self.remember_me_checkbox,
                self.login_button,
                self.register_link,
                self.error_message,
                self.success_message,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        user_data = fetch_user(username)

        if user_data and verify_password(user_data[2], password): # user_data[2] is the password hash
            set_session(user_data[0], user_data[1], self.remember_me_checkbox.value) # user_data[1] is the username
            self.success_message.value = "Inicio de sesión exitoso."
            self.error_message.value = ""
            self.logged_in = True
            self.logged_in_username = user_data[1]
            self.update_navigation_bar()
            self.page.go("/home")
        else:
            self.error_message.value = "Credenciales incorrectas."
            self.success_message.value = ""
        self.page.update()

    def build_registration_form(self):
        self.username_field = ft.TextField(label="Usuario")
        self.email_field = ft.TextField(label="Correo Electrónico", keyboard_type=ft.KeyboardType.EMAIL)
        self.phone_field = ft.TextField(label="Teléfono", keyboard_type=ft.KeyboardType.PHONE)
        self.password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
        self.confirm_password_field = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True)
        self.register_button = ft.ElevatedButton("Registrarse", on_click=self.register)
        self.login_link = ft.TextButton("¿Ya tienes cuenta? Inicia sesión aquí", on_click=lambda _: self.page.go("/login"))
        self.error_message = ft.Text("", color=ft.colors.RED)
        self.success_message = ft.Text("", color=ft.colors.GREEN)
        return ft.Column(
            [
                self.username_field,
                self.email_field,
                self.phone_field,
                self.password_field,
                self.confirm_password_field,
                self.register_button,
                self.login_link,
                self.error_message,
                self.success_message,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def register(self, e):
        username = self.username_field.value
        email = self.email_field.value
        phone = self.phone_field.value
        password = self.password_field.value
        confirm_password = self.confirm_password_field.value

        if password != confirm_password:
            self.error_message.value = "Las contraseñas no coinciden."
            self.success_message.value = ""
        else:
            success, message = insert_user(username, email, phone, password)
            if success:
                self.success_message.value = message
                self.error_message.value = ""
                self.page.go("/login")
            else:
                self.error_message.value = message
                self.success_message.value = ""
        self.page.update()

    def build_home_view(self):
        return ft.Column(
            [
                ft.Text("Bienvenido al Home!", size=30),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

    def update_navigation_bar(self):
        if self.logged_in and self.logged_in_username:
            self.page.appbar = ft.AppBar(
                title=ft.Text(self.page.title),
                actions=[
                    ft.Text(f"({self.logged_in_username})"),
                    self.logout_button,
                ],
            )
        else:
            self.page.appbar = ft.AppBar(
                title=ft.Text(self.page.title),
                actions=[self.user_icon_button],
            )
        self.page.update()

    def update_view(self):
        if self.page.route == "/home":
            self.current_view.content = self.home_view
        elif self.page.route == "/login":
            self.current_view.content = self.login_form
        elif self.page.route == "/register":
            self.current_view.content = self.registration_form
        else:
            self.current_view.content = ft.Text("Página no encontrada")
        self.page.update()

    def route_change(self, route):
        self.logged_in = is_logged_in()
        self.logged_in_username = logged_in_username
        self.update_navigation_bar()
        self.update_view()

    def navigation_change(self, e):
        if e.control.selected_index == 0:
            self.page.go("/home")
        elif e.control.selected_index == 1:
            # Aquí iría la lógica para la vista de "Eventos"
            pass
        elif e.control.selected_index == 2:
            # Aquí iría la lógica para la vista de "Contactos"
            pass
        elif e.control.selected_index == 3:
            # Aquí iría la lógica para la vista de "Mi cuenta"
            pass

    def logout(self, e):
        clear_session()
        self.logged_in = False
        self.logged_in_username = None
        self.update_navigation_bar()
        self.page.go("/home")

def main(page: ft.Page):
    create_tables()
    MainApp(page)

if __name__ == "__main__":
    ft.app(target=main)