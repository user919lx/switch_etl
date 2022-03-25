from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator

with DAG(
    'eshop',
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        'depends_on_past': False,
        'email': ['user919lx@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 3, 24),
    catchup=False,
    tags=['eshop'],
) as dag:

    crawler_root = "/home/ubuntu/Projects/crawler/switch"
    crawler_python = "/home/ubuntu/.local/share/virtualenvs/crawler-BBmXFxCd/bin/python"
    eshop = BashOperator(
        task_id='eshop',
        bash_command=f'cd {crawler_root} && {crawler_python} -m scrapy crawl eshop',
    )
