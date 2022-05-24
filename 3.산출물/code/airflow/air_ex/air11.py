from airflow import DAG
from pendulum import yesterday
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

dag = DAG(
    dag_id='air11',
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