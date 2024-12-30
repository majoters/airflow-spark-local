from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, date_format, to_timestamp, current_timestamp, lit, to_date
import sys

# Initialize Spark session
spark = SparkSession \
    .builder \
    .appName("spark-nb") \
    .master("spark://spark-master:7077") \
    .config("hive.metastore.uris", "thrift://metastore:9083") \
    .config("spark.sql.warehouse.dir", "s3a://raw-data") \
    .config("spark.sql.catalogImplementation", "hive") \
    .enableHiveSupport() \
    .getOrCreate()

# Input table name
data_table = "local_db.sample_hive_table"

# Output table name
output_table = "local_db.daily_transaction"

# Get execution date from Airflow or default to the current date
execution_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")

# Calculate the previous day's date
execution_date_obj = datetime.strptime(execution_date, "%Y-%m-%d")
previous_date_obj = execution_date_obj - timedelta(days=1)
transaction_date = previous_date_obj.strftime("%Y-%m-%d")

print(f"Execution date: {execution_date}")
print(f"Transaction date: {transaction_date}")

# Read the input data
df = spark.read.format("parquet").load("s3a://raw-data/")
df.printSchema()
data = spark.table(data_table)

# Filter and calculate total transactions for the previous day
daily_transaction = data \
    .filter(to_date(col("lpep_pickup_datetime")) == to_date(lit(transaction_date))) \
    .agg(
        lit(transaction_date).alias("transaction_date"),
        count("*").alias("total_transactions"),
        date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss").cast("string").alias("calculated_at")
    )

# Write the result into the output table
daily_transaction.write \
    .mode("append") \
    .format("hive") \
    .saveAsTable(output_table)

sample_hive_pandas = spark.sql("SELECT * FROM local_db.sample_hive_table LIMIT 5").toPandas()
print("Sample Hive Data:")
print(sample_hive_pandas)

daily_transaction_pandas = spark.sql("SELECT * FROM local_db.daily_transaction LIMIT 5").toPandas()
print("Daily Transaction Data:")
print(daily_transaction_pandas)

# Stop the Spark session
spark.stop()





