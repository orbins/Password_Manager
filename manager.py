from getpass import getpass
import logging
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class PasswordManager:

    def __init__(self):
        self.db_file = Path(__file__).cwd() / "passwords.db"

    def add_password(self):
        try:
            connection = sqlite3.connect("passwords.db")
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
                    ...
                else:
                    logging.error("Пароли не похожи, попробуйте заново!")
                    self.add_password()
            else:
                self.add_password()
        else:
            logging.error('В файле БД отсутствует таблица с паролями!')

    def select_service(self):
        ...

    def generate_password(self):
        ...

    def main(self):
        if self.db_file.exists():
            action = input(
                "Выберите действие: " 
                "\n1.Add\n2.Copy\n3.Change\n4.Generate"
            )
            match action.lower():
                case 'add': self.add_password()
                case 'copy', 'change': self.select_service()
                case 'generate': self.generate_password()
        else:
            logging.error('Не удалось найти файл базы данных!')


if __name__ == '__main__':
    manager = PasswordManager()
    manager.main()
