import scrapy
from datetime import date

# Anleitung auf: https://www.pluralsight.com/guides/crawling-web-python-scrapy
# Web-Scraping Verkaufspreise Wohnungen Schweiz/FL

class ScoutSpider(scrapy.Spider):
    name = 'scout'
    start_urls = ['https://www.immoscout24.ch/de/wohnung/kaufen/land-schweiz-fl?pn=1']
    allowed_domains = ['www.immoscout24.ch']
    page_number = 1
    custom_settings = {
        'FEEDS': {'./output/appartements_bereinigt.csv': {
            'format': 'csv', 'encoding': 'utf8', 'overwrite': False,
        }}
    }


# css-response angepasst auf aktuelle Webseite von immoscout am 29.09.2024
    def parse(self, response):

        for article in response.css('.ResultList_listItem_j5Td_'):
            try:
                try:
                    # Wohnungsart = article.css('span.Box-cYFBPY.Badge__StyledBadge-bJJanS.kQjLxE.fdYwUL::text').getall()[0]
                    Wohnungsart = article.css('div.HgNewConstructionBadge_newConstructionBadgeContainer_Ivd9x > span::text').getall()[0],
                except:
                    Wohnungsart = 'unbekannt'
                try:
                    # Zimmeranzahl = article.css('h3.Box-cYFBPY::text').extract()[0].strip()
                    Zimmeranzahl = article.css('div.HgListingCard_mainTitle_x0p2D > div > strong:nth-child(1)::text').extract()[0].strip(),
                except:
                    Zimmeranzahl = 'unbekannt'
                try:
                    # Wohnungsgroesse_m2 = article.css('h3.Box-cYFBPY::text').extract()[2].strip(),
                    Wohnungsgroesse_m2 = article.css('div.HgListingCard_mainTitle_x0p2D > div > strong:nth-child(3)::text').extract()[0].strip(),
                except:
                    Wohnungsgroesse_m2 = 'unbekannt'
                try:
                    # Verkaufspreis = article.css('h3.Box-cYFBPY > span::text').extract()[0].strip(),
                    Verkaufspreis = article.css('span.HgListingRoomsLivingSpacePrice_price_u9Vee::text').extract()[0].strip(),
                except:
                    Verkaufspreis = 'unbekannt'
                try:
                    # Wohnungsadresse = article.css('span.AddressLine__TextStyled-eaUAMD::text').extract()[0],
                    Wohnungsadresse = article.css('div.HgListingCard_secondaryTitle_uVla3 > div > address::text').extract()[0],
                except:
                    Wohnungsadresse = 'unbekannt'
                    # 'Seitenzahl': response.css('a.Box-cYFBPY PseudoBox-fXdOzA Shell-fTlxHA dxURpc gVespY gfKtRI::attribut(int)').extract(),
                    # 'Wohnungs_Beschrieb': article.css('p.Box-cYFBPY.wYYQQ::text').extract()[0],
                    # result['Nähester_Bahnhof'] = response.css('span.PersonalPOI').extract()
                yield {
                        'Datum': date.today().strftime('%Y-%m-%d'),
                        'Wohnungsart': Wohnungsart,
                        'Zimmeranzahl': Zimmeranzahl,
                        'Wohnungsgrösse_m2': Wohnungsgroesse_m2,
                        'Verkaufspreis': Verkaufspreis,
                        'Wohnungs_Adresse': Wohnungsadresse
                }
            except:
                print(f'Crawling {article} fehlgeschlagen')

            ScoutSpider.page_number = max(ScoutSpider.page_number, 2)  # Sicherstellen, dass die Seitenzahl mindestens 2 ist
            next_page = 'https://www.immoscout24.ch/de/wohnung/kaufen/land-schweiz-fl?pn=' + str(
                ScoutSpider.page_number)
            if ScoutSpider.page_number <= 60:
                ScoutSpider.page_number += 1
                yield response.follow(next_page, callback=self.parse)

""""
def parse(self, response):
    for article in response.css('article'):
        try:
            # Wohnungsart
            Wohnungsart = article.css('span.Badge__StyledBadge-bJJanS.kQjLxE::text').get(default='unbekannt')

            # Zimmeranzahl
            Zimmeranzahl = article.css('h3.Box-cYFBPY::text').get(default='unbekannt').strip()

            # Wohnungsgröße (m²)
            Wohnungsgroesse_m2 = article.css('span.Box-cYFBPY::text').get(
                default='unbekannt').strip()  # Stelle sicher, dass der korrekte Index verwendet wird

            # Verkaufspreis
            Verkaufspreis = article.css('h3.Box-cYFBPY > span::text').get(default='unbekannt').strip()

            # Wohnungsadresse
            Wohnungsadresse = article.css('span.AddressLine__TextStyled-eaUAMD::text').get(default='unbekannt')

            yield {
                'Datum': date.today().strftime('%Y-%m-%d'),
                'Wohnungsart': Wohnungsart,
                'Zimmeranzahl': Zimmeranzahl,
                'Wohnungsgröße_m2': Wohnungsgroesse_m2,
                'Verkaufspreis': Verkaufspreis,
                'Wohnungs_Adresse': Wohnungsadresse
            }
        except Exception as e:
            self.logger.error(f'Crawling {article} fehlgeschlagen: {e}')
"""



# Scrapy starten und Resultate in csv schreiben (-o fügt hinzu, -O überschreibt => -t csv -o ./output/appartements_bereinigt.csv)
#Shell Spider laufen lassen => scrapy runspider webscraping\webscraping\spiders\scout_final.py