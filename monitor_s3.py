import boto3

bucket_name = "uvt-streaming-data"
bucket_dir = 'everynoise/'

s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucket_name)

obj=['<!doctype html>\n<html>\n<head>\n<title>Content of S3 directory</title>\n</head>\n<body>\n<p>']

files = []
for object_summary in my_bucket.objects.filter(Prefix=bucket_dir):
    if 'html_dumbs' not in object_summary.key:
        #obj.append('<br>'+object_summary.key)
        files.append(object_summary.key)
files=files[::-1]
obj.append('<br>'.join(files))
obj.append('</p>\n</body>\n</html>')


boto3.client('s3').put_object(Key='s3.html', Body=''.join(obj), ContentType='text/html', Bucket = 'uvt-public')
