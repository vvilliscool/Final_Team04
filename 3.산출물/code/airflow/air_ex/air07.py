from airflow import DAG
from pendulum import today
from airflow.operators.dummy import DummyOperator

dag = DAG(
    dag_id='air07',
    schedule_interval=None,
    start_date=today()
)

task1=DummyOperator(task_id="task1",dag=dag)
task2=DummyOperator(task_id="task2",dag=dag)
task3=DummyOperator(task_id="task3",dag=dag)
task4=DummyOperator(task_id="task4",dag=dag)
task5=DummyOperator(task_id="task5",dag=dag)
task6=DummyOperator(task_id="task6",dag=dag)
task7=DummyOperator(task_id="task7",dag=dag)
task8=DummyOperator(task_id="task8",dag=dag)

# fan-out(1:n)
task1 >> [task2, task3]
# fan-in(n:1)
[task2,task3] >> task4
task4 >> task5 >> task6
task3 >> task7
[task6, task7] >> task8
