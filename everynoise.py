import scrapy
from scrapy.crawler import CrawlerProcess
import json
import io
import time
from datetime import datetime
import os
from urllib.parse import parse_qs, urlparse
import boto3
import logging

# enable logging
logging.basicConfig(level=logging.INFO, filename="everynoise_newreleases_logs.log", filemode="a", format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

bucket_name = "uvt-streaming-data"
bucket_dir = 'everynoise/new-releases/'

# function to backup on S3
def uploadToS3(filepath, filename):

    logging.info("Trying to upload to S3 file... %s", filename)

    # uploads the file via a managed uploader, which will split up large files automatically and upload in parallel
    try:
        s3.upload_file(filepath, bucket_name, filename)
        logging.info("Upload to S3 OK.")
        return True
    except boto3.exceptions.S3UploadFailedError as e:
        logging.critical("Upload to S3 ERROR.", exc_info=True)
        return False


# function to move files to errorsDirectory when an error is raised
def moveFile(filepath, filename):
    try:
        os.rename(filepath, errorsDirectory + "/" + filename)
        logging.error("File moved to /errors: %s", filepath)
    except OSError as e:
        logging.critical("Can't move file: %s", filepath, exc_info=True)


class EveryNoiseSpider(scrapy.Spider):
    name = "releases"
    start_urls = ['http://everynoise.com/new_releases_by_genre.cgi?region=']

    def parse(self, response):
        for region in response.xpath('//select[@name="region"]/option'):
            # reconstruct the url using the country code obtained from the "region" drop-down menu
            final_url = self.start_urls[0] + region.css('option::attr(value)').get() + "&albumsonly=&style=cards&date=&genre=anygenre&artistsfrom="
            # final_url = self.start_urls[0] + "US" + "&albumsonly=&style=cards&date=&genre=anygenre&artistsfrom="  # Uncomment for US only - use it to debug
            yield scrapy.Request(final_url, callback=self.parse_page)

    def parse_page(self, response):
        logging.info("Crawling started...")
        # retrieve date from "date" drop-down menu
        everyNoiseDate = response.xpath('//select[@name="date"]/option[@selected]/text()').get()
        # retrieve country code from the current url parameter
        parsed_url = urlparse(response.request.url)
        countryCode = parse_qs(parsed_url.query)['region'][0]  # the list contains only 1 item, the current country code

        with open(htmlDirectory +'/page_' + runDate + '_' + countryCode + '.html', 'wb') as html_file:
            html_file.write(response.body)
            files_to_handle.append(os.path.basename(html_file.name))  # add html_file filename to files_to_handle list

        for albumrow in response.css('div.albumrow'):
            # if a:nth-child(3) contains no text, then the album name is in the child i
            if albumrow.css('a:nth-child(3)::text').get() is None:
                albumName = albumrow.css('a > i::text').get()
            else:
                albumName = albumrow.css('a:nth-child(3)::text').get()

            yield {
                'countryCode': countryCode,
                'trackId': albumrow.css('span.play::attr(trackid)').get(),
                'artistId': albumrow.css('a::attr(href)').extract()[0],
                'rank': albumrow.css('a::attr(title)').extract()[0],
                'artistName': albumrow.css('a > b::text').get(),
                'albumId': albumrow.css('a::attr(href)').extract()[1],
                'albumName': albumName,
                'scrapeUnix': runUnix,
                'scrapeDate': runDate,
                'everyNoiseDate': everyNoiseDate,
            }


# define list to collect all items
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
    'LOG_LEVEL' : 'INFO',
})

# define directories
directory = "output"
htmlDirectory = "html_dumbs"
errorsDirectory = "errors"

try:
    os.makedirs(directory)
except FileExistsError:
    pass  # directory already exists
try:
    os.makedirs(htmlDirectory)
except FileExistsError:
    pass  # directory already exists
try:
    os.makedirs(errorsDirectory)
except FileExistsError:
    pass  # directory already exists

# define timestamps
runUnix = int(time.time())
runDate = datetime.now().strftime("%Y%m%d")

# define empty list for file names that needs to be handled
files_to_handle = []

# create an S3 client and configure from shell
s3 = boto3.client("s3")

# launch the spider
process.crawl(EveryNoiseSpider)
process.start()  # the script will block here until the crawling is finished

# write output file
with io.open(directory + "/everynoise_newreleases_" + runDate + ".json", "w", encoding="UTF-8") as json_output:
    for item in items:  # loop through objects to add new lines between them
        json.dump(item, json_output, ensure_ascii=False)
        json_output.write("\n")  # add new line for the next object
    logging.info("File written.")
    files_to_handle.append(os.path.basename(json_output.name))  # append json_output filename to files_to_handle list

# upload all json files to S3
for file in os.scandir(directory):
    if file.name.endswith(".json") and file.name in files_to_handle:  # only upload files from the current crawling
        uploadResult = uploadToS3(file.path, bucket_dir+file.name)
        if uploadResult is False:
            moveFile(file.path, file.name)  # move file to errorsDirectory if an error is raised
        logging.info("All done with json files.")

# upload all html files from htmlDirectory to S3
for file in os.scandir(htmlDirectory):
    if file.name.endswith(".html") and file.name in files_to_handle:  # only upload files from the current crawling
        uploadResult = uploadToS3(file.path, bucket_dir+"html_dumbs/"+file.name)
        if uploadResult is False:
            moveFile(file.path, file.name)  # move file to errorsDirectory if an error is raised
        logging.info("All done with html files.")
