import scrapy
from scrapy_films.items import MovieItem
from datetime import datetime
import random

class CrawlFilmSpider(scrapy.Spider):
    name = "crawl_film"
    allowed_domains = ["www.allocine.fr"]
    # 111874
    start_id = 111874
    end_id = 700000

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
        'Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0',
    ]

    def start_requests(self):
        # yield scrapy.Request(f"https://www.allocine.fr/film/fichefilm-265358/box-office/", self.parse)
        for i in range(self.start_id, self.end_id):
            user_agent = random.choice(self.USER_AGENTS)
            self.logger.info(f"Current iteration: {i}")
            yield scrapy.Request(f"https://www.allocine.fr/film/fichefilm-{i}/box-office/", self.parse, headers={'User-Agent': user_agent})


    def parse(self, response):
        item = MovieItem()

        entries_one = response.css('.title-punchline+ .section .responsive-table-row:nth-child(1) .col-bg::text').get()
        entries_two = response.css('.title-punchline+ .section .responsive-table-row:nth-child(2) .col-bg::text').get()
        title = response.css('.titlebar-link::text').get()
        box_office_fr = response.css('.title-punchline+ .section .titlebar-title-md::text').get()
        date_str = response.css('.responsive-table-row:nth-child(1) .blue-link::text').get()

        if entries_one and box_office_fr == "Box Office France":
            item['title'] = title
            try:
                entries_one = int(entries_one.replace(" ", ""))
                entries_two = int(entries_two.replace(" ", ""))
                
                if entries_one > entries_two:
                    entries = entries_one
                else:
                    entries = entries_two
                item['entries'] = entries
                self.logger.info(f"Entries found: {entries}")
                self.logger.info(f"Title found: {title}")
                
                if date_str:
                    # Nettoyer la chaîne de caractères
                    date_str = date_str.strip()
                    
                    # Extraire le jour, le mois et l'année
                    date_parts = date_str.split()
                    if len(date_parts) == 7:
                        day1, month, year = date_parts[0], date_parts[1], date_parts[2]
                    elif len(date_parts) == 6:
                        day1, month, year = date_parts[0], date_parts[1], date_parts[5]
                    elif len(date_parts) == 5:
                        day1, month, year = date_parts[0], date_parts[3], date_parts[4]
                    else:
                        self.logger.warning(f"Unexpected date format: {date_str}")
                        return

                    print(day1, month, year)
                    # Convertir le mois en français en numéro de mois
                    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
                    month_number = months.index(month) + 1
                    # Convertir le jour, le mois et l'année en format 'année-mois-jour'
                    date = datetime(int(year), month_number, int(day1))
                    item['date'] = date.strftime('%Y-%m-%d')
                yield item
            except ValueError:
                self.logger.error("Error converting entries to int or date")
        else:
            self.logger.warning("No entries found")