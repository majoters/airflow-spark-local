"""
spark-submit \
    --master spark://spark-master:7077 \
    --deploy-mode client \
    --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1 \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
    --conf spark.sql.catalog.spark_catalog.type=hive \
    spark_script.py
"""

from pyspark.sql import SparkSession

# Initialize Spark session with Hive support
spark = SparkSession.builder.appName("test").enableHiveSupport().getOrCreate()

# Load the data from S3
df = spark.read.format('parquet').load("s3a://raw-data/")

print(f"Row count: {df.count()}")
print(df.printSchema())

# Select target columns and limit rows
target_columns = ["VendorID", "lpep_pickup_datetime", "lpep_dropoff_datetime"]
df = df.select(target_columns)
df = df.limit(100)

# Hive database and table names
hive_db = "local_db"
hive_table_name = "test_from_spark_submit"
full_table_name = f"{hive_db}.{hive_table_name}"

# Check if the table exists
table_exists = spark.sql(f"SHOW TABLES IN {hive_db}").filter(f"tableName = '{hive_table_name}'").count() > 0

# Drop the table if it exists
if table_exists:
    print(f"Dropping table {full_table_name}")
    spark.sql(f"DROP TABLE {full_table_name}")

# Create the table
print(f"Creating table {full_table_name}")
df.writeTo(full_table_name).using("iceberg").create()

# Verify table creation by showing its schema
create_table_stmt = spark.sql(f"SHOW CREATE TABLE {full_table_name}").collect()[0].createtab_stmt
print(create_table_stmt)

# Query the table and display results
spark.sql(f"SELECT * FROM {full_table_name} LIMIT 10").show()