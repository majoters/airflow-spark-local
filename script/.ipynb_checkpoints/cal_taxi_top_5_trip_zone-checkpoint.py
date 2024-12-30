from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, current_timestamp, date_format, dense_rank, lit, to_date
from pyspark.sql.window import Window

# Initialize Spark session
spark = SparkSession \
    .builder \
    .appName("spark-nb") \
    .master("spark://spark-master:7077") \
    .enableHiveSupport() \
    .getOrCreate()

# Input table name containing trip records
data_table = "local_db.sample_hive_table"

# Output table name
output_table = "local_db.daily_topfive_taxi_zone"

# Get execution date from arguments (Airflow) or default to current date
execution_date = sys.argv[1] if len(sys.argv) > 1 else spark.sql("SELECT current_date() as current_date").collect()[0]["current_date"]

# Calculate the target date for data filtering
target_date = spark.sql(f"SELECT date_sub('{execution_date}', 1) as target_date").collect()[0]["target_date"]

# Read the input data
data = spark.table(data_table)

# Filter the data for trips that occurred before the target date
filtered_data = data.filter(to_date(col("lpep_pickup_datetime")) < lit(target_date))

# Calculate the top-5 TLC Taxi Zones based on trip count
top_five_zones = filtered_data.groupBy("PULocationID") \
    .agg(count("*").alias("trip_count")) \
    .withColumn("rank", dense_rank().over(Window.orderBy(col("trip_count").desc()))) \
    .filter(col("rank") <= 5) \
    .select(
        col("PULocationID").alias("taxi_zone_id"),
        col("rank"),
        date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss").alias("calculated_at")
    )

# Write the result into the output table
top_five_zones.write \
    .mode("overwrite") \
    .format("hive") \
    .saveAsTable(output_table)

spark.sql("SELECT * FROM local_db.sample_hive_table LIMIT 5").toPandas()

spark.sql("SELECT * FROM local_db.daily_topfive_taxi_zone LIMIT 5").toPandas()

# Stop the Spark session
spark.stop()