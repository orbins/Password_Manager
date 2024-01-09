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

    def check_db_file(self):
        ...

    def add_password(self):
        ...

    def select_service(self):
        ...

    def generate_password(self):
        ...

    def main(self):
        self.check_db_file()
        action = input(
            "Выберите действие:" 
            "\n1.Add\n2.Copy\n3.Change\n4.Generate"
        )
        match action.lower():
            case 'add': self.add_password()
            case 'copy', 'change': self.select_service()
            case 'generate': self.generate_password()


if __name__ == '__main__':
    manager = PasswordManager()
    manager.main()
