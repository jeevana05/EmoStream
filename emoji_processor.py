# emoji_proccessor.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, window, from_json, expr, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("EmojiProcessor") \
    .getOrCreate()

# Define the schema for the incoming JSON data
schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("emoji_type", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# Read data from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "emoji_topic") \
    .load()

# Cast the 'value' field to string (Kafka messages are in binary format by default)
df = df.selectExpr("CAST(value AS STRING) as json_value")

# Parse the JSON value in the 'value' column into individual columns (using the schema defined earlier)
emoji_data = df.select(from_json(col("json_value"), schema).alias("data"))

# Aggregate data by emoji_type within a 2-second window
aggregated_data = emoji_data.groupBy(
    window(expr("current_timestamp()"), "2 seconds"),
    "data.emoji_type"
).agg(count("data.emoji_type").alias("count")) \
    .filter(col("count") > 1)  # For testing, keeping count > 1

# Format the output for Kafka: convert to JSON string
formatted_output = aggregated_data.select(
    col("emoji_type").alias("key"),  # Use emoji_type as the key
    to_json(struct("emoji_type", "count")).alias("value")  # Convert count and emoji_type to JSON string for value
)

# Write the formatted data to Kafka topic 'aggregated_emoji_topic'
query = formatted_output.writeStream \
    .outputMode("complete") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "aggregated_emoji_topic") \
    .option("checkpointLocation", "/tmp/spark/checkpoint/kafka") \
    .start()

query.awaitTermination()

