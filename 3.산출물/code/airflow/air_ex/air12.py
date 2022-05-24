from airflow import DAG
from pendulum import yesterday
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.apache.hdfs.sensors.hdfs import HdfsSensor
from airflow.operators.bash import BashOperator

dag = DAG(
    dag_id='air12',
    schedule_interval=None,
    start_date=yesterday('Asia/Seoul'),
    catchup=False
)

spark_submit_task = SparkSubmitOperator(
    task_id='spark_submit_task',
    application='/home/hjyoon/airflow/dags/using_spark.py',
    conn_id='spark_default',
    dag=dag
)

# /result/_SUCCESS 파일이 만들어지면 다음 단계로 진행
hadoop_sensor_task = HdfsSensor(
    task_id='hadoop_sensor_task',
    filepath='hdfs://home/hjyoon/result/_SUCCESS',
    hdfs_conn_id='hdfs_default',
    dag=dag
)

prn_task = BashOperator(
    task_id='prn',
    bash_command='echo success pyspark proccess',
    dag=dag
)

spark_submit_task >> hadoop_sensor_task >> prn_task
