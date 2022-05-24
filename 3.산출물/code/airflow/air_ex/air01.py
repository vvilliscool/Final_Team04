from airflow import DAG
from pendulum import yesterday
from airflow.operators.python import PythonOperator

# DAG 객체 생성
# pendulum : airflow의 날짜, 시간에 사용
dag = DAG(
    dag_id='air01',
    schedule_interval=None,
    # start_date = DAG가 시작되는 기준 시점, 그 날짜에 실행된다는 의미가 아님
    # 현재 시간이 start_date보다 이전이면 DAG가 실행되지 않음
    start_date=yesterday('Asia/Seoul')
)

def hello():
    print('Hello,airflow!')

# python 함수 실행
task01 = PythonOperator(
    task_id='hello',
    # python_callable=함수명 "()" 은 제외
    python_callable=hello,
    dag=dag
)
