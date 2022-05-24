from airflow import DAG
from pendulum import yesterday
from airflow.operators.bash import BashOperator

dag = DAG(
    dag_id='air2',
    schedule_interval=None,
    start_date=yesterday('Asia/Seoul')
)

task01=BashOperator(
    task_id='hello',
    bash_command='echo Hello, Airflow!',
    dag=dag
)
