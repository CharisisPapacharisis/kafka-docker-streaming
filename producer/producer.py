# Python 3
import http.client, urllib.parse
from kafka import KafkaProducer
from json import dumps, loads
from time import sleep
from datetime import datetime

#params for api request
params = urllib.parse.urlencode({
    'api_token': 'XXXXXX',
    'symbols': 'AAPL,TSLA',
    'limit': 1,
    })

#initialize the kafka producer
producer = KafkaProducer(bootstrap_servers=['broker:9092'],
                         value_serializer=lambda x: bytes(dumps(x,default=str).encode('utf-8'))
                         )
#ongoing loop
while True: 
    conn = http.client.HTTPSConnection('api.stockdata.org')
    conn.request('GET', '/v1/data/quote?{}'.format(params))

    res = conn.getresponse()
    data = res.read()
    print ("data_before_decoding: ", data)

    #add time
    utc_time = datetime.utcnow()
    utc_time_str = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ") 

    data = data.decode('utf-8')
    print ("data_after_decoding: ", data)

    # convert dictionary-string to dictionary
    data_dict = loads(data)

    data_dict['timestamp_utc'] = utc_time_str
    print("data dict: ", data_dict)

    #send the data to the correct topic
    try:
        producer.send('api-data', value = data_dict )
        print ("data sent to topic")
        #producer.flush()
    except Exception as e:
            print("didnt work:", e)
            pass
    
    #wait a few minutes before calling again the API
    sleep(300)

