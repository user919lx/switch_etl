import json
import re
from urllib.parse import urljoin

import arrow
from arrow.parser import ParserError
from switch_etl.db import MySQLStorage
from zhconv import convert
import logging


class GamePipeline:
    def __init__(self, mysql_config):
        self.query_storage = MySQLStorage(mysql_config)
        self.save_storage = MySQLStorage(mysql_config)

    def process_date(self, raw_date):
        if raw_date:
            try:
                return arrow.get(raw_date).date()
            except ParserError:
                print(f"========= error date: {raw_date}=======================")

    def parse_jpy(self, price_str):
        m = re.search(r"(\d+,)?\d+", price_str)
        if m:
            return int(m.group().replace(",", ""))

    def parse_row_impl(self, raw_data):
        raise NotImplementedError("execute_impl must be implemented by subclass")

    def process(self):
        self.query_storage.open()
        self.save_storage.open()
        record_iter = self.query_storage.record_iter(
            "game_raw", filter_clause=f"region='{self.region}'", batch_size=1000
        )
        logging.info(f"region = {self.region} ,start writing rows")
        for records in record_iter:
            for row in records:
                raw_data = MySQLStorage.uncompress(row[3], True)
                # parse_func = PARSE_FUNC_DICT[region]
                parse_data = self.parse_row_impl(raw_data)
                parse_data["unique_id"] = row[1]
                self.save_storage.save(f"game_{self.region}", parse_data)
        logging.info("finish writing")
        self.query_storage.close()
        self.save_storage.close()


class GameHKPipeline(GamePipeline):
    region = "hk"

    def parse_row_impl(self, raw_json):
        row = json.loads(raw_json)
        nsuid = row["link"].split("/")[-1]
        name = row["title"].strip()
        name_sc = row.get("title_sc").strip()
        if not name_sc and name:
            name_sc = convert(name, "zh-cn")
        data = {
            "nsuid": nsuid,
            "name": name,
            "name_sc": name_sc,
            "release_date": self.process_date(row["release_date"]),
            "url": row["link"].strip(),
            "maker_publisher": row.get("maker_publisher").strip(),
            "product_code": row["product_code"].strip(),
        }
        return data


class GameJPPipeline(GamePipeline):
    region = "jp"

    def parse_row_impl(self, raw_json):
        row_list = json.loads(raw_json)
        name_map = {
            "initialcode": "code",
            "titlename": "name",
            "makername": "maker",
            "makerkana": "makerkana",
            "dliconflg": "dliconflg",
            "salesdate": "release_date",
            "softtype": "soft_type",
            "platformid": "platform_id",
            "screenshotimgurl": "img",
        }
        row_data = {}
        for key, value in row_list.items():
            map_name = name_map.get(key)
            if map_name:
                if map_name == "release_date":
                    value = self.process_date(value)
                row_data[map_name] = value
            elif key in ("screenshotimgflg"):
                continue
            elif key == "price":
                row_data[key] = self.parse_jpy(value)
            else:
                row_data[key] = value
        return row_data


class GameNAPipeline(GamePipeline):
    region = "na"

    def parse_row_impl(self, raw_json):
        row = json.loads(raw_json)
        name_map = {
            "objectID": "object_id",
            "nsuid": "nsuid",
            "title": "name",
            "description": "game_desc",
            "horizontalHeaderImage": "img",
            "boxart": "boxart",
            "msrp": "price",
            "lowestPrice": "lowest_price",
            "priceRange": "price_range",
            "esrbRating": "esrb_rating",
        }
        row_data = {}
        for key, value in row.items():
            map_name = name_map.get(key)
            if map_name:
                row_data[map_name] = value
            elif key == "releaseDateDisplay":
                row_data["release_date"] = self.process_date(value)
            elif key == "url":
                if row["title"] == "Worms W.M.D":
                    row_data["url"] = "https://www.nintendo.com/store/products/worms-w-m-d-switch/"
                else:
                    base = "https://www.nintendo.com/"
                    row_data["url"] = urljoin(base, value)
            elif key in ("developers", "publishers", "genres"):
                row_data[key] = ",".join(value)
            elif key == "numOfPlayers":
                num_of_players = None
                if value:
                    m = re.search(r"up to (\d)+ players", value)
                    if value == "1 player":
                        num_of_players = 1
                    elif m:
                        num_of_players = int(m.group(1))
                row_data["num_of_players"] = num_of_players
        return row_data


class GameEUPipeline(GamePipeline):
    region = "eu"

    def parse_row_impl(self, raw_json):
        row = json.loads(raw_json)
        name_map = {
            "fs_id": "fs_id",
            "title": "name",
            "product_catalog_description_s": "game_desc",
            "image_url": "img",
            "image_url_h2x1_s": "boxart",
            "publisher": "publisher",
            "price_regular_f": "price",
            "price_lowest_f": "lowest_price",
            "digital_version_b": "has_digital_version",
            "physical_version_b": "has_physical_version",
            "eshop_removed_b": "eshop_removed",
            "players_to": "num_of_players",
            "pretty_agerating_s": "pretty_agerating",
            "age_rating_type": "age_rating_type",
            "age_rating_value": "age_rating_value",
        }
        row_data = {}
        for key, value in row.items():
            map_name = name_map.get(key)
            if map_name:
                row_data[map_name] = value
            elif key == "nsuid_txt":
                nsuid = value[0] if value else None
                row_data["nsuid"] = nsuid
            elif key == "dates_released_dts":
                if value:
                    release_date = self.process_date(value[0])
                else:
                    release_date = None
                row_data["release_date"] = release_date
            elif key == "url":
                base = "https://www.nintendo-europe.com/"
                row_data["url"] = urljoin(base, value)
            elif key == "product_code_ss":
                row_data["product_code"] = value[0]
            elif key == "genres":
                genres = ",".join(value) if value else None
                row_data["product_code"] = genres
        return row_data


class GamePipelineFactory(object):
    pipeline_dict = {
        "hk": GameHKPipeline,
        "jp": GameJPPipeline,
        "na": GameNAPipeline,
        "eu": GameEUPipeline,
    }

    def generate_game_pipeline(self, region, mysql_config):
        pipeline_class = self.pipeline_dict[region]
        pipeline = pipeline_class(mysql_config)
        return pipeline
