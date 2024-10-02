import scrapy
from datetime import date

# Anleitung auf: https://www.pluralsight.com/guides/crawling-web-python-scrapy
# Dis ist nur ein Test-Datei, kein funktionierender Spyder!!
# Web-Scraping Verkaufspreise Wohnungen Schweiz/FL

class ScoutSpider(scrapy.Spider):
    name = 'scout'
    start_urls = ['https://www.immoscout24.ch/de/wohnung/kaufen/land-schweiz-fl?pn=1']
    allowed_domains = ['www.immoscout24.ch']
    page_number = 1
    """
    custom_settings = {
        'FEEDS': {'./output/appartements_1.csv': {'format': 'csv',}, 'overwrite': False,
                  'encoding': 'utf8'}
    }
    """

    def parse(self, response):

        for article in response.css('article'):
            try:
                try:
                    Wohnungsart = article.css('span.Box-cYFBPY.Badge__StyledBadge-bJJanS.kQjLxE.fdYwUL::text').getall()[0]
                except:
                    Wohnungsart = 'n/a'
                try:
                    Zimmeranzahl = article.css('h3.Box-cYFBPY::text').extract()[0].strip()
                except:
                    Zimmeranzahl = 'n/a'
                try:
                    Wohnungsgroesse_m2 = article.css('h3.Box-cYFBPY::text').extract()[2].strip(),
                except:
                    Wohnungsgroesse_m2 = 'n/a'
                try:
                    Verkaufspreis = article.css('h3.Box-cYFBPY > span::text').extract()[0].strip(),
                except:
                    Verkaufspreis = 'n/a'
                try:
                    Wohnungsadresse = article.css('span.AddressLine__TextStyled-eaUAMD::text').extract()[0],
                except:
                    Wohnungsadresse = 'n/a'
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

        next_page = 'https://www.immoscout24.ch/de/wohnung/kaufen/land-schweiz-fl?pn=' + str(ScoutSpider.page_number)
        if ScoutSpider.page_number <= 13:
            ScoutSpider.page_number += 1
            yield response.follow(next_page, callback = self.parse)



# Scrapy starten und Resultate in csv schreiben (-o fügt hinzu, -O überschreibt)
#Shell: scrapy runspider webscraping\webscraping\spiders\scout_test.py -t csv -o ./output/appartements_1.csv