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

    def get_user(self, username):
        conn, cursor = self.connect()
        user = cursor.execute(
            """SELECT * FROM users WHERE username is ?""",
            (username,)
        ).fetchone()
        self.disconnect(conn)
        return user

    def create_user(self, username, hashed_password, key):
        conn, cursor = self.connect()
        cursor.execute(
            """INSERT INTO users (username, password, key)  VALUES (?, ?, ?)""",
            (username, hashed_password, key),
        )
        self.disconnect(conn)

    def check_data(self, login, password):
        conn, cursor = self.connect()
        user = cursor.execute(
            """SELECT * FROM users WHERE (username is ?, password is ?)""",
            (login, password)
        ).fetchone()
        self.disconnect(conn)
        return user

    def add_service(self, userid, service, login, password, info):
        conn, cursor = self.connect()
        cursor.execute(
            """INSERT INTO services (userid, service, login, password, info)  VALUES (?, ?, ?, ?, ?)""",
            (userid, service, login, password, info),
        ).fetchone()
        self.disconnect(conn)