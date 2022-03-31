import click
import logging
from switch_etl.db import MySQLStorage
from switch_etl.setting import MYSQL_CONFIG
from switch_etl.pipeline.supply_excel import SupplyExcelPipeline
from switch_etl.pipeline.game import GamePipelineFactory
from switch_etl.spider.game_na import GameNASpider
from switch_etl.spider.game_db import GameDBSpider
from switch_etl.pipeline.content import ContentPipeline
from switch_etl.pipeline.price import PricePipeline


def init_logging(
    level_name="info",
    fmt="%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - [%(process)d:%(threadName)s] - %(message)s",
    silent_cassandra=True,
):
    level = logging.INFO
    if level_name == "info":
        level = logging.INFO
    elif level_name == "warning":
        level = logging.WARNING
    elif level_name == "error":
        level = logging.ERROR
    elif level_name == "debug":
        level = logging.DEBUG
    logging.basicConfig(level=level, format=fmt)

    if silent_cassandra:
        # cassandra is too noisy
        logging.getLogger("cassandra.cluster").setLevel(logging.WARNING)


def __upload():
    db = MySQLStorage(MYSQL_CONFIG)
    file = "input/games.xlsx"
    table = "review"
    db.upload_excel(file, table)


def __gen_new_game_info():
    pipeline = SupplyExcelPipeline(MYSQL_CONFIG)
    pipeline.process("output/games_new.xlsx")


def __gen_md():
    pipeline = ContentPipeline(MYSQL_CONFIG)
    input_path = "output/games_new.xlsx"
    output_path = "output/review.md"
    pipeline.md_content(input_path, output_path)


@click.group()
def cli():
    init_logging()


@cli.command()
def upload():
    __upload()


@cli.command()
def gen_new():
    __gen_new_game_info()


@cli.command()
def md():
    __gen_md()


@cli.command()
def gen_review():
    __upload()
    __gen_new_game_info()
    __gen_md()


@cli.command()
@click.option("-r", "--region")
def game_pipeline(region):
    factory = GamePipelineFactory()
    pipeline = factory.generate_game_pipeline(region, MYSQL_CONFIG)
    pipeline.process()


@cli.command()
def na_spider():
    spider = GameNASpider(MYSQL_CONFIG)
    spider.fetch_data_all()


@cli.command()
def db_spider():
    spider = GameDBSpider(MYSQL_CONFIG)
    spider.fetch_data_all()


@cli.command()
def price_etl():
    pipeline = PricePipeline(MYSQL_CONFIG)
    pipeline.process()


if __name__ == "__main__":
    cli()
