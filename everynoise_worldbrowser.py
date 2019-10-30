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
logging.basicConfig(level=logging.INFO, filename="everynoise_worldbrowser_logs.log", filemode="a", format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

bucket_name = "uvt-streaming-data"
bucket_dir = 'everynoise/worldbrowser/'


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


class EveryNoiseWorldBrowserSpider(scrapy.Spider):
    name = "worldbrowser"
    start_urls = ['http://everynoise.com/worldbrowser.cgi?section=']
    
    rate = .25
    
    def __init__(self):
        self.download_delay = 1/float(self.rate)
    
    def parse(self, response):
        for section in response.xpath('//select[@name="section"]/option'):
            # reconstruct the url using the section name and hour - if available - from drop-down
            section_name=section.css('option::attr(value)').get()
            
            if (section_name=='featured'):
                for hour in response.xpath('//select[@name="hours"]/option'):
                    final_url = self.start_urls[0] + section.css('option::attr(value)').get() + "&hours=" + hour.css('option::attr(value)').get()
                    # final_url = self.start_urls[0] + "featured" + "&hours=" + hour.css('option::attr(value)').get()  # Uncomment for featured only - use it to debug
                    # final_url = self.start_urls[0] + "featured" + "&hours=0"  # Uncomment for featured only - use it to debug
                    yield scrapy.Request(final_url, callback=self.parse_page)
            else:
                final_url = self.start_urls[0] + section.css('option::attr(value)').get() + '&hours=0'
                yield scrapy.Request(final_url, callback=self.parse_page)

    def parse_page(self, response):
        logging.info("Crawling started...")
        # retrieve hour from "hour" drop-down menu - if available
        try:
            everyNoiseHour = response.xpath('//select[@name="hours"]/option[@selected]/text()').get()
        except:
            everyNoiseHour = 'NA'

        # retrieve section name from the current url parameter
        parsed_url = urlparse(response.request.url)
        sectionName = parse_qs(parsed_url.query)['section'][0]  # the list contains only 1 item, the current section
        try:
            everyNoiseHourReference = parse_qs(parsed_url.query)['hours'][0]
        except:
            everyNoiseHourReference = 'NA'
       
        with open(htmlDirectory +'/worldbrowser_page_' + runTS + '_' + sectionName + '_'+ str(everyNoiseHour).replace(':','')+'.html', 'wb') as html_file:
            html_file.write(response.body)
            files_to_handle.append(os.path.basename(html_file.name))  # add html_file filename to files_to_handle list
        
        for playlists in response.css('div.playlists'):
            yield {
                'sectionName': sectionName,
                'countryName': playlists.xpath('preceding::a[1]/text()').get(),
                'countryCode': str(playlists.xpath('preceding::a[1]/@href').get())[9:11],  # a substring of the href tag
                'playlistIdArray': playlists.css('a::attr(href)').getall(),
                'scrapeUnix': runUnix,
                'scrapeDate': runDate,
                'everyNoiseHour': everyNoiseHour,
                'everyNoiseHourReference': everyNoiseHourReference,
            }


# define list to collect all items
items = []


# pipeline processes items
class EveryNoiseWorldBrowserPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        items.append(item)


# settings
process = CrawlerProcess(settings={
    'ITEM_PIPELINES': {'everynoise_worldbrowser.EveryNoiseWorldBrowserPipeline': 300},
    # 'LOG_LEVEL' : 'INFO',
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
runTS = datetime.now().strftime("%Y%m%d_%H%M")

# define empty list for file names that needs to be handled
files_to_handle = []

# create an S3 client and configure from shell
s3 = boto3.client("s3")

# launch the spider
process.crawl(EveryNoiseWorldBrowserSpider)
process.start()  # the script will block here until the crawling is finished

# write output file
with io.open(directory + "/everynoise_worldbrowser_" + runTS + ".json", "w", encoding="UTF-8") as json_output:
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
