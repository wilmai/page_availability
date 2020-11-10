from psycopg2.extras import RealDictCursor
import psycopg2

from .page_request_result import PageRequestResult


class PageDatabase:

    # static query strings
    table_create = """CREATE TABLE PAGE_AVAILABILITY(
        ID SERIAL PRIMARY KEY,
        URL TEXT NOT NULL,
        STATUS INT NOT NULL,
        REQUEST_TIME TIMESTAMP NOT NULL,
        REQUEST_DURATION REAL NOT NULL,
        CONTENT_REGEX TEXT,
        CONTENT_MATCHED BOOLEAN,
        ERROR TEXT
    );"""
    table_insert = """INSERT INTO PAGE_AVAILABILITY(
        URL,STATUS,CONTENT_REGEX,CONTENT_MATCHED,REQUEST_TIME,REQUEST_DURATION,ERROR
    ) VALUES (
        %s,%s,%s,%s,%s,%s,%s
    );"""
    table_tail = """SELECT * FROM PAGE_AVAILABILITY ORDER BY ID DESC LIMIT %s;"""

    def __init__(self, uri, create_table=False):
        self.uri = uri
        self.conn = psycopg2.connect(uri)
        if create_table:
            c = self.conn.cursor(cursor_factory=RealDictCursor)
            c.execute(PageDatabase.table_create)
            self.conn.commit()
            c.close()

    def insert(self, results) -> None:
        # accept iterable or single object of type PageRequestResult
        try:
            itr = iter(results)
        except:
            lst = [results]
            itr = iter(lst)

        c = self.conn.cursor(cursor_factory=RealDictCursor)
        for res in itr:
            c.execute(PageDatabase.table_insert, (res.url, res.status, res.text_regex, res.text_matched,
                res.request_time, res.request_duration, res.error))
        self.conn.commit()
        c.close()

    def query(self, limit=1):
        c = self.conn.cursor(cursor_factory=RealDictCursor)
        c.execute(PageDatabase.table_tail, (limit,))
        rows = c.fetchall()
        c.close()
        return rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
