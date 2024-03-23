import sys
import pytest
from unittest.mock import patch


sys.path.append('src')
from auth import Auth
from firebase import auth

# Фикстура для создания тестовых данных пользователя
@pytest.fixture
def test_user():
    return {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirmed_password': 'testpassword'
    }

# Тестирование регистрации пользователя
@patch('auth.auth.create_user_with_email_and_password')
def test_register(mock_create_user, test_user):
    mock_create_user.return_value = {'localId': '123456'}
    user = Auth.register(test_user['email'], test_user['password'], test_user['confirmed_password'])
    assert user == {'localId': '123456'}
    mock_create_user.assert_called_with(test_user['email'], test_user['password'])

# Тестирование входа пользователя
@patch('auth.auth.sign_in_with_email_and_password')
def test_login(mock_sign_in, test_user):
    mock_sign_in.return_value = {'localId': '123456'}
    user = Auth.login(test_user['email'], test_user['password'])
    assert user == {'localId': '123456'}
    mock_sign_in.assert_called_with(test_user['email'], test_user['password'])

# Тестирование удаления пользователя
@patch('auth.auth.delete_user_account')
@patch('auth.auth.sign_in_with_email_and_password')
def test_delete_user(mock_sign_in, mock_delete_user, test_user, monkeypatch):
    # Макет для ввода пользователем
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    mock_sign_in.return_value = {'localId': '123456', 'idToken': 'test_token'}
    result = Auth.delete_user(test_user['email'], test_user['password'])
    assert result is True
    mock_sign_in.assert_called_with(test_user['email'], test_user['password'])
    mock_delete_user.assert_called_with('test_token')