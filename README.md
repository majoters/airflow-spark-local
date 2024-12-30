# Apache Airflow & Spark for Local Development

This repository contains Airflow & Spark for local docker development, built-in with Hive Metastore and Minio

## Components
1. Apache Spark 3.5.3
    - Spark in Standalone Cluster Mode
    - Spark History Server
2. Apache Hadoop 3.3.6
3. Apache Hive 2.3.9
4. Python 3.12.17 
5. Jupyter Lab
6. Minio Server (S3)
7. Apache Airflow 2.10.3

## Services in Docker
| Name                 | URL                                                      | Remark |
|----------------------|----------------------------------------------------------| ----- |
| Jupyter Lab          | [http://localhost:8089](http://localhost:8089)           | |
| Spark Master         | [http://localhost:8080](http://localhost:8080)           | |
| Spark History Server | [http://localhost:18080](http://localhost:18080)         | |
| Spark Web UI         | [http://localhost:4040-4060](http://localhost:4040-4060) | |
| Minio Web UI         | [http://localhost:9000](http://localhost:9000)           | `minioadmin` is username and password |
| Hive Metastore       | [thrift://localhost:9083](thrift://localhost:9083)       | |
| Airflow              | [http://localhost:8082](http://localhost:8082)           | |

## How to Get Started
- build the docker
```
docker build -t spark-in-local:latest \
    --build-arg spark_version=3.5.3 \
    --build-arg hadoop_version=3.3.6 \
    --build-arg hive_version=2.3.9 \
    .
```
- start the components
```
docker compose up -d

# scale spark worker
docker compose up -d --scale spark-worker=2
```

## Prepare Sample Data
- you can simply select `./data/nyc_taxi_data` in order to download 3 months of nyc taxt data 2024
- then you can upload it to bucket `s3://raw-data`

## How to run PySpark 
1. run through Jupyter Notebook (init sample database)
    - range of Spark Web UI port is `4040-4050`
2. run through spark-submit command through `spark-master` (see [spark_script.py](./spark_script.py))
    - execute `docker exec -it spark-master /bin/bash`
    - then do spark-submit (see spark-submit script in [spark_script.py](./spark_script.py))
    - range of Spark Web UI port is `4040-4050`
    - the script [spark_script.py](./spark_script.py) contains example of how to create Hive table and Iceberg table, which store data externally in S3 (Minio)

## Notes 
- The Hive database `local_db` is created automatically when you started the docker
- The S3 bucket `spark-warehouse`, `raw-data,` and `spark-event` are created automatically