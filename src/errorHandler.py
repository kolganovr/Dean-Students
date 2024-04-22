from json import loads
from firebase import storage
import threading

class ErrorHandler:
    """
    Класс для обработки и логирования ошибок
    """
    @staticmethod
    def logError(e):
        t = threading.Thread(target=ErrorHandler._logError, args=(e,))
        t.start()

    @staticmethod
    def _logError(e):
        # Скачиваем файл из Cloud Storage
        storage.child('data/error.log').download('','data/error.log')

        # Записываем в файл
        with open('data\\error.log', 'a', encoding='utf-8') as file:
            file.write(str(e) + '\n')

        # Добавляем в файл в Cloud Storage
        storage.child('data/error.log').put('data/error.log')

        # Очищаем файл
        with open('data\\error.log', 'w', encoding='utf-8') as file:
            pass

    @staticmethod
    def clearLog():
        with open('data\\error.log', 'w', encoding='utf-8') as file:
            pass

        storage.child('data/error.log').put('data/error.log')

    @staticmethod
    def analyzeLog():
        # FIXME: Пока не работает из-за того как хранятся записи в Cloud Storage
        storage.child('data/error.log').download('','data/error.log')

        errors = {}
        with open('data\\error.log', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line in errors:
                    errors[line] += 1
                else:
                    errors[line] = 1
        
        # Считаем количество ошибок каждого типа и выводим их в порядке убывания в формате {количество: тип}
        sortedErrors = sorted(errors.items(), key=lambda x: x[1], reverse=True)

        print("Список ошибок:")
        for error in sortedErrors:
            print(f"{error[1]}: {error[0]}")

        print(f"Всего ошибок: {sum(errors.values())}")

        # Очищаем файл
        with open('data\\error.log', 'w', encoding='utf-8') as file:
            pass

    @staticmethod
    def handleException(e: Exception):
        """
        JSON обработка ошибок.

        Параметры:
            e (Exception): Ошибка при работе с аутентификацией
        
        Поднимает:
            ValueError с описанием ошибок
            ValueError c кодом ошибки если ошибка неизвестна
        """
        try:
            message = loads(e.args[1])['error']['message']
        except Exception as e:
            ErrorHandler.logError(e)
            print(e)
            if "Failed to establish a new connection" in str(e) or 'Max retries exceeded with url' in str(e):
                raise ValueError("Нет соединения с интернетом")
                
            raise ValueError("Неизвестная ошибка!")
        
        # ErrorHandler.logError(message)
        if message == "INVALID_LOGIN_CREDENTIALS":
            raise ValueError("Неверные логин или пароль!")
        elif message == "MISSING_PASSWORD":
            raise ValueError("Не указан пароль!")
        elif message == "INVALID_EMAIL":
            raise ValueError("Неверный email!")
        elif message == "EMAIL_EXISTS":
            raise ValueError("Пользователь с таким email уже существует!")
        else:
            ErrorHandler.logError(e)
            raise ValueError(message)
        
    @staticmethod
    def getErrorMessage(e):
        if "Permission denied" in str(e):
            return "Нет доступа к данным!"
        else:
            ErrorHandler.logError(e)
            print(e)
            return "Неизвестная ошибка!"