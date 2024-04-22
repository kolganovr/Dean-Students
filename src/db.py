from firebase import db
from cfg import firebaseConfig

from student import Student
from hashlib import shake_256

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
            student (Student or dict): Студент

        Возвращает:
            str: Хеш-значение студента

        Пример:
            >>> student = Student(...)
            >>> hash = DB.writeStudent(student)
            >>> print(hash)
            ed9dc20e31dbc1db
        """
        written = False
        if type(student) is dict:
            # Формируем необходимыйе словари personal_info, contact_info, study_info в словаре student получая пути к полям
            newStudent = {}
            for key, value in student.items():
                path = Student.getPathToField(key)
                if path.find("/") == -1:
                    raise ValueError(f"Invalid criteria {key}")
                path = path.split("/")
                if len(path) == 0:
                    raise ValueError(f"Invalid criteria {key}")
                if path[0] == "personal_info":
                    if 'personal_info' not in newStudent:
                        newStudent['personal_info'] = {}
                    newStudent['personal_info'][path[1]] = value
                elif path[0] == "contact_info":
                    if 'contact_info' not in newStudent:
                        newStudent['contact_info'] = {}
                    newStudent['contact_info'][path[1]] = value
                elif path[0] == "study_info":
                    if 'study_info' not in newStudent:
                        newStudent['study_info'] = {}
                    newStudent['study_info'][path[1]] = value
                else:
                    raise ValueError(f"Invalid criteria {key}")

            try:
                hash = DB._getHash(newStudent['personal_info']['surname'], newStudent['personal_info']['name'], 
                                   newStudent['personal_info']['age'], newStudent['contact_info']['phoneNumber'])
            except KeyError:
                raise ValueError("Ошибка в ключах словаря")

                
            print(newStudent)
            db.child("students").child(hash).set(newStudent)
            written = True
        
        if not written:
            hash = DB.getHashByStudent(student)

        # Если заданы оценки, то добавляем их в базу данных
        if type(student) is Student:
            grades = student.grades
            grants = student.grants
            type_of_education = student.type_of_education
        elif type(student) is dict:
            grades = student.get('grades')
            grants = student.get('grants')
            type_of_education = student.get('type_of_education')

        if grades is not None:
            for semestr in grades.keys():
                for subject in grades[semestr].keys():
                    db.child("grades").child(semestr).child(subject).child(hash).set(grades[semestr][subject])

        if grants is not None:
            for semestr in grants.keys():
                for grant in grants[semestr].keys():
                    db.child("grants").child(semestr).child(grant).child(hash).set(grants[semestr][grant])
                
        if type_of_education is not None:
            for semestr in type_of_education.keys():
                for subject in type_of_education[semestr].keys():
                    db.child("type_of_education").child(semestr).child(subject).child(hash).set(type_of_education[semestr][subject])
        
        if not written:
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
        allInfo = {}
        for key, val in current_data.items():
            allInfo.update(val)
        for key, val in changes.items():
            field = allInfo.get(key)
            if field is not None:
                if type(field) is dict:
                    for sem, value in field.items():
                        newVal = changes[key].get(sem)
                        if newVal is not None:
                            field[sem].update(changes[key][sem])
                else:
                    allInfo[key] = val

        # Формируем словарь по правилам структуры студента
        new_data = {}
        for key, val in allInfo.items():
            path = Student.getPathToField(key)
            path = path.split("/")
            if new_data.get(path[0]) is None:
                new_data[path[0]] = {path[1]: val}
            else:
                new_data[path[0]][path[1]] = val                
        
        print(new_data)
        return new_data


    
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
        try:
            current_data = DB.getStudentByHash(hash).__dict__()
        except AttributeError:
            raise ValueError(f"Студента больше нет в базе данных")

        # Обновляем данные
        # FIXME: Удаляет те оценки которые не были изменены
        print(changes)
        newData = DB._updateValues(current_data, changes)
        
        # Генерируем новый хеш
        # TODO: Проверка на то, нужно ли генерировать новый хеш
        
        new_hash = DB._getHash(newData['personal_info']['surname'], newData['personal_info']['name'], 
                                   newData['personal_info']['age'], newData['contact_info']['phoneNumber'])
        
        if new_hash != hash:
            DB.deleteStudents(hash)
            
        # Обновляем данные о студенте
        db.child("students").child(new_hash).update(newData)

        # Обновялем данные в таблицах оценок, стипендий и типа обучения
        # Оценки
        if "grades" in changes.keys() or new_hash != hash:
            for sem, val in newData['study_info']['grades'].items():
                for subj, mark in val.items():
                    if new_hash != hash:
                        db.child("grades").child(sem).child(subj).child(hash).remove()
                    db.child("grades").child(sem).child(subj).child(new_hash).set(mark)
            
        # Стипендии
        if "grants" in changes.keys() or new_hash != hash:
            for sem, val in newData['study_info']['grants'].items():
                if new_hash != hash:
                    db.child("grants").child(sem).child('amount').child(hash).remove()
                    db.child("grants").child(sem).child('order').child(hash).remove()
                db.child("grants").child(sem).child('amount').child(new_hash).set(val['amount'])
                db.child("grants").child(sem).child('order').child(new_hash).set(val['order'])

        # Тип обучения
        if "type_of_education" in changes.keys() or new_hash != hash:
            for sem, val in newData['study_info']['type_of_education'].items():
                if new_hash != hash:
                    db.child("type_of_education").child(sem).child('amount').child(hash).remove()
                    db.child("type_of_education").child(sem).child('order').child(hash).remove()
                db.child("type_of_education").child(sem).child('amount').child(new_hash).set(val['amount'])
                db.child("type_of_education").child(sem).child('order').child(new_hash).set(val['order'])

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
        
        for hash in args:
            # Получаем всю информацию о студенте
            student = DB.getStudentByHash(hash)

            # Удаляем записи в таблице о студентах
            db.child("students").child(hash).remove()

            # Удаляем записи в таблице о оценках
            if student.grades is not None:
                for semestr in student.grades.keys():
                    for subject in student.grades[semestr].keys():
                        db.child("grades").child(semestr).child(subject).child(hash).remove()

            # Удаляем записи в таблице о стипендиях
            if student.grants is not None:
                for semestr in student.grants.keys():
                    for order in student.grants[semestr].keys():
                        db.child("grants").child(semestr).child('order').child(hash).remove()
                        db.child("grants").child(semestr).child('amount').child(hash).remove()

            # Удаляем записи в таблице о типе обучения
            if student.type_of_education is not None:
                for semestr in student.type_of_education.keys():
                    for order in student.type_of_education[semestr].keys():
                        db.child("type_of_education").child(semestr).child('order').child(hash).remove()
                        db.child("type_of_education").child(semestr).child('amount').child(hash).remove()

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
            if key in ["grades"]:
                for key2, value2 in value.items():
                    for key3, value3 in value2.items():
                        # Хеши студентов
                        result = db.child(key).child(key2).child(key3).get()
                        result = dict(result.val())
                        for hash, val in result.items():
                            if val == value3:
                                students.add(DB.getStudentByHash(hash))
                continue
            if key in ["grants", "type_of_education"]:
                for key2, value2 in value.items():
                    amounts = db.child(key).child(key2).child('amount').get()
                    orders = db.child(key).child(key2).child('order').get()
                    amounts = dict(amounts.val())
                    orders = dict(orders.val())

                    for hash, val in amounts.items():
                        if val == list(value2.values())[0]:
                            students.add(DB.getStudentByHash(hash))
                    for hash, val in orders.items():
                        if val == list(value2.keys())[0]:
                            students.add(DB.getStudentByHash(hash))
                continue
                    

            # получаем путь до нужного критерия
            path = Student.getPathToField(key)

            if len(path) == 0:
                raise ValueError(f"Invalid criteria {key}")
            
            result = db.child("students").order_by_child(path).equal_to(value).get()
            
            for student in result.each():
                students.add(Student(**student.val()))

        # Убеждаемся что у всех вариантов исполняются одновременно все критерии
        for key, value in criterias.items():
            path = Student.getPathToField(key) # 'personal_info/name'
            for student in students.copy():
                if key in ["grades"]:
                    for key2, value2 in value.items():
                        for key3, value3 in value2.items():
                            # Хеши студентов
                            result = db.child(key).child(key2).child(key3).get()
                            result = dict(result.val())
                            for hash, val in result.items():
                                if val != value3:
                                    students.remove(student)
                                    break
                    continue

                if key in ["grants", "type_of_education"]:
                    for key2, value2 in value.items():
                        amounts = db.child(key).child(key2).child('amount').get()
                        orders = db.child(key).child(key2).child('order').get()
                        amounts = dict(amounts.val())
                        orders = dict(orders.val())

                        for hash, val in amounts.items():
                            if val != list(value2.values())[0]:
                                students.remove(student)
                                break
                        for hash, val in orders.items():
                            if val != list(value2.keys())[0]:
                                students.remove(student)
                                break
                    continue

                current_data_pointer = student.__dict__()
                for step in path.split("/"):
                    current_data_pointer = current_data_pointer[step]
                if current_data_pointer != value:
                    students.remove(student)

        return list(students) if len(students) > 0 else None