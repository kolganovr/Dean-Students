import flet as ft
from auth import Auth

class UI:
    def __init__(self):
        ft.app(target=self.main)

    def changePage(self, pageNum: int):
        self.page.navigation_bar.selected_index = pageNum
        if pageNum == 0:
            self.page.controls = [self.mainPage.build()]
            self.page.update()
        elif pageNum == 1:
            self.page.controls = [self.authPage.build()]
            self.page.update()

    def main(self, page: ft.Page):
        self.page = page
        self.authPage = AuthPage(self)
        self.mainPage = MainPage(self)
        page.window_height = 900
        page.window_width = 1600

        self.navBar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(
                    label="Главная", icon=ft.icons.HOME_OUTLINED, selected_icon=ft.icons.HOME
                ),
                ft.NavigationDestination(
                    label="Вход", icon=ft.icons.LOGIN_OUTLINED, selected_icon=ft.icons.LOGIN
                )
            ],
            on_change=lambda e: self.changePage(e.control.selected_index),
            selected_index=1,
            height=80
        )
        page.navigation_bar = self.navBar
        page.controls = [self.authPage.build()]
        page.update()


class MainPage():
    def __init__(self, ui: UI):
        self.ui = ui
        self.page = ui.page
        self.page.title = "Деканат-Студенты"
        self.title = ft.Text("Деканат-Студенты", size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    def build(self):
        return ft.Column(
            [self.title], 
            alignment=ft.MainAxisAlignment.CENTER, 
            height=self.page.window_height-self.page.navigation_bar.height,
            width=self.page.window_width,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    

class AuthPage():
    def __init__(self, ui: UI):
        self.ui = ui
        self.page = ui.page
        self.emailField = ft.TextField(label="Email", multiline=False, hint_text="example@example.com")
        self.passwordField = ft.TextField(label="Пароль", password=True, can_reveal_password=True)

        def on_click(e):
            user = Auth.login(self.emailField.value, self.passwordField.value)
            print(user)
            if user is not None:
                # Переходим на главную страницу
                self.ui.changePage(0)
            else:
                print("Пользователь не найден")

        self.bt1 = ft.ElevatedButton(text="Вход", on_click=on_click)

    def build(self):
        all = ft.Column(
            [ft.ResponsiveRow(
                [ft.Card(
                    ft.Container(   
                        ft.Column(
                            [ft.ResponsiveRow(
                                [self.emailField]
                            ),
                            ft.ResponsiveRow(
                                [self.passwordField]
                            ),
                            ft.ResponsiveRow(
                                [self.bt1]
                            )]
                        ),
                        padding=20,
                    ),
                    col={"sm": 12, "md": 8, "xl": 5},
                )],
                alignment=ft.MainAxisAlignment.CENTER
            )],
            height=self.page.window_height-self.page.navigation_bar.height,
            width=self.page.window_width,
            alignment=ft.MainAxisAlignment.CENTER
        )
        return all