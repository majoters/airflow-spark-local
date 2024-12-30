# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col, count, current_timestamp, date_sub, date_format, lit, to_date

# # Initialize Spark session
# spark = SparkSession \
#     .builder \
#     .appName("spark-nb") \
#     .master("spark://spark-master:7077") \
#     .enableHiveSupport() \
#     .getOrCreate()

# # Input table name
# data_table = "local_db.sample_hive_table"

# # Output table name
# output_table = "local_db.daily_transaction"

# # Get current date (execution date) and calculate previous day's date
# execution_date = spark.sql("SELECT current_date() as current_date").collect()[0]["current_date"]
# transaction_date = spark.sql(f"SELECT date_sub('{execution_date}', 1) as transaction_date").collect()[0]["transaction_date"]

# # Read the input data
# data = spark.table(data_table)

# # Filter and calculate total transactions for the previous day
# daily_transaction = data \
#     .filter(to_date(col("lpep_pickup_datetime")) == lit(transaction_date)) \
#     .agg(
#         lit(transaction_date).alias("transaction_date"),
#         count("*").alias("total_transactions"),
#         date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss").alias("calculated_at")
#     )

# # Write the result into the output table
# daily_transaction.write \
#     .mode("append") \
#     .format("hive") \
#     .saveAsTable(output_table)

# spark.sql("SELECT * FROM local_db.sample_hive_table LIMIT 5").toPandas()

# spark.sql("SELECT * FROM local_db.daily_transaction LIMIT 5").toPandas()

# # Stop the Spark session
# spark.stop()

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, current_timestamp, date_sub, lit, to_date

# Initialize Spark session
spark = SparkSession \
    .builder \
    .appName("spark-nb") \
    .master("spark://spark-master:7077") \
    .enableHiveSupport() \
    .getOrCreate()

# Input table name
data_table = "local_db.sample_hive_table"

# Output table name
output_table = "local_db.daily_transaction"

# Get execution date from Airflow or default to the current date
execution_date = sys.argv[1] if len(sys.argv) > 1 else spark.sql("SELECT current_date() as current_date").collect()[0]["current_date"]

# Calculate the previous day's date
transaction_date = spark.sql(f"SELECT date_sub('{execution_date}', 1) as transaction_date").collect()[0]["transaction_date"]

# Read the input data
data = spark.table(data_table)

# Filter and calculate total transactions for the previous day
daily_transaction = data \
    .filter(to_date(col("lpep_pickup_datetime")) == lit(transaction_date)) \
    .agg(
        lit(transaction_date).alias("transaction_date"),
        count("*").alias("total_transactions"),
        current_timestamp().alias("calculated_at")
    )

# Write the result into the output table
daily_transaction.write \
    .mode("append") \
    .format("hive") \
    .saveAsTable(output_table)

# Stop the Spark session
spark.stop()





