from airflow import DAG
from pendulum import today
from airflow.operators.python import PythonOperator

dag=DAG(
    dag_id='air08',
    schedule_interval=None,
    start_date=today('Asia/Seoul')
)

# context의 task_instance (task객체가 가지고 있는 xcom)
def send_function(task_instance):
    msg = 'xcom test'
    task_instance.xcom_push(key='msg', value=msg)

# context에서 task_instance 키를 통해 객체 참도
def receive_function(**kwargs):
    print(f"receiv: {kwargs['task_instance'].xcom_pull(task_ids='task1',key='msg')}")

task1=PythonOperator(
    task_id='task1',
    python_callable=send_function,
    dag=dag
)

task2=PythonOperator(
    task_id='task2',
    python_callable=receive_function,
    dag=dag
)
task1 >> task2