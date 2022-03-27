import json

from algoliasearch.search_client import SearchClient
from switch_etl.db import MySQLStorage
from time import sleep
import logging


class GameNASpider:
    def __init__(self, mysql_config):
        self.client = SearchClient.create("U3B6GR4UA3", "c4da8be7fd29f0f5bfa42920b0a99dc7")
        name_list = ["ncom_game_en_us_title_asc", "ncom_game_en_us_title_des"]
        self.index_list = [self.client.init_index(name) for name in name_list]
        self.index = self.index_list[0]
        self.storage = MySQLStorage(mysql_config)

    def __page_str(self, page, resp):
        return f"page = {page+1}, page_number = {resp['nbPages']}, page_row_number = {len(resp['hits'])}"

    def __save_resp_data(self, resp):
        rows = resp.get("hits")
        if rows:
            for row in rows:
                data = {
                    "unique_id": row["objectID"],
                    "region": "na",
                    "raw_data": json.dumps(row, ensure_ascii=True)
                }
                self.storage.save("game_raw", data, compress_keys=["raw_data"])

    def __fetch_response(self, index, facet_filters, page=0, hit_perpage=1000):
        facets = [
            "genres",
            "platform",
            "howToShop",
            "esrbRating",
            "franchises",
            "priceRange",
            "availability",
            "playerFilters",
            "generalFilters",
        ]
        all_ilters = [["platform:Nintendo Switch"]]
        all_ilters.extend(facet_filters)
        search_params = {
            "hitsPerPage": hit_perpage,
            "page": page,
            "analytics": False,
            "facets": json.dumps(facets),
            "facetFilters": json.dumps(all_ilters),
        }
        resp = index.search("", search_params)
        sleep(1)
        return resp

    def __get_genre_count(self, genre):
        facet_filters = [f"genres:{genre}"]
        resp = self.__fetch_response(self.index, facet_filters, page=0, hit_perpage=1)
        hits_count = resp.get("nbHits") or 0
        return hits_count

    # def fetch_data_all(self):
    #     for rating in rlist:
    #         logging.info(f"======= start: {iparam}  {rating} =======")
    #         page = 0
    #         resp = self.fetch_response(iparam, rating, page, hit_perpage)
    #         logging.info(self.__page_str(page, resp))
    #         if len(resp["hits"]) > 0:
    #             self.__save_resp_data(resp)
    #             page_number = resp["nbPages"]
    #             while page + 1 < page_number:
    #                 page += 1
    #                 resp = self.fetch_response(iparam, rating, page, hit_perpage)
    #                 row_number = len(resp["hits"])
    #                 logging.info(self.__page_str(page, resp))
    #                 if row_number > 0:
    #                     self.__save_resp_data(resp)
    #                 sleep(1)
    #     self.storage.close()

    def fetch_data_all(self):
        self.storage.open()
        genres = [
            'Action', 'Adventure', 'Arcade', 'Puzzle', 'Platformer', 'Role-Playing',
            'Simulation', 'Strategy', 'Multiplayer', 'Other', 'Party', 'Board Game',
            'Sports', 'Racing', 'Fighting', 'Education', 'Indie', 'First-Person',
            'Lifestyle', 'Music', 'Training', 'Study', 'Communication', 'Practical',
            'Utility', 'Video', 'Updates', 'Application', 'Shooter', 'Fitness'
        ]
        price_range = ["$5 - $9.99", "$10 - $19.99", "$0 - $4.99", "$20 - $39.99", "$40+", "Free to start"]
        hit_perpage = 1000
        for genre in genres:
            genre_count = self.__get_genre_count(genre)
            if genre_count <= 0:
                return
            elif genre_count <= 1000:
                facet_filters = [f"genres:{genre}"]
                index = self.index
                resp = self.__fetch_response(index, facet_filters, page=0, hit_perpage=hit_perpage)
                hits_count = resp.get("nbHits")
                logging.info(f"index: {index.name}  facet_filters:{facet_filters} hits_count:{hits_count}")
                self.__save_resp_data(resp)
            else:
                for price in price_range:
                    for index in self.index_list:
                        facet_filters = [f"genres:{genre}", f"priceRange:{price}"]
                        resp = self.__fetch_response(index, facet_filters, page=0, hit_perpage=hit_perpage)
                        hits_count = resp.get("nbHits")
                        logging.info(f"index: {index.name}  facet_filters:{facet_filters} hits_count:{hits_count}")
                        self.__save_resp_data(resp)
        self.storage.close()
