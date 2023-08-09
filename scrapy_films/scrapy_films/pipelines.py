# Importer les bibliothèques nécessaires
from dotenv import load_dotenv
import os
import pyodbc

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()  # Prend les variables d'environnement à partir du fichier .env.

class SqlServerPipeline(object):
    """
    Un pipeline pour le web scraping de films vers une base de données SQL Server.
    """

    def open_spider(self, spider):
        """
        Ouvre la connexion à la base de données SQL Server.

        Parameters:
        spider (scrapy.Spider): L'araignée de scraping en cours d'exécution.
        """
        self.connection = pyodbc.connect(
            f'DRIVER={"ODBC Driver 18 for SQL Server"};SERVER={os.getenv("DB_SERVER")};DATABASE={os.getenv("DB_DATABASE")};UID={os.getenv("DB_UID")};PWD={os.getenv("DB_PWD")}'
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        """
        Ferme la connexion à la base de données SQL Server.

        Parameters:
        spider (scrapy.Spider): L'araignée de scraping en cours d'exécution.
        """
        self.connection.close()

    def process_item(self, item, spider):
        """
        Insère les données extraites dans la table "film_scrapy" de la base de données.

        Parameters:
        item (dict): Les données extraites de l'araignée.
        spider (scrapy.Spider): L'araignée de scraping en cours d'exécution.

        Returns:
        dict: Les données extraites inchangées.
        """
        self.cursor.execute(
            """
            INSERT INTO dbo.film_scrapy (title, entries, date)
            VALUES (?, ?, ?)
            """,
            (item['title'], item['entries'], item['date'])
        )
        self.connection.commit()
        return item


