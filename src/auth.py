from firebase import auth

class Auth:
    def _get_emeil_and_password(confirmation=False):
        """
        Получает email и password от пользователя.
        
        Параметры:
            confirmation (bool) = False: Нужно ли подтверждение пароля
        
        Возвращает:
            tuple: email, password
        
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
    def delete_user():
        """
        Удаляет пользователя запросив логин и пароль от аккаунта.

        Возвращает:
            bool: Удалён ли аккаунт
        """
        user = Auth.login()
        if input(f"Вы уверены, что хотите удалить аккаунт {user['email']}? (y/n): ") != "y":
            return False
        
        id_token = user['idToken']
        try:
            auth.delete_user_account(id_token)
        except Exception as e:
            print(e)
            return False
        return True
            
    
    @staticmethod
    def login():
        """
        Логинит пользователя запросив email и password.

        Возвращает:
            dict: Данные пользователя {'kind': '...', 'localId': '...', 'email': '...', 'displayName': '...', 
                                'emailVerified': True, 'idToken': '...', 'registered': True, 'refreshToken': '...', 'expiresIn': '...'}
        """
        email, password = Auth._get_emeil_and_password()
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except Exception as e:
            print(e)
            return Auth.login()
        
        return user

    @staticmethod
    def register():
        """
        Регистрирует нового пользователя запросив email и password и подтверждение пароля.

        Возвращает:
            dict: Данные пользователя {'kind': '...', 'localId': '...', 'email': '...', 'displayName': '...', 
                                'emailVerified': True, 'idToken': '...', 'registered': True, 'refreshToken': '...', 'expiresIn': '...'}

        """
        # TODO: Сделать проверку на сложность пароля используя библиотеку passlib или re
        email, password = Auth._get_emeil_and_password(True)
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except Exception as e:
            print(e)
            return Auth.register()
        
        return user