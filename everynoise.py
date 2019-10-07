import scrapy
from scrapy.crawler import CrawlerProcess
import json
import io
import time
from datetime import datetime
import os

directory = 'html_dumbs'
try:
    os.stat(directory)
except:
    os.mkdir(directory)    
    

run_unix = int(time.time())
run_date = datetime.now().strftime("%Y%m%d")

class EveryNoiseSpider(scrapy.Spider):
    name = "releases"
    start_urls = ['http://everynoise.com/new_releases_by_genre.cgi?region=']
    
    def parse(self, response):
        for region in response.xpath('//select[@name="region"]/option'):
            # reconstruct the url using the country code parameter obtained from the "region" drop-down
            final_url = self.start_urls[0] + region.css('option::attr(value)').get() + "&albumsonly=&style=cards&date=&genre=anygenre&artistsfrom="
            # final_url = self.start_urls[0] + "US" + "&albumsonly=&style=cards&date=&genre=anygenre&artistsfrom="  # Un comment for US only - use it to debug
            yield scrapy.Request(final_url, callback=self.parse_page)

    def parse_page(self, response):
        countryCode = response.request.url[55:57]
        #every_date=response.css(' body > form > div.title > select:nth-child(4) > option:nth-child(1)')
       
        with open(directory+'/page_'+run_date+'_'+countryCode+'.html', 'wb') as backup_file:
            backup_file.write(response.body)
        
        for albumrow in response.css('div.albumrow'):
            # if a:nth-child(3) contains no text, then the album name is in the child i
            if albumrow.css('a:nth-child(3)::text').get() is None:
                albumName = albumrow.css('a > i::text').get()
            else:
                albumName = albumrow.css('a:nth-child(3)::text').get()
            # directly obtain the country code from the region parameter in the current url
            
            yield {
                'countryCode': countryCode,
                'trackId': albumrow.css('span.play::attr(trackid)').get(),
                'artistId': albumrow.css('a::attr(href)').extract()[0],
                'rank': albumrow.css('a::attr(title)').extract()[0],
                'artistName': albumrow.css('a > b::text').get(),
                'albumId': albumrow.css('a::attr(href)').extract()[1],
                'albumName': albumName,
                'scrape_unix': run_unix,
                'scrape_date': run_date,
                'everynoise_date': 'PUT DATE HERE, e.g., FROM LISTBOX; see every_date variable above',
            }

# list to collect all items
items = []


# pipeline processes items
class EveryNoisePipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        items.append(item)


# settings
process = CrawlerProcess(settings={
    'ITEM_PIPELINES': {'everynoise.EveryNoisePipeline': 300},
})


process.crawl(EveryNoiseSpider)
process.start()  # the script will block here until the crawling is finished

# write output file
with io.open("everynoise_newreleases_"+run_date+".json", "w", encoding="UTF-8") as json_output:
    for item in items:  # loop through objects to add new lines between them
        json.dump(item, json_output, ensure_ascii=False)
        json_output.write("\n")  # add new line for the next object
    print("File written.")
