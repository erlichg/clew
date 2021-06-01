"""
This class is just a (very) generic postgres DB interface
It has a singleton patten to be able to access it from all classes and it will generate only once
There are (very) generic methods for fetches and executes
"""
import psycopg2
from psycopg2.extras import DictCursor
import threading

lock = threading.Lock()


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        with lock:
            if not self.instance:
                self.instance = self.klass(*args, **kwds)
            return self.instance


@SingletonDecorator
class DB:
    def setup(self, host, database, user, password):
        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password)
        
    def close(self):
        self.conn.close()

    def fetchone(self, query, args=()):
        curr = self.conn.cursor(cursor_factory=DictCursor)
        curr.execute(query, args)
        ans=curr.fetchone()
        curr.close()
        return ans

    def fetchall(self, query, args=()):
        curr = self.conn.cursor(cursor_factory=DictCursor)
        curr.execute(query, args)
        ans=curr.fetchall()
        curr.close()
        return ans

    def execute(self, command, args=()):
        curr = self.conn.cursor()
        curr.execute(command, args)
        curr.close()
        self.conn.commit()