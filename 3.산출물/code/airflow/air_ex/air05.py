from airflow import DAG
from pendulum import yesterday
from airflow.operators.python import PythonOperator

# catchup=False : backfill을 하지 않음
dag=DAG(
    dag_id='air05',
    start_date=yesterday('Asia/Seoul'),
    schedule_interval='*/1 * * * *',
    catchup=False
)
def hello():
    print('backfill')

task01=PythonOperator(
    task_id='backfill_test',
    python_callable=hello,
    dag=dag
)
