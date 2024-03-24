import flet as ft
from auth import Auth

class UI:
    """
    Класс для работы со всем UI
    """
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


class MainPage:
    """
    Класс для отображения главной страницы
    """
    def __init__(self, ui: UI):
        self.ui = ui
        self.page = ui.page
        self.page.title = "Деканат-Студенты"
        self.title = ft.Text("Деканат-Студенты", size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    def build(self):
        if Auth.getUser() is not None:
            return ft.Column(
                [self.title], 
                alignment=ft.MainAxisAlignment.CENTER, 
                height=self.page.window_height-self.page.navigation_bar.height,
                width=self.page.window_width,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            return ft.Column(
                [ft.Text("Для просмотра информации необходимо войти в аккаунт", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)], 
                alignment=ft.MainAxisAlignment.CENTER, 
                height=self.page.window_height-self.page.navigation_bar.height,
                width=self.page.window_width,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

    

class AuthPage:
    """
    Класс для страницы входа в аккаунт и регистрации.
    """
    class InfoCard:
        """
        Класс для отображения информационной карточки.
        """
        def __init__(self, objs, page: ft.Page):
            self.objs = objs
            self.page = page
        
        def build(self):
            card = ft.Column(
                [ft.ResponsiveRow(
                    [ft.Card(
                        ft.Container(   
                            ft.Column(
                                controls=self.objs,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
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
            return card

            
    def __init__(self, ui: UI):
        self.ui = ui
        self.page = ui.page
        self.clickedRegister = False

        def click_enterButton(e):
            try:
                Auth.login(self.emailField.value, self.passwordField.value)
            except ValueError as err:
                Dialog(self.page, "Ошибка входа", str(err), backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return
            self.ui.changePage(0)
            
        def click_registerButton(e):
            if not self.clickedRegister:
                self.clickedRegister = True
                self.page.controls = [self.build(register=True)]
                self.page.update()
            else:
                try:
                    Auth.register(self.emailField.value, self.passwordField.value, self.passwordFieldConfirm.value)
                except ValueError as err:
                    Dialog(self.page, "Ошибка регистрации", str(err), backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                    return
                
                Auth.login(self.emailField.value, self.passwordField.value)
                self.ui.changePage(0)

        def backToEnter(e):
            self.clickedRegister = False
            self.passwordFieldConfirm.value = ""
            self.page.controls = [self.build(register=False)]
            self.page.update()
            
        def click_signOutButton(e):
            Auth.signOut()
            # Очистка полей ввода
            self.emailField.value = ""
            self.passwordField.value = ""
            self.passwordFieldConfirm.value = ""
            self.currentEmail.value = ""
            self.clickedRegister = False
            # Обновляем страницу
            self.ui.changePage(1)

        self.emailField = ft.TextField(label="Email", multiline=False, hint_text="example@example.com")
        self.passwordField = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
        self.passwordFieldConfirm = ft.TextField(label="Подтверждение пароля", password=True, can_reveal_password=True)
        self.enterButton = ft.ElevatedButton(text="Вход", on_click=click_enterButton)
        self.registerButton = ft.ElevatedButton(text="Регистрация", on_click=click_registerButton)
        self.backButton = ft.ElevatedButton(text="Назад", on_click=backToEnter)

        self.currentEmail = ft.Text("", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.signOutButton = ft.ElevatedButton(text="Выход", on_click=click_signOutButton)

    def build(self, register=False):
        if Auth.getUser() is not None:
            self.currentEmail.value = f"Вы вошли как: {Auth.getUser()['email']}"
            return self.InfoCard([self.currentEmail, self.signOutButton], page=self.page).build()
        else:
            if register or self.clickedRegister:
                return self.InfoCard([self.emailField, self.passwordField, self.passwordFieldConfirm, ft.Row([self.backButton, self.registerButton])], page=self.page).build()
            else:
                return self.InfoCard([self.emailField, self.passwordField, ft.Row([self.enterButton, self.registerButton])], page=self.page).build()
            
class Dialog:
    """
    Класс для отображения диалоговых окон
    """
    def __init__(self,page: ft.Page, title: str, content: str, backAction: ft.ElevatedButton, actions: list[ft.ElevatedButton] = []):
        self.page = page
        self.title = title
        self.content = content
        self.backAction = backAction
        self.actions = actions

    def closeDialog(self, e):
        self.page.dialog.open = False
        self.page.update()
    
    def build(self):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title),
            content=ft.Text(self.content),
            actions=[self.backAction, *self.actions]
        )
        dialog.actions[0].on_click = self.closeDialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()