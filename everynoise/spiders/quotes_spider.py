import scrapy
# How to run it:
# cd to project dir and run: scrapy crawl releases -o releases.json

class ReleasesSpider(scrapy.Spider):
    name = "releases"
    start_urls = ['http://everynoise.com/new_releases_by_genre.cgi?genre=anygenre&region=US']

    def parse(self, response):
        for albumrow in response.css('div.albumrow'):
            # If a:nth-child(3) contains no text, then the album name is in the child i
            if albumrow.css('a:nth-child(3)::text').get() == None:
                albumName = albumrow.css('a > i::text').get()
            else:
                albumName = albumrow.css('a:nth-child(3)::text').get()

            yield {
                'trackId': albumrow.css('span.play::attr(trackid)').get(),
                'artistId': albumrow.css('a::attr(href)').extract()[0],
                'rank': albumrow.css('a::attr(title)').extract()[0],
                'artistName': albumrow.css('a > b::text').get(),
                'albumId': albumrow.css('a::attr(href)').extract()[1],
                'albumName': albumName,
            }
