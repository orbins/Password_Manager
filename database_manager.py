import sqlite3


class DataBaseManager:
    """Класс для выполнения операций с БД"""

    def __init__(self, db_file):
        self.db_file = db_file

    def connect(self):
        """Подключение к базе"""
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def disconnect(connection):
        """Отключение соединения с базой"""
        connection.commit()
        connection.close()

    def create_database(self):
        """Создание БД"""
        conn, cursor = self.connect()

        cursor.execute(
            '''
            CREATE TABLE "users" (
            "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            "username" TEXT NOT NULL,
            "password" BLOB NOT NULL,
            "key" BLOB NOT NULL
            );
            '''
        )

        cursor.execute(
            '''
            CREATE TABLE "services" (
            "userid" INT NOT NULL,
            "service" TEXT NOT NULL,
            "login" TEXT NOT NULL,
            "password" BLOB NOT NULL,
            "info" TEXT NULL,
            CONSTRAINT fk_users
            FOREIGN KEY ("userid")
            REFERENCES users(id)
            );
            '''
        )

        self.disconnect(conn)

    def get_user(self, username: str):
        """Получение пользователя по урлу"""
        conn, cursor = self.connect()
        user = cursor.execute(
            """SELECT * FROM users WHERE username = ?""",
            (username,)
        ).fetchone()
        self.disconnect(conn)
        return user

    def create_user(self, username: str, hashed_password: bytes, key: bytes):
        """Создание пользователя"""
        conn, cursor = self.connect()
        cursor.execute(
            """INSERT INTO users (username, password, key)  VALUES (?, ?, ?)""",
            (username, hashed_password, key,)
        )
        self.disconnect(conn)

    def check_data(self, login: str, password: bytes):
        """Проверка подлинности учётных данных"""
        conn, cursor = self.connect()
        user = cursor.execute(
            """SELECT id FROM users WHERE (username = ? AND password = ?)""",
            (login, password)
        ).fetchone()
        self.disconnect(conn)
        return user

    def add_service(self, userid: int, service: str,
                    login: str, password: bytes, info: str):
        """Добавление нового сервиса пользователя"""
        conn, cursor = self.connect()
        cursor.execute(
            """INSERT INTO services (userid, service, login, password, info)  VALUES (?, ?, ?, ?, ?)""",
            (userid, service, login, password, info),
        ).fetchone()
        self.disconnect(conn)

    def get_services_list(self, userid: int):
        """Получение всех сервисов конкретного пользователя"""
        conn, cursor = self.connect()
        result = cursor.execute(
            """SELECT service FROM services WHERE userid = ?""",
            (userid, )
        ).fetchall()
        self.disconnect(conn)
        return result

    def get_service_data(self, userid: int, service: str):
        """Получение конкретного сервиса пользователя"""
        conn, cursor = self.connect()
        result = cursor.execute(
            """SELECT * FROM services WHERE (userid = ? AND service = ?)""",
            (userid, service,)
        ).fetchone()
        self.disconnect(conn)
        return result

    def get_user_key(self, userid: int):
        """Получение ключа шифрования для пользователя"""
        conn, cursor = self.connect()
        result = cursor.execute(
            """SELECT key FROM users WHERE id = ?""",
            (userid,)
        ).fetchone()
        self.disconnect(conn)
        return result

    def delete_service(self, userid: int, service_name: str):
        """Удаление сервиса пользователя"""
        conn, cursor = self.connect()
        result = cursor.execute(
            """DELETE FROM services WHERE (userid = ? AND service = ?)""",
            (userid, service_name,)
        ).fetchone()
        self.disconnect(conn)
        return result

    def update_service(self, userid: int, updated_service: str, service: str,
                       login: str, password: bytes, info: str):
        """Изменение данных о серисе пользователя"""
        conn, cursor = self.connect()
        cursor.execute(
            """UPDATE services SET service = ?, login = ?, password = ?, info = ? WHERE (userid = ? AND service = ?) """,
            (service, login, password, info, userid, updated_service),
        ).fetchone()
        self.disconnect(conn)
