from airflow import DAG
from pendulum import yesterday
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

dag = DAG(
        dag_id='air3',
        schedule_interval=None,
        start_date=yesterday('Asia/Seoul')
        )

def hello():
    print('Hello, Python!')

task01=PythonOperator(
        task_id='hello_python',
        python_callable=hello,
        dag=dag
        )

task02=BashOperator(
        task_id='hello_bash',
        bash_command='echo Hello,Bash',
        dag=dag
        )

# task 순서
# A >> B : A는 B의 upstream / B는 A의 downstream
task01 >> task02
