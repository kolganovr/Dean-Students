from student import Student
from db import DB
        
def main():
    student = Student(personal_info={'name': 'Дмитрий', 'surname': 'Петров', 'age': 18, 'homeCity': 'Москва'}, 
                      contact_info={'address': 'ул Ленина, 1', 'phoneNumber': 1234567890}, 
                      study_info={'group': 'МИСИС', 'course': 1, 'pass_num': 1234, 'available_rooms': [1, 2, 3], 'ID': 1234567890, 'gradebookID': 1234567890})
    hash = DB.writeStudent(student)
    student = DB.getStudentByHash(hash)
    print(student)

if __name__ == "__main__":
    main()