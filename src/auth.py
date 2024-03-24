from firebase import auth

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
            if "INVALID_LOGIN_CREDENTIALS" in str(e):
                raise ValueError("Неверные логин или пароль!")
            else:
                print(e)
            return None
        
        print("Вы успешно вошли!")
        Auth.user = user
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
            if "EMAIL_EXISTS" in str(e):
                raise ValueError("Пользователь с таким email уже существует!")
            else:
                print(e)
            return None
        
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
            print(e)
            return False

    
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