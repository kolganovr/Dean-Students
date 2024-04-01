from firebase import auth
from errorHandler import ErrorHandler

from cryptography.fernet import Fernet
from os import remove, path, makedirs

class SaverUser:    
    @staticmethod
    def saveUser(email, password):
        """
        Сохраняет данные пользователя в файл в зашифрованном виде для дальнейшей расшифровки.

        Параметры:
            email (str): email пользователя
            password (str): пароль пользователя
        """
        # Генерируем ключ для шифрования
        key = Fernet.generate_key()

        # Если нет папки data, создаем ее
        if not path.exists('data'):
            makedirs('data')

        # Сохраняем ключ в файл
        with open('data\\key.key', 'wb') as file:
            file.write(key)
        
        cipher_suite = Fernet(key)

        # Конвертируем email и пароль пользователя в байты
        user_data = f"{email}:{password}".encode()

        # Шифруем данные пользователя
        cipher_text = cipher_suite.encrypt(user_data)

        # Сохраняем зашифрованные данные и ключ, использованный для шифрования, в файл
        with open('data\\user_data.key', 'w') as file:
            file.write(cipher_text.decode() + '\n' + key.decode())


    @staticmethod
    def loadUser():
        """
        Расшифровывает и возвращает данные пользователя из файла.
        
        Возвращает:
            tuple: (email, password): Данные пользователя

        Поднимает:
            Exception: Нет сохраненных полльзовательских данных!
            Exception: Ошибка при чтении файла
        """
        # Читаем ключ из файла
        try:
            with open('data\\key.key', 'rb') as file:
                key = file.read()
        
            # Читаем зашифрованные данные из файла
            with open('data\\user_data.key', 'r') as file:
                data = file.read().split('\n')
                cipher_text = data[0].encode()

        except FileNotFoundError:
            raise Exception('Нет сохраненных пользовательских данных!')
        except Exception as e:
            raise Exception(e)

        # Создаем набор шифров с использованием ключа
        cipher_suite = Fernet(key)

        # Расшифровываем данные пользователя
        plain_text = cipher_suite.decrypt(cipher_text)

        # Конвертируем расшифрованные данные из байтов в строку
        user_data = plain_text.decode()

        # Разделяем данные пользователя на email и пароль
        email, password = user_data.split(':')

        return email, password


    @staticmethod
    def deleteSavedUser():
        """
        Удаляет файл с данными пользователя.
        """
        try:
            remove('user_data.key')
            remove('key.key')
        except FileNotFoundError:
            pass


class Auth:
    def _get_emeil_and_password(confirmation=False):
        """
        Получает email и password от пользователя.
        
        Параметры:
            confirmation (bool) = False: Нужно ли подтверждение пароля
        
        Возвращает:
            tuple: email, password

        Поднимает:
            ValueError: Пароли не совпадают
        
        Пример:
            >>> email, password = Auth._get_emeil_and_password()
            >>> print(email, password)
        """
        email = input("Email: ")
        password = input("Пароль: ")
        if confirmation:
            confirmed_password = input("Подтвердите пароль: ")
            if password != confirmed_password:
                raise Exception("Пароли не совпадают!")
            
        return email, password    

    @staticmethod
    def delete_user(email=None, password=None):
        """
        Удаляет пользователя запросив логин и пароль от аккаунта.

        Параметры:
            email (str) = None: Email пользователя
            password (str) = None: Пароль пользователя

        Возвращает:
            bool: Удалён ли аккаунт
        """
        user = Auth.login(email, password)
        if input(f"Вы уверены, что хотите удалить аккаунт? (y/n): ") != "y":
            return False
        
        id_token = user['idToken']
        try:
            auth.delete_user_account(id_token)
        except Exception as e:
            print(e)
            return False
        return True
    
        
    @staticmethod
    def login(email=None, password=None):
        """
        Логинит пользователя запросив email и password.

        Параметры:
            email (str) = None: Email пользователя
            password (str) = None: Пароль пользователя

        Возвращает:
            dict: Данные пользователя {'kind': '...', 'localId': '...', 'email': '...', 'displayName': '...', 
                                'emailVerified': True, 'idToken': '...', 'registered': True, 'refreshToken': '...', 'expiresIn': '...'}

        Поднимает: 
            ValueError: Неверные логин или пароль!
        """
        if email is None and password is None:
            email, password = Auth._get_emeil_and_password()
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except Exception as e:
            ErrorHandler.handleException(e)
        
        print("Вы успешно вошли!")
        return user                    


    @staticmethod
    def register(email=None, password=None, confirmed_password=None):
        """
        Регистрирует нового пользователя запросив email и password и подтверждение пароля.

        Параметры:
            email (str) = None: Email пользователя
            password (str) = None: Пароль пользователя
            confirmed_password (str) = None: Подтвержденный пароль

        Возвращает:
            dict: Данные пользователя {'kind': '...', 'localId': '...', 'email': '...', 'displayName': '...', 
                                'emailVerified': True, 'idToken': '...', 'registered': True, 'refreshToken': '...', 'expiresIn': '...'}

        Поднимает:
            ValueError: Пароли не совпадают
            ValueError: Пользователь с таким email уже существует!

        """
        # TODO: Сделать проверку на сложность пароля используя библиотеку passlib или re
        if email is None and password is None and confirmed_password is None:
            email, password = Auth._get_emeil_and_password(True)
        else:
            if password != confirmed_password:
                raise ValueError("Пароли не совпадают!")
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except Exception as e:
            ErrorHandler.handleException(e)
        
        print("Вы успешно зарегистрировались!")
        return user
    
    
    @staticmethod
    def signOut():
        """
        Выходит из аккаунта.
        """
        try:
            auth.current_user = None
            return True
        except Exception as e:
            ErrorHandler.handleException(e)

    
    @staticmethod
    def isAuth():
        """
        Проверяет, авторизирован ли пользователь.

        Возвращает:
            bool: Авторизирован ли пользователь
        """
        return auth.current_user is not None
    
    
    @staticmethod
    def getUser():
        """
        Возвращает данные пользователя.

        Возвращает:
            dict: Данные пользователя {'kind': '...', 'localId': '...', 'email': '...', 'displayName': '...', 
                                'emailVerified': True, 'idToken': '...', 'registered': True, 'refreshToken': '...', 'expiresIn': '...'}
        """
        return auth.current_user