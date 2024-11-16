from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from influxdb import InfluxDBClient
import json

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkStreamingToInfluxDB") \
    .getOrCreate()

# Define the schema for the JSON data
json_schema = StructType([
    StructField("val", IntegerType(), True),
    StructField("etat", StringType(), True)
])

# Reading data from Kafka (using direct stream approach)
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "sensor_temp") \
    .load()

# Kafka data has keys and values as binary, so we cast them to string
df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Parse the JSON data in the 'value' column
df_json = df.withColumn("json_data", from_json(col("value"), json_schema))

# Extract fields from json_data
df_extracted = df_json.select("json_data.val", "json_data.etat")

# Group by 'etat' and calculate the average of 'val'
processed_df = df_extracted.groupBy("etat").agg(avg("val").alias("average_val"))

# Function to write data to InfluxDB
def write_to_influxdb(batch_df, batch_id):
    client = InfluxDBClient(host="influxdb", port=8086, username="change", password="this", database="DBTWO")

    # Convert the DataFrame to Pandas for easier manipulation
    pandas_df = batch_df.toPandas()

    # Prepare InfluxDB points
    points = []
    for index, row in pandas_df.iterrows():
        point = {
            "measurement": "sensor_data",
            "tags": {
                "etat": row["etat"]
            },
            "fields": {
                "average_val": row["average_val"]
            }
        }
        points.append(point)

    # Write the points to InfluxDB
    client.write_points(points)

# Use foreachBatch to apply write_to_influxdb on each streaming batch
query = processed_df.writeStream \
    .outputMode("complete") \
    .foreachBatch(write_to_influxdb) \
    .start()

# Wait for the query to finish
query.awaitTermination()

# Stop Spark session
spark.stop()