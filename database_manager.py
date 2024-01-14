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