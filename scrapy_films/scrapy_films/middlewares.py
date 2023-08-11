# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ScrapyFilmsSpiderMiddleware:
    # Toutes les méthodes ne doivent pas être définies. Si une méthode n'est pas définie,
    # Scrapy agit comme si le middleware d'araignée ne modifiait pas les objets transmis.


    @classmethod
    def from_crawler(cls, crawler):
        # Cette méthode est utilisée par Scrapy pour créer vos araignées.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Appelé pour chaque réponse qui passe par le middleware d'araignée
        # et entre dans l'araignée.

        # Doit retourner None ou lever une exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Appelé avec les résultats renvoyés par l'araignée, après
        # que celle-ci ait traité la réponse.

        # Doit renvoyer un itérable de requêtes ou d'objets d'éléments.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Appelé lorsqu'une araignée ou la méthode process_spider_input()
        # (d'un autre middleware d'araignée) lève une exception.

        # Doit retourner soit None, soit un itérable de requêtes ou d'objets d'éléments.
        pass

    def process_start_requests(self, start_requests, spider):
        # Appelé avec les requêtes de démarrage de l'araignée, et fonctionne
        # de manière similaire à la méthode process_spider_output(),
        # à l'exception qu'elle n'a pas de réponse associée.

        # Doit renvoyer uniquement des requêtes (pas d'éléments).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapyFilmsDownloaderMiddleware:
    # Toutes les méthodes ne doivent pas être définies. Si une méthode n'est pas définie,
    # Scrapy agit comme si le middleware de téléchargement ne modifiait pas les objets transmis.

    @classmethod
    def from_crawler(cls, crawler):
        # Cette méthode est utilisée par Scrapy pour créer vos araignées.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Appelé pour chaque requête qui passe par le middleware de téléchargement.

        # Doit soit :
        # - renvoyer None : continuer le traitement de cette requête
        # - ou renvoyer un objet Response
        # - ou renvoyer un objet Request
        # - ou lever une IgnoreRequest : les méthodes process_exception()
        #   des middlewares de téléchargement installés seront appelées
        return None

    def process_response(self, request, response, spider):
        # Appelé avec la réponse renvoyée par le téléchargement.

        # Doit soit :
        # - renvoyer un objet Response
        # - renvoyer un objet Request
        # - ou lever une IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Appelé lorsqu'un gestionnaire de téléchargement ou une méthode process_request()
        # (d'un autre middleware de téléchargement) lève une exception.

        # Doit soit :
        # - renvoyer None : continuer le traitement de cette exception
        # - renvoyer un objet Response : arrête la chaîne process_exception()
        # - renvoyer un objet Request : arrête la chaîne process_exception()
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
