import json

from algoliasearch.search_client import SearchClient
from switch_etl.db import MySQLStorage
from time import sleep
import logging


class GameNASpider:
    def __init__(self, mysql_config):
        self.client = SearchClient.create("U3B6GR4UA3", "c4da8be7fd29f0f5bfa42920b0a99dc7")
        self.storage = MySQLStorage(mysql_config)

    def __page_str(self, page, resp):
        return f"page = {page+1}, page_number = {resp['nbPages']}, page_row_number = {len(resp['hits'])}"

    def __save_resp_data(self, resp):
        for row in resp["hits"]:
            data = {"unique_id": row["objectID"], "region": "na", "raw_data": json.dumps(row, ensure_ascii=True)}
            self.storage.save("game_raw", data, compress_keys=["raw_data"])

    def fetch_data_all(self, hit_perpage=100):
        self.storage.open()
        ilist = ["ncom_game_en_us_title_des", "ncom_game_en_us_title_asc"]
        rlist = [
            "esrbRating:Everyone",
            "esrbRating:Everyone 10+",
            "esrbRating:Teen",
            "esrbRating:Mature",
            "availability:Pre-order",
            "availability:Coming soon",
            "availability:Available now",
            "franchises:Mario",
            "franchises:Zelda",
            "franchises:Pokémon",
            "franchises:Kirby",
        ]
        for rating in rlist:
            for iparam in ilist:
                logging.info(f"======= start: {iparam}  {rating} =======")
                page = 0
                resp = self.fetch_response(iparam, rating, page, hit_perpage)
                logging.info(self.__page_str(page, resp))
                if len(resp["hits"]) > 0:
                    self.__save_resp_data(resp)
                    page_number = resp["nbPages"]
                    while page + 1 < page_number:
                        page += 1
                        resp = self.fetch_response(iparam, rating, page, hit_perpage)
                        row_number = len(resp["hits"])
                        logging.info(self.__page_str(page, resp))
                        if row_number > 0:
                            self.__save_resp_data(resp)
                        sleep(1)
        self.storage.close()

    def fetch_response(self, iparam, rating, page, hit_perpage):
        index = self.client.init_index(iparam)
        facets = json.dumps(
            [
                "generalFilters",
                "platform",
                "availability",
                "genres",
                "howToShop",
                "virtualConsole",
                "franchises",
                "priceRange",
                "esrbRating",
                "playerFilters",
            ]
        )
        search_params = {
            "hitsPerPage": hit_perpage,
            "page": page,
            "analytics": False,
            "facets": facets,
            "facetFilters": f'[["{rating}"],["platform:Nintendo Switch"]]',
        }

        resp = index.search("", search_params)
        return resp
