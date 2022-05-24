from airflow import DAG
from pendulum import yesterday, tomorrow
from datetime import timedelta
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id='air04',
    # schedule_interval='* */1 * * *',
    # schedule_interval=timedelta(hours=1),
    schedule_interval='@hourly',
    start_date=yesterday('Asia/Seoul'),
    end_date=tomorrow()
)

def hello():
    print('time')

task01=PythonOperator(
    task_id='scheduler_test',
    python_callable=hello,
    dag=dag
)