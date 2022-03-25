from datetime import datetime, timedelta
from airflow.models import Variable

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator

with DAG(
    "eshop",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["user919lx@gmail.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A simple tutorial DAG",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 3, 24),
    catchup=False,
    tags=["eshop"],
) as dag:

    MYSQL_HOST = Variable.get("MYSQL_HOST")
    MYSQL_PWD = Variable.get("MYSQL_PWD")
    MYSQL_USER = Variable.get("MYSQL_USER")
    env = {
        "MYSQL_HOST": MYSQL_HOST,
        "MYSQL_PWD": MYSQL_PWD,
        "MYSQL_USER": MYSQL_USER,
    }
    crawler_root = Variable.get("CRAWLER_ROOT") + "/switch"
    crawler_python = Variable.get("CRAWLER_PYTHON")
    switch_etl_root = Variable.get("SWITCH_ETL_ROOT")
    switch_etl_python = Variable.get("SWITCH_ETL_PYTHON")

    spider_eshop = BashOperator(
        task_id="spider_eshop",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl eshop",
        env=env,
    )
    spider_game_raw_jp = BashOperator(
        task_id="spider_game_raw_jp",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl game_jp",
        env=env,
    )
    spider_game_raw_eu = BashOperator(
        task_id="spider_game_raw_eu",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl game_eu",
        env=env,
    )
    spider_game_raw_hk = BashOperator(
        task_id="spider_game_raw_hk",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl game_hk",
        env=env,
    )
    spider_game_raw_na = BashOperator(
        task_id="spider_game_raw_na",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py na-spider",
        env=env,
    )
    etl_game_jp = BashOperator(
        task_id="etl_game_jp",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py -r jp",
        env=env,
    )
    etl_game_hk = BashOperator(
        task_id="etl_game_jp",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py -r hk",
        env=env,
    )
    etl_game_na = BashOperator(
        task_id="etl_game_jp",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py -r na",
        env=env,
    )
    etl_game_eu = BashOperator(
        task_id="etl_game_jp",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py -r eu",
        env=env,
    )
    spider_price = BashOperator(
        task_id="spider_price",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl price",
        env=env,
    )

    spider_game_raw_jp >> etl_game_jp
    spider_game_raw_na >> etl_game_na
    spider_game_raw_eu >> etl_game_eu
    spider_game_raw_hk >> etl_game_hk

    [etl_game_jp, etl_game_na, etl_game_eu, etl_game_hk] >> spider_price

# spider_eshop -> spider_price -> etl_price_etl
