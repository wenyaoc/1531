import psycopg2
from time import sleep

HOST = 'csproject1.cclytslickfz.ap-southeast-2.rds.amazonaws.com'
USER = 'seulgi'
PASSWORD = 'seulgiseulgi'
DATABASE = 'cs1531'
PORT = '5432'


# psycopg2.connect\
#    (user=user, password=password, host=host, port=port, database=database, ssl_mode=ssl_mode)


class DbConnector:
    def __init__(self):
        self.user = USER
        self.password = PASSWORD
        self.host = HOST
        self.port = PORT
        self.database = DATABASE
        self._connection = None
        self._cursor = None

    def connect(self, counter_reconnect=0):
        try:
            self._connection = psycopg2.connect(user=self.user,
                                                password=self.password,
                                                port=self.port,
                                                dbname=self.database,
                                                host=self.host)
            counter_reconnect = 0
        except psycopg2.OperationalError as error:
            if counter_reconnect > 4:
                raise error
            else:
                counter_reconnect += 1
                sleep(5)
                self.connect(counter_reconnect)

        return self._connection

    def cursor(self):
        self.connect()
        self._cursor = self._connection.cursor()

        return self._cursor

    def execute(self, query, *args, **kwargs):
        try:
            self._cursor.execute(query, *args, **kwargs)
            self._connection.commit()
        except psycopg2.Error as error:
            self._connection.rollback()
            raise error

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        self._cursor.close()
        self._connection.close()


db_connect = DbConnector()

if __name__ == '__main__':
    db_connect1 = DbConnector()
    a = db_connect.connect()
    b = DbConnector()
