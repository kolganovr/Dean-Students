import pyrebase
from cfg import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()