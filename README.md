# Kafka Streaming project

## Project Overview

This project is designed to create a data pipeline that ingests real-time financial data from an external API, processes it using Kafka, and stores the data in both MongoDB and an AWS S3 bucket. The project uses several Docker containers, orchestrated by Docker Compose, to run services such as Kafka, MongoDB, Kafka Connect, and ksqlDB, ensuring seamless communication between components.

1. **Producer**:
   - A Python script (`producer.py`) that periodically fetches stock data (like prices and volume) from a third-party API (e.g., for companies like Apple and Tesla). The data is enriched with a timestamp and published to a Kafka topic (`api-data`).

2. **Kafka**:
   - A Kafka cluster (with **Zookeeper** for coordination and a **broker** for message handling) processes the incoming data. Kafka acts as a distributed message queue, storing the financial data in the `api-data` topic for downstream consumers. Zookeeper is essential for managing Kafka brokers and ensuring they operate in harmony. It stores metadata and handles leader elections. The Kafka Broker is responsible for handling message storage and retrieval. It communicates with Zookeeper to maintain its state and metadata.

3. **Consumer**:
   - A second Python script (`consumer.py`) listens to the `api-data` topic using a **Kafka Consumer**. The data is consumed and then stored in AWS S3 with a structured folder hierarchy (year/month/day) for historical tracking.

4. **MongoDB & Kafka Connect**:
   - **Kafka Connect** is configured to automatically consume the Kafka topic and push the data into **MongoDB** for easy querying and further analysis. A custom JAR-based MongoDB sink connector enables this integration.

5. **ksqlDB**:
   - The project includes **ksqlDB**, which provides a powerful SQL-based interface to query Kafka topics in real-time. This allows for data exploration and transformation directly within Kafka without the need to pull data into external databases.

6. **Mongo Express**:
   - A web-based interface (**Mongo Express**) is also included for managing and visualizing the data stored in MongoDB, providing an easy way to interact with the database.

This pipeline handles everything from data ingestion, real-time processing, and storage, offering flexibility for future extensions such as adding new connectors, querying data with SQL, or integrating with additional data sinks.



## How to Run the Project Locally

Follow these steps to set up and run the project locally on your machine.

### Prerequisites

1. **Install Docker and Docker Compose**
   - Ensure that both Docker and Docker Compose are installed on your local machine.
     - [Install Docker](https://docs.docker.com/get-docker/)
     - [Install Docker Compose](https://docs.docker.com/compose/install/)

2. **Set up AWS Credentials**
   - This project requires AWS credentials to upload data to an S3 bucket. Make sure you have AWS credentials set up locally. You can configure them by running the following command:
     ```bash
     aws configure
     ```
   - You can also provide the credentials in the `consumer.py` file, as shown in the `boto3` setup section.

3. **Install Python (Optional)**
   - If you need to test the `producer.py` or `consumer.py` scripts outside of Docker, you will need Python 3.x installed.
   - [Download Python](https://www.python.org/downloads/)

### Steps to Run the Project

#### 1. Build the Docker Images

First, navigate to the `producer/` and `consumer/` directories and build the Docker images for both the `producer` and `consumer` services.

##### Build the Producer Image
```bash
cd producer/
docker build -t my-producer .
```

##### Build the Consumer Image
```bash
cd ../consumer/
docker build -t my-consumer .
```

#### 2. Start the Containers with Docker Compose

Once the images are built, navigate back to the root directory where your docker-compose.yaml file is located and run the following command to spin up all the services:
```bash
docker-compose up
```

This will start the following containers:
- Zookeeper (for Kafka coordination)
- Kafka Broker (for message handling)
- Kafka Connect (for connecting Kafka to MongoDB)
- MongoDB (for data storage)
- Mongo Express (for managing and visualizing MongoDB data)
- ksqlDB Server and CLI (for querying Kafka topics)
- - Producer (to produce data from the API into the Kafka topic)
Consumer (to consume Kafka messages and store them in S3)


#### 3. Verify that the Containers Are Running
You can verify that all containers are running using the following command:
```bash
docker ps
```

This should list all the services defined in the docker-compose.yaml file.

#### 4. Check MongoDB Data with Mongo Express
Mongo Express is accessible at http://localhost:8081. You can log in and inspect the data that Kafka Connect has written to MongoDB. Note: in the MongoDB configuration of the docker-compose.yml file, there is the definition of volumes:
```bash
myvolume:/data/db
```
This mounts a named volume called `myvolume` to the container's `/data/db directory`, which is where MongoDB stores its data. This ensures that your data persists even if the container is stopped or removed.

#### 5. Query Kafka Topics with ksqlDB
Access the ksqlDB CLI container by running:
```bash
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

You can run SQL-like queries on the Kafka topics here to inspect and transform the data flowing through the pipeline.

#### 6. Monitor AWS S3
The consumer.py script will store the processed data in your specified S3 bucket. You can monitor your AWS S3 bucket to verify that the data is being stored correctly.


### Additional Commands
To stop all the running containers, use:
```bash
docker-compose down
```

To restart individual services:
```bash
docker-compose restart <service-name>
```

To rebuild a specific service if changes are made:
```bash
docker-compose up --build <service-name>
```

e.g. 
```bash
docker-compose up --build producer
```


### Access to MongoDB - Kafka Connect

in your Kafka pipeline, **Kafka Connect** is used to move data from Kafka topics to external systems (in your case, MongoDB). It simplifies the process of getting data into and out of Kafka by using connectors. The Kafka Connect service provides a REST API for managing connectors (source connectors and sink connectors). Once your containers are up and running, we need to register a new Kafka Connector with Kafka Connect by sending a POST request to the Kafka Connect REST API. In our case, we need the MongoDB sink connector to start consuming data from Kafka and storing it in MongoDB. This is the command for it: 
```bash
curl -d @simplelink.json -H "Content-Type: application/json" -X POST http://localhost:8083/connectors
```

The `simplelink.json` file contains the configuration for the connector, such as:
- The Kafka topic to read from.
- The MongoDB connection details.
- The database and collection where data should be stored.

In terms of the `http://localhost:8083/connectors` endpoint: This is the URL of the Kafka Connect REST API. You're sending the POST request to the connectors endpoint, which is responsible for creating new connectors.


### Access to S3 

You will need to create an **IAM user** in AWS, with access to the S3 bucket and its objects. This user's credentials are used by the `consumer.py` script, in order to write to S3.

Example of the **IAM policy** that is assigned to the IAM user:
```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::my-bucket"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObjectAcl",
                "s3:GetObjectAcl",
                "s3:DeleteObjectVersion"
            ],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

You might need to update to the **policy of the S3 bucket**: 
```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::XXXXXXXXXX:user/my-IAM-user"
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::my-bucket"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::XXXXXXXXXX:user/my-IAM-user"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

## Notes on Components

### Kafka cluster - networking

**Kafka Ports (29092 vs. 9092)**
`Port 9092`: This is the **internal** Kafka port used for communication between containers **within the same Docker network**. Services like your producer.py, consumer.py, and other services (like Kafka Connect) inside the same Docker Compose network should use this port to connect to the Kafka broker.
`Port 29092`: This is the **external port** mapped to your host machine. You would use this port if you want to connect to Kafka **from outside the Docker network** (e.g., from your local machine if running a Python script outside of Docker).

**How to ensure communication**:
You need to ensure that your services connect to the correct port based on where they are running.

1. `Producer and Consumer (Inside Docker)`:
In your `docker-compose.yaml` file, both `producer.py` and `consumer.py` are running inside Docker containers. Since all these containers are part of the same Docker network, they should connect to the Kafka broker using port **9092**, which is the internal port exposed by Kafka within the Docker network. The host broker is the hostname of the Kafka broker inside the Docker network (as defined in the Docker Compose file).

2. `MongoDB Communication`:
In your case, the Kafka Connect connector will be responsible for pushing data from Kafka to MongoDB. Both Kafka Connect and MongoDB are running inside Docker, so they can communicate directly using MongoDB's internal hostname (mongo) and port (**27017**). MongoDB should be configured with ports: 27017:27017, which means it exposes port 27017 for internal communication (within Docker) and external communication (on your host machine).

3. `External Connections`:
If you need to run a script (e.g., producer.py or consumer.py) from outside the Docker network (from your host machine), you'll need to connect to Kafka using port **29092**. This is the external port that Docker maps to the Kafka broker. For example, if you were testing producer.py from your host, you would set bootstrap_servers=['localhost:29092'] because your Kafka broker is externally accessible on localhost:29092.

### Offset Explorer 
This is a great free GUI that we can use to inspect topics and messages in your Kafka cluster.

After installing Offset Explorer, in ordertTo create a connection to you Kafka cluster, you can select to `add cluster`. As `Cluster Name` you can add any descriptive name, e.g. *"Local Kafka Cluster"*. Under `Bootstrap Servers`, since your Kafka broker is running locally, use *localhost:29092*. This maps the internal Kafka broker port 9092 to your host machine via port 29092, as specified in your `docker-compose.yaml` file. Then you can verify that the connection works. The `Data` is visible within the `Partition` 0 of the `Topic` api-data. It is presented in Hex decoding. You can use any tool, e.g. codeBeautify (https://codebeautify.org/hex-string-converter) to convert that to the json string.

We can see that the data files are landing succesfully from the Consumer to the S3 bucket. 
Moreover, thanks to the Kafka Connect integration with MongoDB, we can observe the new `database` (mydb) and `collection` (api) being created, as per the `simplelink.json` configuration, with the data flowing in.


### How Kafka Connect Stores Data in MongoDB
Kafka Connect consumes messages from the api-data Kafka topic. It uses a sink connector to automatically transfer the data into MongoDB. It then writes the data to MongoDB collections, where each message corresponds to a document.

To achieve this, you’ll need to install and configure the MongoDB Kafka Connector for Kafka Connect, which you can do by placing the required connector JAR in the container path defined in the Docker Compose file (/etc/kafka-connect/jars). Each connector is typically packaged as a JAR (Java Archive) file that contains the code and dependencies necessary to interact with a specific system.


### Overview of ksqlDB Server and CLI
`ksqlDB` is a powerful stream processing engine that allows you to interact with and process Kafka data using SQL-like syntax. This is especially useful for transforming, filtering, and querying real-time streams of data without the need for custom code.

In your Kafka-based data pipeline, ksqlDB can be used to:
- Query Kafka topics in real-time
- Transform data within Kafka topics (e.g., filtering or enriching messages)
- Join Kafka topics to perform advanced stream processing

You have two main components related to ksqlDB:
- **ksqlDB Server**: This runs the actual engine, which processes your SQL queries over Kafka topics.
- **ksqlDB CLI**: This is the command-line interface you use to interact with the ksqlDB server. You can run SQL queries, define stream transformations, and more from the CLI.

After connecting with: 
```bash
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088 , our command line allows us to perform queries towards the kafka topic. 
```

#### Step 1: Create Stream
First, you need to define a stream for the data coming into your Kafka topic (api-data). Here’s how you would do this in the ksqlDB CLI.

```bash
CREATE STREAM stock_data (
  meta STRUCT<requested INT, returned INT>,
  data ARRAY<STRUCT<
    ticker STRING,
    name STRING,
    mic_code STRING,
    currency STRING,
    price DOUBLE,
    day_high DOUBLE,
    day_low DOUBLE,
    day_open DOUBLE,
    _52_week_high DOUBLE,
    _52_week_low DOUBLE,
    market_cap BIGINT,
    previous_close_price DOUBLE,
    previous_close_price_time STRING,
    day_change DOUBLE,
    volume BIGINT,
    is_extended_hours_price BOOLEAN,
    last_trade_time STRING
  >>,
  timestamp_utc STRING
)
WITH (
  KAFKA_TOPIC='api-data',
  VALUE_FORMAT='JSON'
);
```

Explanation: This creates a stream from the api-data Kafka topic, interpreting the JSON payload. Each record has fields such as ticker, price, day_high, volume, etc.
ARRAY<STRUCT<...>> is used because the data field in your JSON is an array of stock data.

Verify that the Stream is created: 
```bash
SHOW STREAMS;
```

You can also check the topics in the kafka broker:
```bash
SHOW TOPICS;
```

You can always drop the Stream later:
```bash
DROP STREAM IF EXISTS API_DATA_STREAM;
```

#### Step 2: Query the Stream
Once the stream is created, you can start querying it using SQL-like queries.

Example 1: Select All Data from the Stream

```bash
SELECT * FROM stock_data EMIT CHANGES;
```
This will output all stock records as they are ingested into the Kafka topic.

Example 2: Filter Stocks Based on Price

If you want to filter and display only stocks where the price is greater than $170:
```bash
SELECT data[0]->ticker AS ticker, data[0]->price AS price
FROM stock_data
WHERE data[0]->price > 170 EMIT CHANGES;
```

Example 3: Aggregating Data (Average Price per Ticker)
```bash
SELECT data[0]->ticker AS ticker,
       AVG(data[0]->price) AS avg_price
FROM stock_data
GROUP BY data[0]->ticker EMIT CHANGES;
This will output the average price for each stock ticker as new data arrives.
```

Step 3: Write to Another Kafka Topic
You can transform or process the data and write the results to a new Kafka topic. 
For example, if you want to create a new stream with just the filtered high-priced stocks, you could do the following:

```bash
CREATE STREAM high_price_stocks AS
SELECT data[0]->ticker AS ticker, data[0]->price AS price
FROM stock_data
WHERE data[0]->price > 170
EMIT CHANGES;
```

#### Use cases of ksqlDB in our setup:

- **Real-Time Alerts**: You can set up real-time alerts or monitoring. For example, trigger an alert when the price of a stock goes below a certain threshold.
- **Data Transformation**: Clean, filter, or aggregate the raw stock data in real-time and store the results in new Kafka topics for further processing.
- **Join Streams**: You can combine stock data with other Kafka streams (e.g., news, financial data) for more complex stream processing.