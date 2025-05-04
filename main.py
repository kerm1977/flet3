import flet as ft
from database import create_tables
from views import Views
from session import is_logged_in, get_logged_in_username, clear_session # Importa clear_session
import hashlib # Importa hashlib

class MainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Flet App"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.logged_in = is_logged_in()
        self.logged_in_username = get_logged_in_username()
        self.views = Views(page) # Instancia de la clase Views
        self.navigation_bar = ft.NavigationBar(
            bgcolor=ft.Colors.AMBER,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
                ft.NavigationBarDestination(icon=ft.Icons.EVENT, label="Eventos"),
                ft.NavigationBarDestination(icon=ft.Icons.CONTACTS, label="Contactos"),
                ft.NavigationBarDestination(
                    icon=ft.Icons.PERSON,
                    label="Mi cuenta",
                    disabled=not self.logged_in,
                ),
            ],
            on_change=self.navigation_change,
            visible=True,
        )
        self.current_view = ft.Container(expand=True)
        self.user_icon_button = ft.IconButton(ft.Icons.PERSON, on_click=lambda _: self.page.go("/login"))
        self.logout_button = ft.IconButton(ft.Icons.EXIT_TO_APP, on_click=self.logout)
        self.update_appbar()
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

    def update_view(self):
        if self.page.route == "/home":
            self.current_view.content = self.views.home_view
        elif self.page.route == "/login":
            self.current_view.content = self.views.login_form
        elif self.page.route == "/register":
            self.current_view.content = self.views.registration_form
        elif self.page.route == "/mi_cuenta":
            if self.logged_in:
                self.current_view.content = ft.Text("Vista de Mi Cuenta (Contenido privado)")
            else:
                self.page.go("/login")
        elif self.page.route == "/events":
            self.current_view.content = self.views.events_view
        else:
            self.current_view.content = ft.Text("Página no encontrada")
        self.page.update()

    def route_change(self, route):
        self.logged_in = is_logged_in()
        self.update_appbar()
        self.update_view()

    def navigation_change(self, e):
        if e.control.selected_index == 0:
            self.page.go("/home")
        elif e.control.selected_index == 1:
            self.page.go("/events")
        elif e.control.selected_index == 2:
            pass
        elif e.control.selected_index == 3:
            self.page.go("/mi_cuenta")

    def logout(self, e):
        clear_session()
        self.logged_in = False
        self.logged_in_username = None
        self.navigation_bar.destinations[3].disabled = True
        self.update_appbar()
        self.page.go("/home")

    def update_appbar(self):
        if self.logged_in:
            self.page.appbar = ft.AppBar(
                title=ft.Text(self.page.title),
                actions=[self.logout_button],
            )
        else:
            self.page.appbar = ft.AppBar(
                title=ft.Text(self.page.title),
                actions=[self.user_icon_button],
            )
        self.page.update()

def main(page: ft.Page):
    create_tables()
    MainApp(page)

if __name__ == "__main__":
    ft.app(target=main)

