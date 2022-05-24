import json
from airflow import DAG
from pendulum import yesterday
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor

dag=DAG(
    dag_id='air10',
    schedule_interval=None,
    start_date=yesterday('Asia/Seoul'),
    catchup=False
)

def python_task():
    dummy = {'key':'value'}
    return json.dumps(dummy)

crawling = PythonOperator(
    task_id='crawling',
    python_callable=python_task,
    dag=dag
)

make_file=BashOperator(
    task_id='make_file',
    bash_command='echo "{{ task_instance.xcom_pull(task_ids="crawling") }}" >> /home/hjyoon/dummy.json',
    dag=dag
)

# 30초마다 filepath에 file이 있는지 확인, 없으면 대기, 있으면 다음 task로 진행
# sensor : 한 가지 작업만 하는 operator, 특정 조건이 true인지 지속적으로 확인, false이면 true가 되던가 타임아웃이 될 때까지 계속 확인
exists = FileSensor(
    task_id = "exists",
    fs_conn_id = 'file_sensor',
    filepath= "/home/hjyoon/dummy.json",
    poke_interval=30,
    dag=dag
)

# hadoop에 파일 저장
upload = BashOperator(
    task_id='upload',
    bash_command='hdfs dfs -put /home/hjyoon/dummy.json /dummy.json',
    dag=dag
)

prn = BashOperator(
    task_id='prn',
    bash_command='echo "success makefile & upload"',
    dag=dag
)

crawling >> [make_file, exists] >> upload >> prn
