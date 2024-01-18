import getpass
import hashlib
import logging
from pathlib import Path


from cryptography.fernet import Fernet
import pyperclip

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
        username = input("Придумайте логин или используйте /q для выхода: ")
        if username == '/q':
            return
        user = self.db_manager.get_user(username)
        if user:
            print("Данный юзернейм уже занят!")
        else:
            master_password = getpass.getpass("Задайте пароль: ")
            hashed_password = self.hash_password(master_password)
            key = self.generate_key()
            self.db_manager.create_user(username, hashed_password, key)
            print('Аккаунт успешно создан!')

    def login(self):
        login = input("Введите логин или используйте /q для выхода: ")
        if login == '/q':
            return
        master_password = getpass.getpass("Введите пароль: ")
        hashed_password = self.hash_password(master_password)
        user = self.db_manager.check_data(login, hashed_password)
        if user:
            self.select_action(user)
        else:
            print("Неверные данные для входа, попробуйте ещё раз!")
            self.login()

    @staticmethod
    def encrypt_password(password: str, key: bytes) -> bytes:
        encoder = Fernet(key)
        return encoder.encrypt(password.encode())

    @staticmethod
    def decrypt_password(password: str, key: bytes) -> str:
        encoder = Fernet(key)
        return encoder.decrypt(password).decode()

    def add_password(self, user: tuple):
        service_name = input("Введите имя сервиса: ")
        login = input('Введите логин, используемый для сервиса: ')
        is_additional_info = input('Наличие доп. данных? Введите y: ')
        if is_additional_info.lower() == 'y':
            info = input('Введите доп. инфу: ')
        else:
            info = '-'
        is_accepted = input(
            f"Имя сервис: {service_name}\nЛогин: {login}\nДоп. данные: {info}\n"
            "Для подтверждения введите 'y', для выхода /q: "
        )
        if is_accepted.lower() == '/q':
            return
        elif is_accepted.lower() == 'y':
            password = getpass.getpass("Введите пароль: ")
            password2 = getpass.getpass("Повторите пароль: ")
            if password == password2:
                token = self.encrypt_password(password, user[3])
                self.db_manager.add_service(user[0], service_name, login, token, info)
                print('Сервис успешно добавлен!')
                return
            else:
                logging.error("Пароли не похожи, попробуйте заново!")
        print('Операция отклонена!')
        self.add_password(user)

    def select_service(self, user: tuple, action: str):
        services_list = db_mng.get_services_list(user[0])
        text = "-\n".join(row[0] for row in services_list)
        choice = input(f"{text}\nВведите имя сервиса или /q для выхода: ")
        if choice == '/q':
            return
        service_data = db_mng.get_service_data(user[0], choice)
        if service_data:
            if action == '2':
                token = service_data[3]
                key = user[3]
                password = self.decrypt_password(token, key)
                pyperclip.copy(password)
                print(f'Сервис: {service_data[1]}\n'
                      f'Логин: {service_data[2]}\n'
                      f'Доп.инфа: {service_data[4]}\n'
                      f'Ваш пароль скопирован в буфер обмена!')
            elif action == '3':
                self.update_service(service_data)
            else:
                self.delete_service(service_data)
        else:
            print("Сервис с таким именем не найден, попробуйте ещё раз!")
            self.select_service(user, action)

    def generate_password(self, user):
        ...

    def delete_service(self, service):
        ...

    def update_service(self, service):
        ...

    def select_action(self, user: tuple) -> None:
        while True:
            action = input(
                "1.Add\n2.Get\n3.Change\n4.Delete\n5.Generate\n6.Quit\n"
                "Выберите действие: "
            )
            match action:
                case '1': self.add_password(user)
                case '2': self.select_service(user, action)
                case '4': self.generate_password(user)
                case '6': break
                case _: print('Такой команды не существует, попробуйте ещё раз!')

    def main(self):
        while True:
            choice = input(
                "1.Register\n2.Login\n3.Quit\n"
                "Выберите действие: "
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
