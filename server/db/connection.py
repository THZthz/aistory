import psycopg2


class ConnectionSingletonClass(object):
    instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance') or cls.instance is None:
            cls.instance = super(ConnectionSingletonClass, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="aistory",
            user="postgres",
            password="123456",
            host="localhost",
            port="5433") # To use pgvector extension, PostgreSQL 16 must be used.


class Connection(ConnectionSingletonClass):
    pass

