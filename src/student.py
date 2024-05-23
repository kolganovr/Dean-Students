class Student():
    surname = None
    name = None
    patronymic = None
    gender = None
    age = None
    homeCity = None
    address = None
    phoneNumber = None
    group = None
    course = None
    pass_num = None
    grades = None
    grants = None
    form_of_study = None
    type_of_education = None
    status = None
    ID = None
    gradebookID = None

    def __init__(self, personal_info: dict, contact_info: dict, study_info: dict = None):
        try:
            self.surname = personal_info['surname']
            self.name = personal_info['name']
            self.phoneNumber = contact_info['phoneNumber']
            self.age = personal_info['age']
        except KeyError:
            raise ValueError("Not enough information")
        
        self.patronymic = personal_info.get('patronymic')
        self.gender = personal_info.get('gender')
        self.homeCity = personal_info.get('homeCity')
        self.address = contact_info.get('address')

        if study_info is not None:
            self.group = study_info.get('group')
            self.course = study_info.get('course')
            self.pass_num = study_info.get('pass_num')
            self.grades = study_info.get('grades')
            self.grants = study_info.get('grants')
            self.form_of_study = study_info.get('form_of_study')
            self.type_of_education = study_info.get('type_of_education')
            self.status = study_info.get('status')
            self.ID = study_info.get('ID')
            self.gradebookID = study_info.get('gradebookID')

    def __str__(self):
        return ', '.join([str(value) for _, value in self.__dict__().items() if value is not None])
    
    def __dict__(self):
        return {
            "personal_info": {
                "surname": self.surname,
                "name": self.name,
                "patronymic": self.patronymic,
                "gender": self.gender,
                "age": self.age,
                "homeCity": self.homeCity,
            },
            "contact_info": {
                "address": self.address,
                "phoneNumber": self.phoneNumber,
            },
            "study_info": {
                "group": self.group,
                "course": self.course,
                "pass_num": self.pass_num,
                "grades": self.grades,
                "grants": self.grants,
                "form_of_study": self.form_of_study,
                "type_of_education": self.type_of_education,
                "status": self.status,
                "ID": self.ID,
                "gradebookID": self.gradebookID
            }
        }
    
    @classmethod
    def getPathToField(cls, fieldName: str):
        # Получаем путь к полю в словаре студента
        d = cls.__dict__['__dict__'](cls)
        path = ""
        for key, value in d.items():
            if type(value) is dict:
                for k, v in value.items():
                    if k == fieldName:
                        path += f'{key}/{k}'
                        return path
            elif key == fieldName:
                path += f'{key}'
                return path
        
        raise ValueError(f"Invalid field name '{fieldName}'")
    
    def getFieldByPath(self, path: str):
        # Получаем значение поля по пути к нему
        d = self.__dict__()
        for step in path.split("/"):
            if type(d[step]) is dict:
                d = d[step]
            else:
                return d[step]
    
    @classmethod
    def getKeys(cls):
        """
        Возвращает список ключей словаря студента нижнего уровня
        """
        d = cls.__dict__['__dict__'](cls)
        topLevelKeys = list(d.keys())
        keys = []
        for key in topLevelKeys:
            if type(d[key]) is dict:
                keys += list(d[key].keys())
            else:
                keys.append(key)
        return keys
            
    # метод для создания множества (проверка на идентичность)
    def __eq__(self, other):
        return self.__dict__() == other.__dict__()
    
    # метод для создания хэша
    def __hash__(self):
        return hash(self.__str__())