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
    def getHash(*args):
        hash = shake_256()
        for arg in args:
            hash.update(str(arg).encode())
        return hash.hexdigest(8)
    
    @staticmethod
    def getHashByStudent(student: Student):
        return DB.getHash(student.surname, student.name, student.age, student.phoneNumber)
    
    @staticmethod
    def writeStudent(student):
        hash = DB.getHash(student.surname, student.name, student.age, student.phoneNumber)
        db.child("students").child(hash).set(student.__dict__())
        return hash

    @staticmethod
    def getStudent(hash):
        student = db.child("students").child(hash).get().val()
        if student is None:
            raise ValueError("Student not found")
        return Student(**student)
    
    @staticmethod
    def updateStudentByStudent(student: Student, changes: dict):
        # Получаем текущие данные о студенте
        old_hash = DB.getHash(student.surname, student.name, student.age, student.phoneNumber)
        current_data = DB.getStudent(old_hash).__dict__()

        # Обновляем данные
        for key, value in changes.items():
            current_data[key] = value
        
        # Генерируем новый хеш
        new_hash = DB.getHash(current_data['surname'], current_data['name'], current_data['age'], current_data['phoneNumber'])

        # Создаем новую запись в базе данных
        db.child("students").child(new_hash).set(current_data)
        return new_hash
    
    @staticmethod
    def updateStudent(hash: str, changes: dict):
        # Получаем текущие данные о студенте
        current_data = DB.getStudent(hash).__dict__()

        # Обновляем данные
        for key, value in changes.items():
            current_data[key] = value
        
        # Генерируем новый хеш
        new_hash = DB.getHash(current_data)

        # Создаем новую запись в базе данных
        db.child("students").child(new_hash).set(current_data)

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
            result = db.child("students").order_by_child(key).equal_to(value).get()
            for student in result.each():
                students.add(Student(**student.val()))

        return students
        

def main():
    moscowStudents = DB.findByCriteria({"age": 19, "homeCity": "Москва"})
    print(*moscowStudents, sep="\n")


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