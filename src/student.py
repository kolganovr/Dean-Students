class Student():
    surname = None
    name = None
    patronymic = None
    age = None
    homeCity = None
    address = None
    phoneNumber = None
    group = None
    course = None
    pass_num = None
    available_rooms = None
    ID = None
    gradebookID = None

    def __init__(self, personal_info: dict, contact_info: dict, study_info: dict):
        try:
            self.surname = personal_info['surname']
            self.name = personal_info['name']
            self.phoneNumber = contact_info['phoneNumber']
            self.age = personal_info['age']
        except KeyError:
            raise ValueError("Not enough information")
        
        self.patronymic = personal_info.get('patronymic')
        self.homeCity = personal_info.get('homeCity')
        self.address = contact_info.get('address')
        self.group = study_info.get('group')
        self.course = study_info.get('course')
        self.pass_num = study_info.get('pass_num')
        self.available_rooms = study_info.get('available_rooms')
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
                "available_rooms": self.available_rooms,
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
            
    
    # метод для создания множества (проверка на идентичность)
    def __eq__(self, other):
        return self.__dict__() == other.__dict__()
    
    # метод для создания хэша
    def __hash__(self):
        return hash(self.__str__())