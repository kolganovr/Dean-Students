import pyrebase
from cfg import firebaseConfig
from student import Student
from hashlib import shake_256

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

class DB:
    @staticmethod
    def _getHash(*args):
        """
        Считает хеш-значение заданных аргументов, используя алгоритм SHAKE-256.

        Параметры:
            *args (Any): Аргументы для хеширования.

        Возвращает:
            str: Хеш-значение аргументов

        Пример:
            >>> hash = DB._getHash("Roman", 20)
            >>> print(hash)
            ed9dc20e31dbc1db
        """
        hash = shake_256()
        for arg in args:
            hash.update(str(arg).encode())
        return hash.hexdigest(8)
    
    @staticmethod
    def getHashByStudent(student: Student):
        """
        Считает хеш-значение студента для использования как ключ, используя алгоритм SHAKE-256.

        Параметры:
            student (Student): Студент

        Возвращает:
            str: Хеш-значение студента

        Пример:
            >>> student = Student(...)
            >>> hash = DB.getHashByStudent(student)
            >>> print(hash)
            ed9dc20e31dbc1db

        Дополнительные сведения:
            Хеширует имя, фамилию, возраст и номер телефона
        """
        return DB._getHash(student.surname, student.name, student.age, student.phoneNumber)
    
    @staticmethod
    def writeStudent(student):
        """
        Добавляет студента в базу данных.

        Параметры:
            student (Student): Студент

        Возвращает:
            str: Хеш-значение студента

        Пример:
            >>> student = Student(...)
            >>> hash = DB.writeStudent(student)
            >>> print(hash)
            ed9dc20e31dbc1db
        """
        hash = DB.getHashByStudent(student)
        db.child("students").child(hash).set(student.__dict__())
        return hash

    @staticmethod
    def getStudentByHash(hash):
        """
        Возвращает студента по его хешу.

        Параметры:
            hash (str): Хеш-значение студента

        Возвращает:
            Student: Студент

        Пример:
            >>> student = DB.getStudentByHash("ed9dc20e31dbc1db")
            >>> print(student)
            [Информация о студенте из метода Student.__str__()]
        """
        student = db.child("students").child(hash).get().val()
        if student is None:
            return None
        return Student(**student)
    
    @staticmethod
    def _updateValues(current_data: dict, changes: dict):
        """
        Служебная функция для обновления значений в словаре студента.

        Параметры:
            current_data (dict): Словарь текущих данных о студенте
            changes (dict): Изменения, которые нужно внести (словь ключ-значение тех полей, которые нужно обновить)

        Возвращает:
            dict: Обновленные данные о студенте

        Пример:
            >>> current_data = {
                ...
                'personal_info':{'age': 18, ...}
                ...
            }
            >>> changes = {"age": 21}
            >>> new_data = DB._updateValues(current_data, changes)
            >>> print(new_data)
            {
                ...
                'personal_info':{'age': 21, ...}
                ...
            }
        """
        for key, value in changes.items():
            path = Student.getPathToField(key)
            if path.find("/") == -1:
                raise ValueError(f"Invalid criteria {key}")
            path = path.split("/")
            if len(path) == 0:
                raise ValueError(f"Invalid criteria {key}")
                
            current_data_pointer = current_data
            for step in path[:-1]:
                current_data_pointer = current_data_pointer[step]
            current_data_pointer[path[-1]] = value

        return current_data
    
    @staticmethod
    def updateStudent(student, changes: dict):
        """
        Обновляет данные о студенте по студенту и его хешу.

        Параметры:
            student (Student or str): Студент или его хеш
            changes (dict): Изменения, которые нужно внести (словь ключ-значение тех полей, которые нужно обновить)

        Возвращает:
            str: Новое хеш-значение студента

        Пример:
            >>> changes = {"age": 21}
            >>> hash = DB.updateStudent("ed9dc20e31dbc1db", changes)
            >>> print(hash)
            fe9dc20e31dbc1db

        Дополнительные сведения:
            Хеш поменялся тк было изменено поле отвечающее за генерацию хеша (см. метод _getHashByStudent)
        """
        if type(student) is Student:
            hash = DB._getHash(student.surname, student.name, student.age, student.phoneNumber)
        else:
            hash = student

        # Получаем текущие данные о студенте
        current_data = DB.getStudentByHash(hash).__dict__()

        # Обновляем данные
        newData = DB._updateValues(current_data, changes)
        
        # Генерируем новый хеш
        # TODO: Проверка на то, нужно ли генерировать новый хеш
        
        new_hash = DB._getHash(newData['personal_info']['surname'], newData['personal_info']['name'], 
                                   newData['personal_info']['age'], newData['contact_info']['phoneNumber'])
            
        # Обновляем данные о студенте
        db.child("students").child(new_hash).update(newData)

        # Удаляем старого студента
        DB.deleteStudents(hash)

        return new_hash

    @staticmethod
    def deleteAllStudents():
        """
        Удаляет все записи о студентах из базы данных.

        Пример:
            >>> DB.deleteAllStudents()
            Are you sure you want to delete all students? (y/n): y
            All students deleted
        """
        
        if input("Are you sure you want to delete all students? (y/n): ") != "y":
            return
        db.child("students").remove()
        print("All students deleted")

    @staticmethod
    def deleteStudents(*args):
        """
        Удаляет записи о студентах из базы данных.

        Параметры:
            *args (Student or str): Студенты или их хеши

        Пример:
            >>> DB.deleteStudents("ed9dc20e31dbc1db", "fe9dc20e31dbc1db")
            >>> DB.deleteStudents(student1, student2)
        """
        if all([type(arg) is Student for arg in args]):
            args = [DB.getHashByStudent(arg) for arg in args]
        elif all([type(arg) is str for arg in args]):
            args = args
        else:
            raise ValueError("Invalid arguments")
        
        for arg in args:
            db.child("students").child(arg).remove()

    @staticmethod
    def findByCriteria(criterias: dict):
        """
        Поиск студентов по критериям.

        Параметры:
            criterias (dict): Критерии поиска (словь ключ-значение тех полей, по которым нужно искать)

        Возвращает:
            list: Список студентов, подходящих под все критерии

        Пример:
            >>> students = DB.findByCriteria({'surname': 'Петров', 'age': 18, 'homeCity': 'Москва'})
            >>> print(students)
            [Student(...), Student(...), ...]
        """
        # Получаем список студентов подходящих под все критерии одновременно
        students = set()
        for key, value in criterias.items():
            # получаем путь до нужного критерия
            path = Student.getPathToField(key)

            if len(path) == 0:
                raise ValueError(f"Invalid criteria {key}")
            
            result = db.child("students").order_by_child(path).equal_to(value).get()
            
            for student in result.each():
                students.add(Student(**student.val()))

        return list(students) if len(students) > 0 else None