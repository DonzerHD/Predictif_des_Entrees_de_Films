import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

class SqlServerPipeline(object):

    def open_spider(self, spider):
        self.connection = pyodbc.connect(f'DRIVER={"ODBC Driver 18 for SQL Server"};SERVER={os.getenv("DB_SERVER")};DATABASE={os.getenv("DB_DATABASE")};UID={os.getenv("DB_UID")};PWD={os.getenv("DB_PWD")}')
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.cursor.execute("""
            INSERT INTO dbo.film_scrapy (title, entries, date)
            VALUES (?, ?, ?)
        """, (item['title'], item['entries'], item['date']))
        self.connection.commit()
        return item
