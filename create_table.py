from psycopg2 import pool

# CREATING A CONNECTION POOL CLASS

connection_pool = pool.SimpleConnectionPool(
    1, 1, database="flask", user="postgres", password="Abraham1990", host="localhost"
)


class Database:
    __connection_pool = None  # PRIVATE VARIABLES

    @classmethod
    def initialise(cls, **kwargs):  # PASSING KEYWORD ARGUMENTS
        Database.__connection_pool = pool.SimpleConnectionPool(1, 1, **kwargs)

    @classmethod
    def get_connection(cls):
        # you may either use cls. or Database.
        return cls.__connection_pool.getconn()

    @classmethod
    def put_connection(cls, connection):
        # you may either use cls. or Database.
        return cls.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        # you may either use cls. or Database.
        return cls.__connection_pool.closeall()


class CursorFromConnectionFromPool:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        # self.connection = connection_pool.getconn()
        self.connection = Database().get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):  # EXCEPTION AND CONNECTION ROLL BACK
        if exc_type is not None:  # e.g. TypeError, AttributeError, ValueError
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
            # connection_pool.putconn(self.connection)
            Database().put_connection(self.connection)


def create_table(self):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS confirmations (id INTEGER PRIMARY KEY, name text, price real)"
        )


def save_2_db(self):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(
            "INSERT INTO users(email, first_name, last_name) VALUES(%s, %s, %s)",
            (self.email, self.first_name, self.last_name),
        )


def load_from_db_by_email(email):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))  # TUPLE
        data = cursor.fetchall()
        return data


def random(email):
    with CursorFromConnectionFromPool() as cursor:
        user = ("ayo", "abc123")
        # insert_query = "INSERT INTO users VALUES(?, ?, ?)"
        insert_query = "INSERT INTO users(id, username, password) VALUES(NULL, ?, ?)"
        cursor.execute(insert_query, user)

        users = [("rotimi", "abc123"), ("seun", "abc123"), ("abraham", "abc123")]

        cursor.executemany(insert_query, users)

        select_query = "SELECT * FROM users"

        for row in cursor.execute(select_query):
            print(row)

        username = ("seun",)
        select_by_username = "SELECT * FROM users WHERE username = ?"
        user_data = cursor.execute(select_by_username, username)
        for row_data in user_data:
            print(row_data)
