from switch_etl.pipeline import Pipeline
import json
from switch_etl.db import MySQLStorage


class PricePipeline(Pipeline):

    def __init__(self, mysql_config):
        self.query_storage = MySQLStorage(mysql_config)
        self.save_storage = MySQLStorage(mysql_config)

    def process(self):
        self.query_storage.open()
        self.save_storage.open()
        iter = self.query_storage.record_iter("price_raw", batch_size=10000)
        i = 0
        for rows in iter:
            item_list = []
            for row in rows:
                raw_data = json.loads(row[3])
                data = {
                    "id": row[0],
                    "alpha2": row[1],
                    "nsuid": row[2],
                    "sales_status": raw_data["sales_status"],
                    "raw_data": row[3],
                    "created_at": row[4],
                }
                item_list.append(data)
            i += 1
            print(f"iter {i} times")
            if item_list:
                self.save_storage.save_many("price_raw_new", item_list)
        self.query_storage.close()
        self.save_storage.close()
