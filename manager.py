from getpass import getpass
import hashlib
import logging
from pathlib import Path
import sqlite3

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class PasswordManager:

    def __init__(self):
        self.db_file = Path(__file__).cwd() / "db_file.db"

    @staticmethod
    def hash_password(password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode())
        return sha256.hexdigest()

    def generate_key(self, user):
        key = Fernet.generate_key()

    def register(self):
        try:
            connection = sqlite3.connect("db_file.db")
        except ConnectionError:
            logger.error('Файл базы данных не найден, не удалось установить соединение!')
            return
        cursor = connection.cursor()
        table = cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table' AND name='users'"""
        ).fetchone()
        if table:
            username = input("Придумайте логин: ")
            user = cursor.execute(
                """SELECT * FROM users WHERE username is ?""",
                (username, )
            ).fetchone()
            if user:
                logging.info("Данный юзернейм уже занят!")
                self.register()
            master_password = getpass("Задайте пароль: ")
            hashed_password = self.hash_password(master_password)
            # генерация ключа для шифрования паролей
            cursor.execute(
                """INSERT INTO users (username, password)  VALUES (?, ?)""",
                (username, hashed_password)
            )
            connection.commit()
            connection.close()
            logger.info('Пользователь успешно создан!')
        else:
            logging.error('В файле БД отсутствует таблица с пользователями!')

    def login(self):
        try:
            connection = sqlite3.connect("db_file.db")
        except ConnectionError:
            logger.error('Файл базы данных не найден, не удалось установить соединение!')
            return
        cursor = connection.cursor()
        table = cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table' AND name='users'"""
        ).fetchone()
        if table:
            login = input("Введите логин: ")
            master_password = getpass("Введите пароль: ")
            hashed_password = self.hash_password(master_password)
            user = cursor.execute(
                """SELECT * FROM users WHERE (username is ?, password is ?)""",
                (login, hashed_password)
            ).fetchone()
            connection.close()
            logging.info(f'user: {user}')
            if user:
                self.select_action(user)
            else:
                logging.warning("Неверные данные для входа, попробуйте ещё раз!")
                self.login()
        else:
            logging.error('В файле БД отсутствует таблица с пользователями!')

    def encrypt_password(self, password):
        ...

    def add_password(self, user):
        try:
            connection = sqlite3.connect("db_file.db")
        except ConnectionError:
            logger.error('Файл базы данных не найден, не удалось установить соединение!')
            return
        cursor = connection.cursor()
        table = cursor.execute(
            """
            SELECT name FROM sqlite_master WHERE type='table' AND name='passwords'
            """
        ).fetchone()
        if table:
            service_name = input("Введите имя сервиса: ")
            login = input('Введите логин: ')
            is_additional_info = input('Наличие доп. данных? Введите y: ')
            if is_additional_info.lower() == 'y':
                info = input('Введите доп. инфу: ')
            is_accepted = input(f"Имя сервис: {service_name}\nЛогин: {login}\nДоп. данные: {info}. Подтвердить y/n: ")
            if is_accepted.lower() == 'y':
                password = getpass("Введите пароль: ")
                password2 = getpass("Повторите пароль: ")
                if password == password2:
                    encrypted = self.encrypt_password(password)
                else:
                    logging.error("Пароли не похожи, попробуйте заново!")
                    self.add_password(user)
            else:
                self.add_password(user)
        else:
            logging.error('В файле БД отсутствует таблица с паролями!')

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
        if self.db_file.exists():
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
        else:
            logging.error('Не удалось найти файл базы данных!')


if __name__ == '__main__':
    manager = PasswordManager()
    manager.main()
