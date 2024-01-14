from getpass import getpass
import hashlib
import logging
from pathlib import Path
import sqlite3

from cryptography.fernet import Fernet

from database_manager import DataBaseManager

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class PasswordManager:

    def __init__(self, db_manager):
        self.db_manager = db_manager

    @staticmethod
    def hash_password(password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode())
        return sha256.hexdigest()

    @staticmethod
    def generate_key():
        key = Fernet.generate_key()
        return key

    def register(self):
        username = input("Придумайте логин: ")
        user = self.db_manager.get_user(username)
        if user:
            print("Данный юзернейм уже занят!")
        else:
            master_password = getpass("Задайте пароль: ")
            hashed_password = self.hash_password(master_password)
            key = self.generate_key()
            self.db_manager.create_user(username, hashed_password, key)
            print('Аккаунт успешно создан!')

    def login(self):
        login = input("Введите логин: ")
        master_password = getpass("Введите пароль: ")
        hashed_password = self.hash_password(master_password)
        user = self.db_manager.check_data(login, hashed_password)
        print(f'user: {user}')
        if user:
            self.select_action(user)
        else:
            print("Неверные данные для входа, попробуйте ещё раз!")
            self.login()

    @staticmethod
    def encrypt_password(password, user):
        key = user[3]
        encoder = Fernet(key)
        return encoder.encrypt(password)

    def add_password(self, user):
        service_name = input("Введите имя сервиса: ")
        login = input('Введите логин, используемый для сервиса: ')
        is_additional_info = input('Наличие доп. данных? Введите y: ')
        if is_additional_info.lower() == 'y':
            info = input('Введите доп. инфу: ')
        else:
            info = '-'
        is_accepted = input(
            f"Имя сервис: {service_name}\nЛогин: {login}\nДоп. данные: {info}\n"
            "Для подтверждения введите 'y', иначе операция будет отклонена"
        )
        if is_accepted.lower() == 'y':
            password = getpass("Введите пароль: ")
            password2 = getpass("Повторите пароль: ")
            if password == password2:
                encrypted = self.encrypt_password(password, user)
                self.db_manager.add_service(user[0], service_name, login, encrypted, info)
                return
            else:
                logging.error("Пароли не похожи, попробуйте заново!")
        self.add_password(user)

    def select_service(self, user):
        ...

    def generate_password(self, user):
        ...

    def delete_service(self, user):
        ...

    def select_action(self, user):
        while True:
            action = input(
                "Выберите действие: " 
                "\n1.Add\n2.Copy\n3.Change\n4.Generate\n5.Delete\n6.Quit"
            )
            match action.lower():
                case '1': self.add_password(user)
                case '2', '3': self.select_service(user)
                case '4': self.generate_password(user)
                case '5': self.delete_service(user)
                case _: break

    def main(self):
        while True:
            choice = input(
                "Выберите действие: "
                "\n1.Register\n2.Login\n3.Quit"
            )
            if choice == '1':
                self.register()
            elif choice == '2':
                self.login()
            elif choice == '3':
                break
            else:
                print('Такой команды не существует!')


if __name__ == '__main__':
    file = Path(__file__).cwd() / "db_file.db"
    db_mng = DataBaseManager(file)
    if not file.exists():
        db_mng.create_database()
    manager = PasswordManager(db_mng)
    manager.main()
