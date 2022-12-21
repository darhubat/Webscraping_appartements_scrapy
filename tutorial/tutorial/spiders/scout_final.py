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


    def parse(self, response):

        for article in response.css('article'):
            try:
                try:
                    Wohnungsart = article.css('span.Box-cYFBPY.Badge__StyledBadge-bJJanS.kQjLxE.fdYwUL::text').getall()[0]
                except:
                    Wohnungsart = 'unbekannt'
                try:
                    Zimmeranzahl = article.css('h3.Box-cYFBPY::text').extract()[0].strip()
                except:
                    Zimmeranzahl = 'unbekannt'
                try:
                    Wohnungsgroesse_m2 = article.css('h3.Box-cYFBPY::text').extract()[2].strip(),
                except:
                    Wohnungsgroesse_m2 = 'unbekannt'
                try:
                    Verkaufspreis = article.css('h3.Box-cYFBPY > span::text').extract()[0].strip(),
                except:
                    Verkaufspreis = 'unbekannt'
                try:
                    Wohnungsadresse = article.css('span.AddressLine__TextStyled-eaUAMD::text').extract()[0],
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

        next_page = 'https://www.immoscout24.ch/de/wohnung/kaufen/land-schweiz-fl?pn=' + str(ScoutSpider.page_number)
        if ScoutSpider.page_number <= 44:
            ScoutSpider.page_number += 1
            yield response.follow(next_page, callback = self.parse)



# Scrapy starten und Resultate in csv schreiben (-o fügt hinzu, -O überschreibt => -t csv -o ./output/appartements_bereinigt.csv)
#Shell Spider laufen lassen => scrapy runspider tutorial\tutorial\spiders\scout_final.py