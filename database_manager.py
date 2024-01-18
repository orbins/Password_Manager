import sqlite3


class DataBaseManager:
    """Класс для выполнения операций с БД"""

    def __init__(self, db_file):
        self.db_file = db_file

    def connect(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def disconnect(connection):
        connection.commit()
        connection.close()

    def create_database(self):
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
        conn, cursor = self.connect()
        user = cursor.execute(
            """SELECT * FROM users WHERE username = ?""",
            (username,)
        ).fetchone()
        self.disconnect(conn)
        return user

    def create_user(self, username: str, hashed_password: bytes, key: bytes):
        conn, cursor = self.connect()
        cursor.execute(
            """INSERT INTO users (username, password, key)  VALUES (?, ?, ?)""",
            (username, hashed_password, key,)
        )
        self.disconnect(conn)

    def check_data(self, login: str, password: bytes):
        conn, cursor = self.connect()
        user = cursor.execute(
            """SELECT id FROM users WHERE (username = ? AND password = ?)""",
            (login, password)
        ).fetchone()
        self.disconnect(conn)
        return user

    def add_service(self, userid: int, service: str,
                    login: str, password: bytes, info: str):
        conn, cursor = self.connect()
        cursor.execute(
            """INSERT INTO services (userid, service, login, password, info)  VALUES (?, ?, ?, ?, ?)""",
            (userid, service, login, password, info),
        ).fetchone()
        self.disconnect(conn)

    def get_services_list(self, userid: int):
        conn, cursor = self.connect()
        result = cursor.execute(
            """SELECT service FROM services WHERE userid = ?""",
            (userid, )
        ).fetchall()
        self.disconnect(conn)
        return result

    def get_service_data(self, userid: int, service: str):
        conn, cursor = self.connect()
        result = cursor.execute(
            """SELECT * FROM services WHERE (userid = ? AND service = ?)""",
            (userid, service,)
        ).fetchone()
        self.disconnect(conn)
        return result

    def get_user_key(self, userid: int):
        conn, cursor = self.connect()
        result = cursor.execute(
            """SELECT key FROM users WHERE userid = ?""",
            (userid,)
        ).fetchone()
        self.disconnect(conn)
        return result

    def delete_service(self, userid: int, service_name: str):
        conn, cursor = self.connect()
        result = cursor.execute(
            """DELETE FROM services WHERE (userid = ? AND service = ?)""",
            (userid, service_name,)
        ).fetchone()
        self.disconnect(conn)
        return result
