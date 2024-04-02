import flet as ft
from auth import Auth, SaverUser
from db import DB
from student import Student
from errorHandler import ErrorHandler

from datetime import datetime
from os import path, makedirs

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
        elif pageNum == 1:
            self.editPage.searchRes.results = self.searchPage.searchRes.results
            self.editPage.searchRes.resulutsCards = self.searchPage.searchRes.resulutsCards
            self.editPage.searchRes.criterias = self.searchPage.searchRes.criterias
            self.page.controls = [self.editPage.build()]
            self.page.update()
        elif pageNum == 2:
            self.page.controls = [self.createPage.build()]
            self.page.update()
        elif pageNum == 3:
            self.page.controls = [self.authPage.build()]
            self.page.update()

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Деканат-студенты"
        self.authPage = AuthPage(self)
        self.searchPage = SearchEditPage(self, "Search")
        self.editPage = SearchEditPage(self, "Edit")
        self.createPage = CreatePage(self)

        # TODO: Сделать адпированным под масштабы экрана
        # TODO: Сделать обновление высоты и ширины блоков при изменении размера экрана (если возможно)
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
                    label="Создание", icon=ft.icons.ADD_OUTLINED, selected_icon=ft.icons.ADD
                ),
                ft.NavigationDestination(
                    label="Вход", icon=ft.icons.LOGIN_OUTLINED, selected_icon=ft.icons.LOGIN
                )
            ],
            on_change=lambda e: self.changePage(e.control.selected_index),
            selected_index=3,
            height=80
        )
        page.navigation_bar = self.navBar
        page.controls = [self.authPage.build()]
        page.update()

    def deleteDropdown(self, value: str, mode: str):
        find = False
        if mode == "Search":
            drops = self.searchPage.searchDrops
        elif mode == "Edit":
            drops = self.editPage.searchDrops
        else:
            drops = self.createPage.createDrops
        
        if len(drops) > 0:
            for i in range(len(drops)-1, -1, -1):
                block = drops[i]
                if block.controls[0].value == value:
                    drops.pop(i)
                    find = True
                    break
            if find:
                if mode == "Search":
                    self.changePage(0)
                elif mode == "Edit":
                    self.changePage(1)
                else:
                    self.changePage(2)
        if not find:
            Dialog(self.page, "Ошибка удаления", "Не удалось удалить блок", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
        
    def signOut(self):
        self.searchPage = SearchEditPage(self, "Search")
        self.editPage = SearchEditPage(self, "Edit")
        self.createPage = CreatePage(self)
        self.changePage(3)
            
class NeedToLogin:
    """
    Класс для отображения страницы, когда пользователь не авторизован
    """
    def __init__(self, ui: UI, page: ft.Page, text: str = "Для просмотра информации необходимо войти в соответствующий аккаунт"):
        self.ui = ui
        self.page = page
        self.title = ft.Text(text, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    
    def build(self):
        button = ft.ElevatedButton(
            "На страницу входа",
            on_click=lambda e: self.ui.changePage(3),
        )
        return ft.Column(
            [self.title, button], 
            alignment=ft.MainAxisAlignment.CENTER, 
            height=self.page.window_height-self.page.navigation_bar.height,
            width=self.page.window_width,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

class SearchEditPage:
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

            @staticmethod
            def getNouns(number, words : list):
                if number % 10 == 1 and number % 100 != 11:
                    return f'{number} {words[0]}'
                
                if number % 10 >= 2 and number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
                    return f'{number} {words[1]}'

                return f'{number} {words[2]}'
            
            def build(self):
                #           Кол-во записей в поиске
                # Чекбокс
                #           Критерии поиска

                self.checkBox = ft.Checkbox(value=self.isSelected, on_change=self.change)
                self.count = ft.Text(f'{self.getNouns(len(self.res), ["запись", "записи", "записей"])}', size=20)
                
                # Переименовываем ключи студента в ключи ui {'age':...} -> {'Возраст':...} используя SearchPage.keysStudentToUi
                self.criteria = {SearchEditPage.keysStudentToUi[key]: value for key, value in self.criteria.items()}

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
            
        def __init__(self, page: ft.Page, mode: str):
            self.page = page
            self.mode = mode
            self.results = [] # Список списков словарей студентов - результатов поиска
            self.criterias = [] # Список списков словарей критериев поиска
            self.resulutsCards = []
        
        def fillCards(self):
            self.resulutsCards = []
            for i in range(len(self.results)):
                self.resulutsCards.append(self.SearchResultsCard(self.results[i], self.criterias[i]))
        
        def exportToCSV(self):
            # Если нет папки export, то создаем ее
            if not path.exists('export'):
                makedirs('export')

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
            with open(f"export\\export_{time}.csv", 'w', newline='', encoding='utf-8') as csvfile:
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
            
            # Получаем полный путь к экспортируемому файлу
            exportedFilePath = path.abspath(f"export\\export_{time}.csv")

            self.page.set_clipboard(exportedFilePath)
            Dialog(self.page, "Успешный экспорт", f"Путь скопирован в буфер обмена\nПуть: {exportedFilePath}", 
                backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            
        def deleteFromDB(self):
            studentsToDelete = []
            for i in range(len(self.resulutsCards)):
                if self.resulutsCards[i].isSelected:
                    for j in range(len(self.results[i])):
                        studentsToDelete.append(self.results[i][j])

            if len(studentsToDelete) == 0:
                Dialog(self.page, "Ошибка удаления", "Ничего не выбрано", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return
            
            try:
                DB.deleteStudents(*studentsToDelete)
            except Exception as e:
                Dialog(self.page, "Ошибка удаления", str(e), 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return

            Dialog(self.page, "Успешное удаление", "Студенты удалены" if len(studentsToDelete) > 1 else "Студент удален",
                backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            
        def build(self):
            self.fillCards()
            # div = ft.VerticalDivider() # TODO: Может быть сделать возможность двигать слайдер
            scrollCol = ft.Column(
                controls=[self.resulutsCards[i].build() for i in range(len(self.resulutsCards))],
                scroll=ft.ScrollMode.ALWAYS,
            )
            showButton = ft.ElevatedButton(
                "Показать",
                disabled=True
            )
            exportButton = ft.ElevatedButton(
                "Экспорт в CSV",
                on_click=lambda e: self.exportToCSV(),
            )
            deleteFromDBButton = ft.ElevatedButton(
                "Удалить из БД",
                on_click=lambda e: self.deleteFromDB(),
            )
            buttonRow = ft.Row(
                [showButton, exportButton] if self.mode == "Search" else [deleteFromDBButton], alignment=ft.MainAxisAlignment.SPACE_EVENLY
            )
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [scrollCol, buttonRow if self.mode == "Search" else buttonRow],
                    ),
                    padding=20
                ),
                col={'xs': 12, 'sm': 12, 'md': 7, 'xl': 7}
            )
            
            return card
        
    def __init__(self, ui: UI, mode: str = "Search"):
        self.ui = ui
        self.page = ui.page
        self.mode = mode
        if mode == "Search":
            self.title = ft.Text("Поиск", size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        elif mode == "Edit":
            self.title = ft.Text("Изменение", size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.searchRes = self.SearchResults(self.page, self.mode)
        self.searchDrops = [SearchDropdown(self.ui, 0, self.searchCategories, self.mode).build()]


    def addDropdown(self):
        self.searchDrops.append(SearchDropdown(self.ui, len(self.searchDrops), self.searchCategories, self.mode).build())
        if self.mode == "Search":
            self.ui.changePage(0)
        elif self.mode == "Edit":
            self.ui.changePage(1)

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
        if self.mode == "Search":
            self.ui.changePage(0)
        elif self.mode == "Edit":
            self.ui.changePage(1)

    def edit(self):
        # Получаем хеш каждого студента из выбранных SearchResultCard
        selectedStudents = []
        for i in range(len(self.searchRes.resulutsCards)):
            if self.searchRes.resulutsCards[i].isSelected:
                for j in range(len(self.searchRes.results[i])):
                    selectedStudents.append(self.searchRes.results[i][j])
                

        selectedStudents = list(set(selectedStudents))

        if len(selectedStudents) == 0:
            Dialog(self.page, "Ошибка изменения", "Для начала выберите хотя бы одного студента", 
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
        
        hashes = [DB.getHashByStudent(student) for student in selectedStudents]
        
        # Получаем словарь с изменяемыми данными из дропбоксов
        changes = {}

        for i in range(len(self.searchDrops)):
            block = self.searchDrops[i]
            dropValue = block.controls[0].value
            fieldValue = block.controls[1].value
            if dropValue is None or dropValue == "":
                continue
            if dropValue in ['Возраст', 'Номер пропуска', 'Курс']:
                try:
                    fieldValue = int(fieldValue)
                except ValueError:
                    Dialog(self.page, "Ошибка изменения", f'"{fieldValue}" не является числом', 
                        backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                    return
            changes[self.keysUiToStudent[dropValue]] = fieldValue
        
        if len(changes) == 0:
            Dialog(self.page, "Ошибка изменения", "Нет изменений",
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
        
        for hash in hashes:
            try:
                DB.updateStudent(hash, changes)
            except Exception as e:
                message = ErrorHandler.getErrorMessage(e)
                Dialog(self.page, "Ошибка изменения", message, 
                    backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return

        Dialog(self.page, "Изменения сохранены", "Все изменения сохранены",
               backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
        
        # Удаляем все карточки поиска ибо в них могли измениться данные
        # TODO: Обновлять все затронутые карточки
        self.ui.searchPage.searchRes.results = []
        self.ui.searchPage.searchRes.criterias = []
        self.ui.searchPage.searchRes.resulutsCards = []
        
        self.ui.changePage(1)
        

    def build(self):
        if Auth.getUser() is not None and ((self.mode == "Search") or (self.mode == "Edit" and Auth.getUser()['email'] == 'admin@gmail.com')):
            plusDropButton = ft.IconButton(
                icon=ft.icons.ADD_OUTLINED,
                on_click=lambda e: self.addDropdown(),
            )
            findButton = ft.ElevatedButton(
                "Найти",
                on_click=lambda e: self.find(),
            )
            editButton = ft.ElevatedButton(
                "Редактировать",
                on_click=lambda e: self.edit(),
            )
            
            buttons = ft.Row([plusDropButton, findButton if self.mode == "Search" else editButton], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
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
            return NeedToLogin(self.ui, self.page).build()
        
class SearchDropdown:
    def __init__(self, ui: UI, index: int, variants: list[str], mode: str):
        self.page = ui.page
        self.ui = ui
        self.variants = variants
        self.index = index
        self.mode = mode

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
            on_click=lambda e: self.ui.deleteDropdown(drop.value, self.mode),
            col={"xs": 2, "sm": 2, "md": 2, "xl": 2},
        )
        return ft.ResponsiveRow(controls=[drop, valueField, delButton], vertical_alignment=ft.CrossAxisAlignment.CENTER)


class CreatePage:
    """
    Класс для отображения страницы создания студента
    """
    def __init__(self, ui: UI):
        self.ui = ui
        self.page = ui.page
        self.title = ft.Text("Создание студента", size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.createButton = ft.ElevatedButton(
            "Создать",
            on_click=lambda e: self.create(),
        )
        self.cancelButton = ft.ElevatedButton(
            "Отмена",
            on_click=lambda e: self.cancel(),
        )
        # Сразу создаем дропы для задания хешируемых параметров: Фамилия, Имя, Возраст, Телефон
        self.createDrops = [
            CreateDropdown(self.ui, 0, ['Фамилия']).build(),
            CreateDropdown(self.ui, 1, ['Имя']).build(),
            CreateDropdown(self.ui, 2, ['Возраст']).build(),
            CreateDropdown(self.ui, 3, ['Телефон']).build(),
        ]
        self.hashStudent = None
            

    def addDropdown(self):
        # TODO: Оставлять только категории, котрые еще не добавлены
        # FIXME: Будет проблема с последним элементом (нельзя будет удалить из-за логики удаления)
        self.createDrops.append(CreateDropdown(self.ui, len(self.createDrops), SearchEditPage.searchCategories).build())
        self.ui.changePage(2)

    def create(self):
        # Получаем словарь с данными из дропбоксов
        student = {}
        for i in range(len(self.createDrops)):
            block = self.createDrops[i]
            dropValue = block.controls[0].value
            fieldValue = block.controls[1].value
            if dropValue is None or dropValue == "":
                continue
            if dropValue in ['Возраст', 'Номер пропуска', 'Курс']:
                try:
                    if dropValue == 'Возраст' and fieldValue == "":
                        Dialog(self.page, "Ошибка создания", "Не заполнены обязательные поля",
                            backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                        return
                    
                    fieldValue = int(fieldValue)
                except ValueError:
                    Dialog(self.page, "Ошибка создания", f'"{fieldValue}" не является числом', 
                        backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                    return
            student[SearchEditPage.keysUiToStudent[dropValue]] = fieldValue
        
        if len(student) == 0:
            Dialog(self.page, "Ошибка создания", "Нет данных",
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
    
        keys = list(student.keys())
        for key in keys:
            if student[key] == "":
                Dialog(self.page, "Ошибка создания", "Не заполнены обязательные поля",
                    backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return
        
        try:
            self.hashStudent = DB.writeStudent(student)
        except Exception as e:
            message = ErrorHandler.getErrorMessage(e)
            Dialog(self.page, "Ошибка записи", message, 
                backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return

        Dialog(self.page, "Студент создан", "Студент успешно создан",
                backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
        
    def cancel(self):
        '''
        Метод для отмены создания студента
        Удаляет только что созданного студента
        '''
        if self.hashStudent is None:
            Dialog(self.page, "Ошибка отмены", "Нет данных для отмены",
                   backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
        try:
            DB.deleteStudents(self.hashStudent)
        except Exception as e:
            # TODO: Сделать централизованную обработку ошибок
            Dialog(self.page, "Ошибка отмены", str(e), 
                backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
            return
        
        Dialog(self.page, "Отмена создания", "Создание студента отменено",
                backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()

        
    def build(self):
        if Auth.getUser() is not None and Auth.getUser()['email'] == 'admin@gmail.com':
            plusDropButton = ft.IconButton(
                icon=ft.icons.ADD_OUTLINED,
                on_click=lambda e: self.addDropdown(),
            )
            buttons = ft.Row([plusDropButton, self.createButton, self.cancelButton], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

            listView = ft.ListView(
                controls=[self.createDrops[i] for i in range(len(self.createDrops))],
                spacing=20,
                height=min(self.page.window_height-self.page.navigation_bar.height-250, len(self.createDrops)*(55+20)),
            )
            card = ft.Column(
                [ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [self.title, listView, buttons],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
                        ),
                        padding=20
                    ),
                    col={'xs': 12, 'sm': 12, 'md': 7, 'xl': 7}
                )],
                alignment=ft.MainAxisAlignment.CENTER,
                height=self.page.window_height-self.page.navigation_bar.height-50,
            )
            return card
        else:
            return NeedToLogin(self.ui, self.page).build()
        
class CreateDropdown:
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
            value=self.variants[0] if len(self.variants) == 1 else None,
            disabled=len(self.variants) == 1
        )
        valueField = ft.TextField(
            label="Значение", multiline=False, hint_text="Введите значение",
            col={"xs": 5, "sm": 5, "md": 5, "xl": 5}
        )
        delButton = ft.IconButton(
            icon=ft.icons.DELETE_OUTLINED,
            on_click=lambda e: self.ui.deleteDropdown(drop.value, "Create"),
            col={"xs": 2, "sm": 2, "md": 2, "xl": 2},
        )
        if len(self.variants) > 1:
            return ft.ResponsiveRow(controls=[drop, valueField, delButton], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            return ft.ResponsiveRow(controls=[drop, valueField], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    

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

        def click_enterButton(recover: bool = False):
            if recover:
                # Если восстанавливаем пользователя из памяти
                try:
                    email, password = SaverUser.loadUser()
                except Exception as e:
                    # TODO: Сделать централизованную обработку ошибок
                    Dialog(self.page, "Ошибка входа", str(e), backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                    return
                
            try:
                if recover:
                    Auth.login(email, password)
                else:
                    Auth.login(self.emailField.value, self.passwordField.value)
            except ValueError as err:
                Dialog(self.page, "Ошибка входа", str(err), backAction=ft.ElevatedButton("OK", on_click=Dialog.closeDialog)).build()
                return
            
            if self.rememberUser:
                SaverUser.saveUser(self.emailField.value, self.passwordField.value)

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

        def rememberCheckBox(e):
            self.rememberUser = e.control.value

        def backToEnter(e):
            self.clickedRegister = False
            self.passwordFieldConfirm.value = ""
            self.page.controls = [self.build(register=False)]
            self.page.update()
            
        def click_signOutButton(e):
            Auth.signOut()
            SaverUser.deleteSavedUser()
            # Очистка полей ввода
            self.emailField.value = ""
            self.passwordField.value = ""
            self.passwordFieldConfirm.value = ""
            self.currentEmail.value = ""
            self.clickedRegister = False
            self.ui.signOut()
            # Обновляем страницу
            self.ui.changePage(3)

        self.emailField = ft.TextField(label="Email", multiline=False, hint_text="example@example.com")
        self.passwordField = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
        self.passwordFieldConfirm = ft.TextField(label="Подтверждение пароля", password=True, can_reveal_password=True)
        self.enterButton = ft.ElevatedButton(text="Вход", on_click=lambda e: click_enterButton())
        self.registerButton = ft.ElevatedButton(text="Регистрация", on_click=click_registerButton)
        self.recoverButton = ft.ElevatedButton(text="Войти по сохранённым данным", on_click=lambda e: click_enterButton(recover=True))
        self.rememberUser = False
        self.rememberMeCheckbox = ft.Checkbox(label="Запомнить меня", value=False, on_change=lambda e: rememberCheckBox(e))
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
                return self.InfoCard([self.emailField, self.passwordField, self.rememberMeCheckbox, ft.Row([self.enterButton, self.recoverButton, self.registerButton])], page=self.page).build()
            
class Dialog:
    """
    Класс для отображения диалоговых окон
    """
    def __init__(self,page: ft.Page, title: str, content: str, backAction: ft.ElevatedButton = None, actions: list[ft.ElevatedButton] = []):
        self.page = page
        self.title = title
        self.content = content
        if backAction is None:
            self.backAction = ft.ElevatedButton("OK", on_click=Dialog.closeDialog)
        self.backAction = backAction
        self.actions = actions

    def closeDialog(self):
        self.page.dialog.open = False
        self.page.update()
    
    def build(self):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title),
            content=ft.Text(self.content),
            actions=[ft.ResponsiveRow([self.backAction, *self.actions])],
        )
        dialog.actions[0].on_click = lambda e: self.closeDialog()
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()