import scrapy
# How to run it:
# cd to project dir and run: scrapy crawl releases -o releases.json

class ReleasesSpider(scrapy.Spider):
    name = "releases"
    start_urls = ['http://everynoise.com/new_releases_by_genre.cgi?genre=anygenre&region=US']

    def parse(self, response):
        # for albumrow in response.css('div.albumrow'):
        for albumrow in response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "albumrow", " " ))]'):
            yield {
                'trackid': albumrow.xpath('//b').getall(),
                # 'author': album.css('small.author::text').get(),
                'artistid': albumrow.xpath('//a+//a').get(),
            }
