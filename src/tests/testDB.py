import pytest
import sys

sys.path.append('src')

from student import Student
from main import DB

# Фикстура для создания тестовых студентов
@pytest.fixture
def test_students():
    return [
        Student(personal_info={'name': 'TestName1', 'surname': 'TestSurname1', 'age': 20, 'homeCity': 'TestCity1'},
                contact_info={'address': 'TestAddress1', 'phoneNumber': 1234567890},
                study_info={'group': 'TestGroup1', 'course': 1, 'pass_num': 12345, 'available_rooms': [1, 2, 3], 'ID': 1234567890, 'gradebookID': 1234567890}),
        Student(personal_info={'name': 'TestName2', 'surname': 'TestSurname2', 'age': 21, 'homeCity': 'TestCity2'},
                contact_info={'address': 'TestAddress2', 'phoneNumber': 9876543210},
                study_info={'group': 'TestGroup2', 'course': 2, 'pass_num': 67890, 'available_rooms': [4, 5, 6], 'ID': 9876543210, 'gradebookID': 9876543210})
    ]

# Тестирование удаления студентов из базы данных
def test_delete_students(test_students):
    # Запись тестовых студентов в базу данных
    hashes = [DB.writeStudent(student) for student in test_students]

    # Удаление записей из базы данных
    DB.deleteStudents(*hashes)

    # Проверка отсутствия записей в базе данных
    for hash in hashes:
        assert DB.getStudentByHash(hash) is None

# Тестирование записи студентов в базу данных
def test_write_students(test_students):
    # Запись тестовых студентов в базу данных
    hashes = [DB.writeStudent(student) for student in test_students]

    # Проверка наличия записей в базе данных
    for hash, student in zip(hashes, test_students):
        retrieved_student = DB.getStudentByHash(hash)
        assert retrieved_student.__dict__() == student.__dict__()

    # Удаление записей из базы данных
    DB.deleteStudents(*hashes)

# Тестирование обновления данных студента
def test_update_student(test_students):
    # Запись тестового студента в базу данных
    test_student = test_students[0]
    hash = DB.writeStudent(test_student)

    # Обновление данных студента
    changes = {'personal_info': {'name': 'UpdatedName'}, 'study_info': {'group': 'UpdatedGroup', 'course': 3}}
    new_hash = DB.updateStudentByStudent(test_student, changes)

    # Проверка обновленных данных
    updated_student = DB.getStudentByHash(new_hash)
    assert updated_student.name == 'UpdatedName'
    assert updated_student.group == 'UpdatedGroup'
    assert updated_student.course == 3

    # Удаление записи из базы данных
    DB.deleteStudents(new_hash)

# Тестирование поиска студентов по критериям
def test_find_by_criteria(test_students):
    # Запись тестовых студентов в базу данных
    hashes = [DB.writeStudent(student) for student in test_students]

    # Поиск студентов по критериям
    criteria = {'homeCity': 'TestCity1'}
    found_students = DB.findByCriteria(criteria)

    # Проверка найденных студентов
    assert len(found_students) == 1
    assert found_students[0] == test_students[0]

    # Удаление записей из базы данных
    DB.deleteStudents(*hashes)