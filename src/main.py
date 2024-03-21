import pyrebase
from cfg import firebaseConfig
import time
import sys

from hashlib import shake_256

from student import Student

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()

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
            raise ValueError("Student not found")
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
        db.child("students").remove()

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
        

def main():
    student = Student(personal_info={'name': 'Николай', 'surname': 'Петров', 'age': 18, 'homeCity': 'Москва'}, 
                      contact_info={'address': 'ул Ленина, 1', 'phoneNumber': 1234567890}, 
                      study_info={'group': 'МИСИС', 'course': 1, 'pass_num': 1234, 'available_rooms': [1, 2, 3], 'ID': 1234567890, 'gradebookID': 1234567890})
    hash = DB.writeStudent(student)
    # print(*DB.findByCriteria({"homeCity": "Москва", "course": 2}))

    DB.updateStudent(hash, {'study_info': {'available_rooms': [1, 2, 3, 4]}})

# def get_emeil_and_password(confirmation=False):
#     email = input("Email: ")
#     password = input("Password: ")
#     if confirmation:
#         confirmed_password = input("Confirm Password: ")
#         return email, password, confirmed_password
#     return email, password

# def login():
#     email, password = get_emeil_and_password(confirmation=False)
#     try:
#         user = auth.sign_in_with_email_and_password(email, password)
#         print("Login Successful")
#     except:
#         print("Login Failed")

# def sign_in():
#     email, password = get_emeil_and_password(confirmation=False)
#     try:
#         user = auth.create_user_with_email_and_password(email, password)
#         print("Sign In Successful")
#     except:
#         print("Sign In Failed")

# def sign_up():
#     email, password, confirmed_password = get_emeil_and_password(confirmation=True)
#     if password == confirmed_password:
#         try:
#             user = auth.create_user_with_email_and_password(email, password)
#             print("Sign Up Successful")
#         except:
#             print("Email already in use")
#     else:
#         print("Passwords do not match")

if __name__ == "__main__":
    main()