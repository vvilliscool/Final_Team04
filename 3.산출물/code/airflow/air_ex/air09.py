import imp
from pprint import pprint
from airflow import DAG
from pendulum import yesterday
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

dag=DAG(
    dag_id='air09',
    schedule_interval=None,
    start_date=yesterday('Asia/Seoul'),
    catchup=False
)

def print_context(**kwargs):
    pprint(kwargs)
    return str(kwargs)

task01=PythonOperator(
    task_id='print_context',
    python_callable=print_context,
    dag=dag
)

# xcom으로 전달된 내용을 파일로저장
task02=BashOperator(
    task_id='save_context',
    bash_command='echo "{{ task_instance.xcom_pull(task_ids="print_context") }}" >> ~/context.json',
    dag=dag
)
