from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'Supakorn',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='daily_topfive_taxi_zone_dag',
    default_args=default_args,
    description='A daily DAG to calculate top 5 taxi zones by trip count',
    schedule_interval='@daily',  # Runs daily
    start_date=datetime(2024, 1, 1),  # Replace with desired start date
    catchup=False,  # Ensures missed runs are backfilled
    max_active_runs=4,
    tags=['taxi_zones', 'spark', 'hive']
) as dag:
    
    # Define the Spark job task
    calculate_topfive_zones = SparkSubmitOperator(
        task_id='calculate_topfive_zones',
        application='/opt/airflow/script/cal_taxi_top_5_trip_zone.py',  # Replace with the actual script path
        conn_id='spark_default',  # Ensure this connection is set up in Airflow
        verbose=True,
        env_vars={
            'HADOOP_CONF_DIR': '/opt/hadoop/etc/hadoop',
            'YARN_CONF_DIR': '/opt/hadoop/etc/hadoop'
        },
        application_args=['{{ execution_date.strftime("%Y-%m-%d") }}']  # Pass execution_date for backfilling date
    )

    calculate_topfive_zones