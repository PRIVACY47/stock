from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import pypyodbc
from .imp_info import DATABASE_UID, DATABASE_PWD,DB_SERVER,DB_NAME
import bcrypt
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        conn = pypyodbc.connect(
            'Driver={SQL Server};'
            f'Server={DB_SERVER};'
            f'Database={DB_NAME};'
            f'uid={DATABASE_UID};'
            f'pwd={DATABASE_PWD}'
        )

        cursor = conn.cursor()
        print(cursor)
        query = "SELECT * FROM user_man WHERE userid = ?"
        cursor.execute(query, (username,))

        result = cursor.fetchone()
        print(result)
        if result is not None:
            # Verify the password
            hashed_password = result[2]  # replace with the index of the password in your result
            print(verify_password(password, hashed_password))
            if verify_password(password, hashed_password):
                # If the password is correct, get or create a Django user
                print("in user")
                User = get_user_model()
                print(User)
                user, created = User.objects.get_or_create(username=username)
                print(user)
                return user
        cursor.close()
        conn.close()
        # If the username or password is incorrect, return None
        return None
