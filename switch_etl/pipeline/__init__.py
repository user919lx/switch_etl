from switch_etl.db import MySQLStorage


class Pipeline:
    def __init__(self, mysql_config):
        self.db = MySQLStorage(mysql_config)
