import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn_str = os.getenv("DATABASE_URL")
        if not self.conn_str:
            raise ValueError("DATABASE  URL not found in environment variables")
        self.conn = None

    def connect(self):
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(self.conn_str)
        return self.conn

    def execute(self, query, params=None, fetch=False):
        conn = self.connect()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
            return None

    def close(self):
        if self.conn:
            self.conn.close()
