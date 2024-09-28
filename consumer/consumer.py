from kafka import KafkaConsumer
from json import loads
import json
from time import sleep
import boto3
from datetime import datetime

consumer = KafkaConsumer(
    'api-data', #the topic name
     bootstrap_servers=['broker:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-consumers-group-2',  #you need a consumer group to be able to commit the offset
     value_deserializer=lambda x: loads(x.decode('utf-8')))

# s3 configuration
# Get the AWS access key and secret key from environment variables
access_key = 'XXXXXX'
secret_key = 'XXXXXX'

# Create a session using the AWS keys
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

# Create an S3 client
s3 = session.client('s3')


for count, message in enumerate(consumer):

    data = message.value
    print(json.dumps(data, indent = 1)) 

    #extract date string from payload
    timestamp_string = data['timestamp_utc']

    #convert the string to datetime object, so that we can extract year, month, day
    timestamp_utc = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%SZ')
    utc_year = timestamp_utc.strftime("%Y")
    print('utc_year',utc_year)
    utc_month = timestamp_utc.strftime("%m")
    print('utc_year',utc_month)
    utc_day = timestamp_utc.strftime("%d")
    print('utc_year',utc_day)
    utc_hour = timestamp_utc.strftime("%H")
    utc_minute = timestamp_utc.strftime("%M")
    utc_second = timestamp_utc.strftime("%S")


    # Save the dictionary to a JSON file
    json_file = 'data.json'
    with open(json_file, 'w') as f:
        json.dump(data, f,  indent=4)


    # Upload the JSON file to S3
    s3.upload_file(json_file, 'my-bucket-name', f'kafka_api_data/{utc_year}/{utc_month}/{utc_day}/input_file_{utc_year}_{utc_month}_{utc_day}_{utc_hour}_{utc_minute}_{utc_second}_.json')
