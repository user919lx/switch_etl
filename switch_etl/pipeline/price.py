from switch_etl.pipeline import Pipeline
import json


class PricePipeline(Pipeline):
    def process(self):
        self.db.open()
        iter = self.db.record_iter("price_raw", batch_size=10000)
        item_list = []
        for rows in iter:
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
        self.db.save_many("price_raw_new", item_list)
        self.db.close()
