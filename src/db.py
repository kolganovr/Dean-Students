import pyrebase
from cfg import firebaseConfig
from student import Student
from hashlib import shake_256

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

class DB:
    @staticmethod
    def _getHash(*args):
        hash = shake_256()
        for arg in args:
            hash.update(str(arg).encode())
        return hash.hexdigest(8)
    
    @staticmethod
    def getHashByStudent(student: Student):
        return DB._getHash(student.surname, student.name, student.age, student.phoneNumber)
    
    @staticmethod
    def writeStudent(student):
        hash = DB.getHashByStudent(student)
        db.child("students").child(hash).set(student.__dict__())
        return hash

    @staticmethod
    def getStudentByHash(hash):
        student = db.child("students").child(hash).get().val()
        if student is None:
            return None
        return Student(**student)
    
    @staticmethod
    def updateStudentByStudent(student: Student, changes: dict):
        # Получаем текущие данные о студенте
        old_hash = DB._getHash(student.surname, student.name, student.age, student.phoneNumber)
        current_data = DB.getStudentByHash(old_hash)
        
        # Генерируем новый хеш
        new_hash = DB._getHash(current_data.surname, current_data.name, current_data.age, current_data.phoneNumber)

        current_data = current_data.__dict__()
        # Обновляем данные
        newData = DB._updateValues(current_data, changes)

        print(changes, current_data, sep="\n\n")

        # Создаем новую запись в базе данных
        db.child("students").child(new_hash).update(newData)
        return new_hash
    

    def _updateValues(current_data: dict, changes: dict):
        for key, value in changes.items():
            if type(value) is dict:
                for k, v in value.items():
                    current_data[key][k] = v
            else:
                current_data[key] = value
        return current_data
    
    @staticmethod
    def updateStudent(hash: str, changes: dict):
    # ! Добавить проыверку на правильность ключей
        # Получаем текущие данные о студенте
        current_data = DB.getStudentByHash(hash).__dict__()

        # Обновляем данные
        newData = DB._updateValues(current_data, changes)
        
        # Генерируем новый хеш
        new_hash = DB._getHash(current_data)

        # Создаем новую запись в базе данных
        db.child("students").child(new_hash).update(newData)

        # Удаляем старую запись
        db.child("students").child(hash).remove()
        return new_hash
    
    @staticmethod
    def deleteAllStudents():
        if input("Are you sure you want to delete all students? (y/n): ") != "y":
            return
        db.child("students").remove()
        print("All students deleted")

    @staticmethod
    def deleteStudents(*args):
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