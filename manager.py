import getpass
import hashlib
import logging
from pathlib import Path
import re
import secrets
import string

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
            print("Данный юзернейм уже занят!\n")
        else:
            master_password = getpass.getpass("Задайте пароль: ")
            hashed_password = self.hash_password(master_password)
            key = self.generate_key()
            self.db_manager.create_user(username, hashed_password, key)
            print('Аккаунт успешно создан!\n')

    def login(self):
        login = input("Введите логин или используйте /q для выхода: ")
        if login == '/q':
            return
        master_password = getpass.getpass("Введите пароль: ")
        hashed_password = self.hash_password(master_password)
        uid_tuple = self.db_manager.check_data(login, hashed_password)
        if uid_tuple:
            self.select_action(uid_tuple[0])
        else:
            print("Неверные данные для входа, попробуйте ещё раз!\n")
            self.login()

    @staticmethod
    def encrypt_password(password: str, key: bytes) -> bytes:
        encoder = Fernet(key)
        return encoder.encrypt(password.encode())

    @staticmethod
    def decrypt_password(password: str, key: bytes) -> str:
        encoder = Fernet(key)
        return encoder.decrypt(password).decode()

    def add_password(self, userid: int, updated_service: str = None):
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
                key = self.db_manager.get_user_key(userid)[0]
                token = self.encrypt_password(password, key)
                if updated_service:
                    self.db_manager.update_service(userid, updated_service,
                                                   service_name, login, token, info)
                else:
                    self.db_manager.add_service(userid, service_name, login, token, info)
                print('Данные сохранены!\n')
                return
            else:
                logging.error("Пароли не похожи, попробуйте заново!\n")
        print('Операция отклонена!\n')
        self.add_password(userid)

    def select_service(self, userid: int, action: str):
        services_list = db_mng.get_services_list(userid)
        text = "-\n".join(row[0] for row in services_list)
        choice = input(f"Список ваших сервисов:\n{text}\nВведите имя сервиса или /q для выхода: ")
        if choice == '/q':
            return
        service_data = db_mng.get_service_data(userid, choice)
        if service_data:
            if action == '2':
                token = service_data[3]
                key = self.db_manager.get_user_key(userid)[0]
                password = self.decrypt_password(token, key)
                pyperclip.copy(password)
                print(f'Сервис: {service_data[1]}\n'
                      f'Логин: {service_data[2]}\n'
                      f'Доп.инфа: {service_data[4]}\n'
                      f'Ваш пароль скопирован в буфер обмена!\n')
            elif action == '3':
                self.add_password(userid, service_data[1])
            else:
                self.db_manager.delete_service(userid, service_data[1])
                print('Сервис успешно удалён!\n')
        else:
            print("Сервис с таким именем не найден, попробуйте ещё раз!\n")
            self.select_service(userid, action)

    def generate_password(self):
        print('Укажите длину пароля, не менее 6 символов и не более 20: ')
        length = input("Для выхода введите /q: ")
        if length == '/q':
            return
        if length.isdigit() and (6 <= int(length) <= 20):
            alphabet = string.ascii_letters + string.digits + string.punctuation
            while True:
                password = ''.join(secrets.choice(alphabet) for i in range(int(length)))
                pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_])[a-zA-Z\d\W_]{6,20}$'
                if re.match(pattern, password):
                    break
            pyperclip.copy(password)
            print('Сгенерированный пароль скопирован в буфер обмена!')
            return
        print('Длина пароля должна соответствовать условиям!')
        self.generate_password()

    def select_action(self, userid: int) -> None:
        while True:
            action = input(
                "1.Add\n2.Get\n3.Change\n4.Delete\n5.Generate\n6.Quit\n"
                "Выберите действие: "
            )
            match action:
                case '1': self.add_password(userid)
                case '2' | '3' | '4': self.select_service(userid, action)
                case '5': self.generate_password()
                case '6': break
                case _: print('Такой команды не существует, попробуйте ещё раз!\n')

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
                print('Такой команды не существует!\n')


if __name__ == '__main__':
    file = Path(__file__).cwd() / "db_file.db"
    db_mng = DataBaseManager(file)
    if not file.exists():
        db_mng.create_database()
    manager = PasswordManager(db_mng)
    manager.main()
