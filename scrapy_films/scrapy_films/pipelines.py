# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapyFilmsPipeline:
    def process_item(self, item, spider):
        return item


import pyodbc
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the current path
current_path = Path(os.getcwd())

# Define the path to the .env file
env_path = current_path.parent / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

class SqlServerPipeline(object):

    def open_spider(self, spider):
        self.connection = pyodbc.connect(f'DRIVER={os.getenv("DB_DRIVER")};SERVER={os.getenv("DB_SERVER")};DATABASE={os.getenv("DB_DATABASE")};UID={os.getenv("DB_UID")};PWD={os.getenv("DB_PWD")},')
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
