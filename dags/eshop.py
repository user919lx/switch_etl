from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.providers.mysql.operators.mysql import MySqlOperator
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator


clean_sql = """
truncate table game_clean
;insert into game_clean
select
    db.code,
    db.name db_name,
    case
    when eu_name is not null then eu_name
    when na_name is not null then na_name
    ELSE db.en_name
    end en_name,
    if (jp.jp_name is not null, jp.jp_name, db.jp_name) jp_name,
    if (hk_name is not null, hk_name, db.`cn_name`) cn_name,
    cast(case
    when eu_num_of_players is not null then eu_num_of_players
    ELSE db.`num_of_players`
    end as unsigned) num_of_players,
jp_nsuid,hk_nsuid,eu_nsuid,na_nsuid,
eu_lowest_price,na_lowest_price,
CURRENT_TIMESTAMP created_at
from game_db db left join (
select nsuid eu_nsuid,
replace(replace(replace (name,'™',''),'®',''),'’',"'") eu_name,
SUBSTR(product_code,5) code,lowest_price eu_lowest_price,
num_of_players eu_num_of_players
from game_eu
) eu on db.code = eu.code
left join (
select nsuid jp_nsuid,name jp_name, SUBSTR(code,4) code
from game_jp
) jp on db.code = jp.code
left join (
select nsuid hk_nsuid,name_sc hk_name,SUBSTR(trim(product_code),5) code
from game_hk
where trim(product_code)!=''
) hk on db.code = hk.code
left join (
select nsuid na_nsuid,
replace(replace(replace (name,'™',''),'®',''),'’',"'") na_name,
lowest_price na_lowest_price,
num_of_players na_num_of_players
from game_na
) na on eu.eu_name = na.na_name""".split(";")

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
    env = {
        "MYSQL_HOST": Variable.get("MYSQL_HOST"),
        "MYSQL_PWD": Variable.get("MYSQL_PWD"),
        "MYSQL_USER": Variable.get("MYSQL_USER"),
        "MYSQL_PORT": Variable.get("MYSQL_PORT")
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
    spider_db = BashOperator(
        task_id="spider_db",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py db-spider",
        env=env,
    )
    etl_game_jp = BashOperator(
        task_id="etl_game_jp",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py game-pipeline -r jp",
        env=env,
    )
    etl_game_hk = BashOperator(
        task_id="etl_game_hk",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py game-pipeline -r hk",
        env=env,
    )
    etl_game_na = BashOperator(
        task_id="etl_game_na",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py game-pipeline -r na",
        env=env,
    )
    etl_game_eu = BashOperator(
        task_id="etl_game_eu",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py game-pipeline -r eu",
        env=env,
    )
    etl_game_eu = BashOperator(
        task_id="etl_game_eu",
        bash_command=f"cd {switch_etl_root} && {switch_etl_python} cli.py game-mult",
        env=env,
    )
    spider_price = BashOperator(
        task_id="spider_price",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl price",
        env=env,
    )

    spider_game_deku = BashOperator(
        task_id="spider_game_deku",
        bash_command=f"cd {crawler_root} && {crawler_python} -m scrapy crawl game_deku",
        env=env,
    )

    game_clean = MySqlOperator(
        task_id="game_clean",
        sql=clean_sql,
        mysql_conn_id="switch_ol",
    )

    spider_game_raw_jp >> etl_game_jp
    spider_game_raw_na >> etl_game_na >> spider_game_deku >> etl_game_mult
    spider_game_raw_eu >> etl_game_eu
    spider_game_raw_hk >> etl_game_hk
    [etl_game_jp, etl_game_na, etl_game_eu, etl_game_hk] >> game_clean
    [spider_eshop, etl_game_jp, etl_game_na, etl_game_eu, etl_game_hk] >> spider_price

# spider_eshop -> spider_price -> etl_price_etl
