from airflow import DAG
from pendulum import yesterday
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id='air06',
    schedule_interval=None,
    start_date=yesterday('Asia/Seoul'),
    catchup=False
)

# ds : {{ ds }} / {{ logical_date }}
def hello(ds):
    print(ds)

def print_context01(**kwargs):
    print(kwargs)

def print_context02(ds, **kwargs):
    print(ds)
    print(kwargs)

task01=PythonOperator(
    task_id='print_context',
    # python_callable=hello,
    # python_callable=print_context01,
    python_callable=print_context02,
    dag=dag
)
