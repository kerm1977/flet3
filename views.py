import flet as ft
from database import insert_user, fetch_user
from session import set_session, clear_session, is_logged_in, get_logged_in_username
import hashlib # Importa el módulo hashlib


class Views:
    def __init__(self, page: ft.Page):
        self.page = page
        self.logged_in_username = get_logged_in_username()
        self.build_login_form()
        self.build_registration_form()
        self.build_home_view()
        self.build_events_view()

    def build_login_form(self):
        self.username_field = ft.TextField(label="Usuario")
        self.password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
        self.remember_me_checkbox = ft.Checkbox(label="Recordarme")
        self.login_button = ft.ElevatedButton("Iniciar Sesión", on_click=self.login)
        self.register_link = ft.TextButton("¿No tienes cuenta? Regístrate aquí", on_click=lambda _: self.page.go("/register"))
        self.error_message = ft.Text("", color=ft.colors.RED)
        self.success_message = ft.Text("", color=ft.colors.GREEN)
        self.login_form = ft.Column(
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
        self.registration_form = ft.Column(
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

    def build_home_view(self):
        self.home_view = ft.Column(
            [
                ft.Text("Bienvenido al Home!", size=30),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

    def build_events_view(self):
        self.events_view = ft.Column(
            [
                ft.Text("Aquí irán los eventos y la calculadora.", size=20),
                ft.IconButton(
                    ft.Icons.CALCULATE_OUTLINED,
                    tooltip="Abrir calculadora",
                    on_click=self.open_calculator,
                    icon_size=40,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        user_data = fetch_user(username)

        if user_data and self.verify_password(user_data[2], password):
            set_session(user_data[0], user_data[1], self.remember_me_checkbox.value)
            self.success_message.value = "Inicio de sesión exitoso."
            self.error_message.value = ""
            self.logged_in = True
            self.logged_in_username = user_data[1]
            self.page.go("/home")
            self.page.update()
        else:
            self.error_message.value = "Credenciales incorrectas."
            self.success_message.value = ""
            self.page.update()

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

    def open_calculator(self, e):
        print("¡El icono de la calculadora fue presionado!")
        # Aquí integraremos la lógica para mostrar tu calculadora

    def verify_password(self, stored_hash, password):
        """Verifica si la contraseña coincide con el hash almacenado."""
        return stored_hash == self.hash_password(password)

    def hash_password(self, password):
        """Hashea la contraseña utilizando SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()


