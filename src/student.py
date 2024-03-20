class Student():
    def __init__(self,surname,name, age, homeCity, address, phoneNumber, group, cource, patronymic=None):
        # ["surname", "name", "patronymic", "age", "homeCity", "address", "phoneNumber", "group", "cource"]
        self.surname = surname
        self.name = name
        self.age = age
        self.homeCity = homeCity
        self.address = address
        self.phoneNumber = phoneNumber
        self.group = group
        self.cource = cource
        self.patronymic = patronymic

    def __str__(self):
        return ', '.join([str(value) for key, value in self.__dict__().items() if value is not None])

    def __dict__(self):
        return {
            "surname": self.surname,
            "name": self.name,
            "patronymic": self.patronymic,
            "age": self.age,
            "homeCity": self.homeCity,
            "address": self.address,
            "phoneNumber": self.phoneNumber,
            "group": self.group,
            "cource": self.cource
        }
    
    # метод для создания множества (проверка на идентичность)
    def __eq__(self, other):
        return self.__dict__() == other.__dict__()
    
    # метод для создания хэша
    def __hash__(self):
        return hash(frozenset(self.__dict__().items()))
