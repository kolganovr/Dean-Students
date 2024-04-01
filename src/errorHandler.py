from json import loads

class ErrorHandler:
    """
    Класс для обработки и логирования ошибок
    """
    @staticmethod
    def logError(e):
        # TODO: Сделать логирование ошибок в файл или в cloud storage
        print(f'Log: {e}')
        # Записываем в файл
        with open('data\\error.log', 'a') as file:
            file.write(str(e) + '\n')
    
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
        except:
            if "Failed to establish a new connection" in str(e) or 'Max retries exceeded with url' in str(e):
                raise ValueError("Нет соединения с интернетом")
            ErrorHandler.logError(e)
            raise ValueError("Неизвестная ошибка!")
        
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