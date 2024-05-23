from db import DB
from student import Student
import random
from tqdm import tqdm

class DBFiller:
    hashes = []
    homeCities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Нижний Новгород"]
    streets = ['Ул. Центральная', 'Ул. Молодежная', 'Ул. Лесная', 'Ул. Школьная', 'Ул. Садовая', 'Ул. Новая', 'Ул. Советская', 'Ул. Набережная', 'Ул. Заречная', 'Ул. Полевая']

    def fillDB(n: int):
        '''
        Заполняет базу данных студентами

        Параметры:
            n (int): Количество студентов
        '''
        with open('data/fillValues/subj.txt', 'r', encoding='utf-8') as f:
            subjects = f.read().splitlines()

        with open('data/fillValues/surnames.txt', 'r', encoding='utf-8') as f:
            surnames = f.read().splitlines()

        with open('data/fillValues/namesM.txt', 'r', encoding='utf-8') as f:
            namesM = f.read().splitlines()
        with open('data/fillValues/patronymicM.txt', 'r', encoding='utf-8') as f:
            patronymicsM = f.read().splitlines()

        with open('data/fillValues/namesW.txt', 'r', encoding='utf-8') as f:
            namesW = f.read().splitlines()
        with open('data/fillValues/patronymicW.txt', 'r', encoding='utf-8') as f:
            patronymicsW = f.read().splitlines()

        for i in tqdm(range(n)):
            gender = random.choice(["Мужской", "Женский"])

            surname = random.choice(surnames)
            if gender == "Женский":
                surname += "а"

            if gender == "Мужской":
                name = random.choice(namesM)
                patronymic = random.choice(patronymicsM)
            else:
                name = random.choice(namesW)
                patronymic = random.choice(patronymicsW)

            age = random.randint(18, 21)
            cource = age - 17

            homeCity = random.choice(DBFiller.homeCities)
            address = f"{random.choice(DBFiller.streets)}, д.{random.randint(1, 100)}, кв.{random.randint(1, 100)}"
            phoneNumber = f"+7{random.randint(1000000000, 9999999999)}"
            group = f"{random.randint(1, 50)}Б-{24-cource}"

            pass_num = random.randint(100000, 999999)
            status = "Студент"
            ID = random.randint(100000, 999999)
            gradebookID = random.randint(100000, 999999)
            form_of_study = "Очная"

            grades = {}
            for sem in range(cource*2):
                semName = f"Семестр {sem+1}"
                for _ in range(5):
                    subj = random.choice(subjects)
                    grade = random.randint(2, 5)
                    if semName not in grades:
                        grades[semName] = {}
                    grades[semName][subj] = grade

            grants = {}
            for sem in range(cource*2):
                semName = f"Семестр {sem+1}"
                isGrant = random.choice([True, False])
                if isGrant:
                    amount = random.randint(1000, 15000)
                else:
                    amount = 0
                order = random.randint(100000, 999999)
                grants[semName] = {'amount': amount, 'order': order}

            isBudget = random.choice([True, False])
            if not isBudget:
                isGotBudget = random.choice([True, False])
                if isGotBudget:
                    semWhenStart = random.randint(2, cource*2)

            type_of_education = {}
            for sem in range(cource*2):
                semName = f"Семестр {sem+1}"
                if isBudget:
                    type_of_education[semName] = {'amount': 0, 'order': random.randint(100000, 999999)}
                else:
                    if isGotBudget and sem >= semWhenStart:
                        type_of_education[semName] = {'amount': 0, 'order': random.randint(100000, 999999)}
                    else:
                        type_of_education[semName] = {'amount': random.randint(100000, 300000), 'order': random.randint(100000, 999999)}

            personal_info = {
                "surname": surname,
                "name": name,
                "patronymic": patronymic,
                "gender": gender,
                "age": age,
                "homeCity": homeCity
            }

            contact_info = {
                "address": address,
                "phoneNumber": phoneNumber
            }

            study_info = {
                "group": group,
                "course": cource,
                "pass_num": pass_num,
                "grades": grades,
                "grants": grants,
                "form_of_study": form_of_study,
                "type_of_education": type_of_education,
                "status": status,
                "ID": ID,
                "gradebookID": gradebookID
            }

            student = Student(personal_info, contact_info, study_info)

            hash = DB.writeStudent(student)
            DBFiller.hashes.append(hash)

DBFiller.fillDB(50)
