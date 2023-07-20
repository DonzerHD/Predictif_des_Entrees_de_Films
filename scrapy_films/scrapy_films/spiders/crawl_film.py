import scrapy
from scrapy_films.items import MovieItem
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import random
from colorama import Fore, Style

class CrawlFilmSpider(scrapy.Spider):
    name = "crawl_film"
    allowed_domains = ["www.allocine.fr"]

    # Liste des user agents
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    ]

    # Générer dynamiquement les URLs de départ
    start_urls = []
    start_date = datetime(2005, 1,5)  # Date de début
    end_date = datetime(2023, 7, 5)  # Date de fin
    week_delta = timedelta(days=7)  # Intervalle de temps (une semaine)

    current_date = start_date
    while current_date <= end_date:
        # Ajouter l'URL à la liste des URLs de départ
        start_urls.append(f"https://www.allocine.fr/boxoffice/france/sem-{current_date.strftime('%Y-%m-%d')}/")
        # Passer à la semaine suivante
        current_date += week_delta

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers={'User-Agent': random.choice(self.USER_AGENTS)})

    def parse(self, response):
        movie_rows = response.css('.responsive-table-row')  # Récupérer toutes les lignes de films

        for row in movie_rows:
            semaine = row.css("td[data-heading='Semaine']::text").get()  # Récupérer la valeur de la semaine
            if semaine and semaine.strip() == "1":
                item = MovieItem()
                item['title'] = row.css('.meta-title-link::text').get()  # Titre du film
                item['entries'] = row.css('strong::text').get()  # Entrées du film
                
                
                # Extraire la date de l'URL
                parsed_url = urlparse(response.url)
                date_str = parsed_url.path.split('/')[-2]  # La date se trouve dans le chemin de l'URL
                date_str = date_str.replace('sem-', '')  # Enlever 'sem-' de la chaîne de date
                try:
                    item['date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    print(Fore.RED + f"Invalid date format in URL: {response.url}" + Style.RESET_ALL)
                    continue


                print(Fore.GREEN + f"Title: {item['title']}, Entries: {item['entries']}, Date: {item['date']}" + Style.RESET_ALL)

                yield item