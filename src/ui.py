import flet as ft
from auth import Auth
from db import DB
from student import Student
from datetime import datetime

class UI:
    """
    Класс для работы со всем UI
    """
    def __init__(self):
        ft.app(target=self.main)

    def changePage(self, pageNum: int):
        self.page.navigation_bar.selected_index = pageNum
        if pageNum == 0:
            self.page.controls = [self.searchPage.build()]
            self.page.update()
        elif pageNum == 2:
            self.page.controls = [self.authPage.build()]
            self.page.update()

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Деканат-студенты"
        self.authPage = AuthPage(self)
        self.searchPage = SearchPage(self)
        page.window_height = 900
        page.window_width = 1600

        self.navBar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(
                    label="Поиск", icon=ft.icons.SEARCH_OUTLINED, selected_icon=ft.icons.SEARCH
                ),
                ft.NavigationDestination(
                    label="Изменение", icon=ft.icons.EDIT_OUTLINED, selected_icon=ft.icons.EDIT
                ),
                ft.NavigationDestination(
                    label="Вход", icon=ft.icons.LOGIN_OUTLINED, selected_icon=ft.icons.LOGIN
                )
            ],
            on_change=lambda e: self.changePage(e.control.selected_index),
            selected_index=2,
            height=80
        )
        page.navigation_bar = self.navBar
        page.controls = [self.authPage.build()]
        page.update()

    def deleteDropdown(self, value: str):
        find = False
        if len(self.searchPage.searchDrops) > 0:
            for i in range(len(self.searchPage.searchDrops)):
                block = self.searchPage.searchDrops[i]
                if block.controls[0].value == value:
                    self.searchPage.searchDrops.pop(i)
                    find = True
                    break
            if find:
                self.changePage(0)
        if not find:
            Dialog(self.page, "Ошибка удаления", "Не удалось удалить блок", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()

class SearchPage:
    """
    Класс для отображения страницы поиска
    """

    def getKeysStudentAndUI(searchCategories: list):
        """
        Метод для получения соответствия ключей для студента и ключей для UI

        Возвращает:
            tuple: (dict, dict) - (UiToStudent, StudentToUi)
        """
        studentKeys = Student.getKeys()
        keysUiToStudent = {searchCategories[i]: key for i, key in enumerate(studentKeys)}
        keysStudentToUi = {key: searchCategories[i] for i, key in enumerate(studentKeys)}

        return keysUiToStudent, keysStudentToUi
    
    # ['surname', 'name', 'patronymic', 'age', 'homeCity', 'address', 'phoneNumber', 'group', 'course', 'pass_num', 'available_rooms', 'ID', 'gradebookID']
    searchCategories = ["Фамилия", "Имя", "Отчество", "Возраст", "Город", "Адрес", "Телефон", "Группа", "Курс", "Номер пропуска", "Доступные аудитории", "Номер студенческого", "Номер зачетки"]  
    keysUiToStudent, keysStudentToUi = getKeysStudentAndUI(searchCategories)      
    class SearchResults:
        """
        Класс для отображения результатов поиска
        """
        class SearchResultsCard:
            """
            Класс для отображения карточки с результатами поиска
            """
            def __init__(self, res: dict, criteria: dict):
                self.res = res
                self.criteria = criteria
                self.isSelected = False
            
            def change(self, e):
                self.isSelected = not self.isSelected
            
            def build(self):
                #           Кол-во записей в поиске
                # Чекбокс
                #           Критерии поиска

                self.checkBox = ft.Checkbox(value=self.isSelected, on_change=self.change)
                self.count = ft.Text(str(len(self.res)), size=20)
                
                # Переименовываем ключи студента в ключи ui {'age':...} -> {'Возраст':...} используя SearchPage.keysStudentToUi
                self.criteria = {SearchPage.keysStudentToUi[key]: value for key, value in self.criteria.items()}

                fineTextCriteria = ""
                for key in self.criteria:
                    fineTextCriteria += f'{key}: {self.criteria[key]}, '
                fineTextCriteria = fineTextCriteria.strip()[:-1]
                fineTextCriteria = ft.Text(fineTextCriteria, size=20)

                column = ft.Column(
                    [
                        self.count, fineTextCriteria
                    ]
                )

                return ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [self.checkBox, column],
                            alignment=ft.MainAxisAlignment.START
                        ),
                        padding=20
                    )
                )
            
        def __init__(self, page: ft.Page):
            self.page = page
            self.results = [] # Список списков словарей студентов - результатов поиска
            self.criterias = [] # Список списков словарей критериев поиска
            self.resulutsCards = []
        
        def fillCards(self):
            #self.reslutsCards.append([self.SearchResultsCard(self.results[i]).build() for i in range(len(self.results))])
            self.resulutsCards = []
            for i in range(len(self.results)):
                self.resulutsCards.append(self.SearchResultsCard(self.results[i], self.criterias[i]))
        
        def exportToCSV(self):
            # Перебираем карточки резульатов поиска и если у них стоит чекбокс, то экспортируем их в один CSV файл
            selectedResults = []
            for i in range(len(self.resulutsCards)):
                if self.resulutsCards[i].isSelected:
                    for j in range(len(self.results[i])):
                        selectedResults.append(self.results[i][j])

            selectedResults = list(set(selectedResults))

            if len(selectedResults) == 0:
                Dialog(self.page, "Ошибка экспорта", "Ничего не выбрано", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return

            # Пишем в CSV
            time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(f"export_{time}.csv", 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = Student.getKeys()
                csvfile.write(f"{';'.join(fieldnames)}\n")

                for i in range(len(fieldnames)):
                    fieldnames[i] = Student.getPathToField(fieldnames[i])

                for student in selectedResults:
                    row = []
                    for field in fieldnames:
                        val = str(student.getFieldByPath(field)).replace(';', ",")
                        row.append(val)
                    csvfile.write(f"{';'.join(row)}\n")
            

            Dialog(self.page, "Успешно", "Экспорт завершен", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            
        def build(self):
            self.fillCards()
            div = ft.VerticalDivider() # TODO: Может быть сделать возможность двигать слайдер
            scrollCol = ft.Column(
                controls=[self.resulutsCards[i].build() for i in range(len(self.resulutsCards))],
                scroll=ft.ScrollMode.ALWAYS,
            )
            showButton = ft.ElevatedButton(
                "Показать",
            )
            exportButton = ft.ElevatedButton(
                "Экспорт в CSV",
                on_click=lambda e: self.exportToCSV(),
            )
            buttonRow = ft.Row(
                [showButton, exportButton], alignment=ft.MainAxisAlignment.SPACE_EVENLY
            )
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [scrollCol, buttonRow]
                    ),
                    padding=20
                ),
                col={'xs': 12, 'sm': 12, 'md': 7, 'xl': 7}
            )
            
            return card
        
    def __init__(self, ui: UI):
        self.ui = ui
        self.page = ui.page
        self.title = ft.Text("Поиск", size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.searchRes = self.SearchResults(self.page)
        self.searchDrops = [SearchDropdown(self.ui, 0, self.searchCategories).build()]


    def addDropdown(self):
        self.searchDrops.append(SearchDropdown(self.ui, len(self.searchDrops), self.searchCategories).build())
        self.ui.changePage(0)

    def find(self):
        if len(self.searchDrops) == 0:
            Dialog(self.page, "Ошибка поиска", "Для начала добавьте блоки", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
    
        crireria = {}
        for i in range(len(self.searchDrops)):
            block = self.searchDrops[i]
            dropValue = block.controls[0].value
            fieldValue = block.controls[1].value

            if dropValue is None or dropValue == "" or fieldValue is None or fieldValue == "":
                continue

            # Если уже есть search[dropValue] то показываем Dialog
            if crireria.get(dropValue) is not None:
                Dialog(self.page, "Ошибка поиска", f'Для "{dropValue}" уже выбрано значение "{crireria[dropValue]}"', 
                        backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return
            if dropValue in ['Возраст', 'Номер пропуска', 'Курс']:
                try:
                    fieldValue = int(fieldValue)
                except ValueError:
                    Dialog(self.page, "Ошибка поиска", f'"{fieldValue}" не является числом', 
                        backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                    return
            crireria[self.keysUiToStudent[dropValue]] = fieldValue
        
        
        res = DB.findByCriteria(crireria)
        if res is None:
            Dialog(self.page, "Ошибка поиска", "Ничего не найдено", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
        
        self.searchRes.results.append(res)
        self.searchRes.criterias.append(crireria)
        self.ui.changePage(0)
        

    def build(self):
        if Auth.getUser() is not None:
            plusDropButton = ft.IconButton(
                icon=ft.icons.ADD_OUTLINED,
                on_click=lambda e: self.addDropdown(),
            )
            findButton = ft.ElevatedButton(
                "Найти",
                on_click=lambda e: self.find(),
            )
            buttons = ft.Row([plusDropButton, findButton], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            card1 = self.searchRes.build()
            return ft.Column(
                [ft.ResponsiveRow([
                    ft.Column(
                        [self.title, *self.searchDrops, buttons],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        col={"xs": 12, "sm": 12, "md": 5, "xl": 5}
                        ),
                        card1
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )],
                height=self.page.window_height-self.page.navigation_bar.height,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        else:
            return ft.Column(
                [ft.Text("Для просмотра информации необходимо войти в аккаунт", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)], 
                alignment=ft.MainAxisAlignment.CENTER, 
                height=self.page.window_height-self.page.navigation_bar.height,
                width=self.page.window_width,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        
class SearchDropdown:
    def __init__(self, ui: UI, index: int, variants: list[str]):
        self.page = ui.page
        self.ui = ui
        self.variants = variants
        self.index = index

    def build(self):
        drop = ft.Dropdown(
            options=[ft.dropdown.Option(variant) for variant in self.variants],
            hint_text="Выберите параметр",
            col={"xs": 5, "sm": 5, "md": 5, "xl": 5},
        )
        # TODO: Сделать неактивным если drop пустой
        valueField = ft.TextField(
            label="Значение", multiline=False, hint_text="Введите значение",
            col={"xs": 5, "sm": 5, "md": 5, "xl": 5}
        )
        delButton = ft.IconButton(
            icon=ft.icons.DELETE_OUTLINED,
            on_click=lambda e: self.ui.deleteDropdown(drop.value),
            col={"xs": 2, "sm": 2, "md": 2, "xl": 2},
        )
        return ft.ResponsiveRow(controls=[drop, valueField, delButton], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    

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
            self.ui.changePage(2)

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