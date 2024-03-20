import pyrebase
from cfg import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

class DB:
    @staticmethod
    def getHash(*args):
        # Используя SHA256 хеширует переданные аргументы
        import hashlib
        hash = hashlib.sha256()
        for arg in args:
            hash.update(str(arg).encode())

        return hash.hexdigest()
    
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
        return db.child("students").child(hash).get().val()

    @staticmethod
    def updateStudentByStudent(student, changes: dict):
        # Получаем текущие данные о студенте
        old_hash = DB.getHash(student.surname, student.name, student.age, student.phoneNumber)
        current_data = DB.getStudent(old_hash)

        # Обновляем данные
        for key, value in changes.items():
            current_data[key] = value
        
        # Генерируем новый хеш
        new_hash = DB.getHash(student.surname, student.name, student.age, student.phoneNumber)

        # Создаем новую запись в базе данных
        db.child("students").child(new_hash).set(current_data)
        return new_hash
    
    @staticmethod
    def updateStudent(hash: str, changes: dict):
        # Получаем текущие данные о студенте
        current_data = DB.getStudent(hash)

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