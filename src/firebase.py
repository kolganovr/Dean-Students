import pyrebase
try:
    from cfg import firebaseConfig
except ImportError:
    raise Exception("Файл cfg.py необходимый для работы приложения не найден!")

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()