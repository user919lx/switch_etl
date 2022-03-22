import io
import logging
import zipfile

import requests
from bs4 import BeautifulSoup
from switch_etl.db import MySQLStorage
from zhconv import convert
import html


class GameDBSpider:
    def __init__(self, mysql_config):
        self.storage = MySQLStorage(mysql_config)

    def __parse_game(self, game):
        local_player = game.input.attrs["players"]
        online_player = game.find("wi-fi").attrs["players"]

        data = {
            "code": game.id.text,
            "region": game.region.text,
            "languages": game.languages.text,
            "name": game.attrs["name"],
            "developer": game.developer.text if game.developer else None,
            "publisher": game.publisher.text if game.publisher else None,
            "num_of_players": local_player if local_player else None,
            "num_of_online_players": online_player if online_player else None,
        }
        if game.find("locale", {"lang": "EN"}):
            en_name = game.find("locale", {"lang": "EN"}).title.text.strip()
            for keyword in ["Trine 4", "Diablo III"]:
                if keyword in en_name:
                    en_name.replace("-", ":")
            data["en_name"] = html.unescape(en_name)
        if game.find("locale", {"lang": "JA"}):
            data["jp_name"] = game.find("locale", {"lang": "JA"}).title.text.strip()
        if game.find("locale", {"lang": "ZHCN"}):
            data["cn_name"] = convert(game.find("locale", {"lang": "ZHCN"}).title.text, "zh-cn").strip()
        elif game.find("locale", {"lang": "ZHTW"}):
            data["cn_name"] = convert(game.find("locale", {"lang": "ZHTW"}).title.text, "zh-cn").strip()

        if game.rating_ESRB:
            data["esrb_rating"] = (game.rating_ESRB.attrs["value"],)
            data["esrb_rating_desc"] = (",".join([desc.text.strip() for desc in game.find_all("descriptor_ESRB")]),)
        if game.rating_PEGI:
            data["pegi_rating"] = (game.rating_PEGI.attrs["value"],)
            data["pegi_rating_desc"] = (",".join([desc.text.strip() for desc in game.find_all("descriptor_PEGI")]),)
        return data

    def fetch_data_by_region(self, region):
        params = {"LANG": region}
        url = "https://www.gametdb.com/switchtdb.zip"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.post(url, params=params, headers=headers)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("output")
        with open("output/switchtdb.xml", "r") as f:
            contents = f.read()
            soup = BeautifulSoup(contents, "html.parser")
            games = soup.find_all("game")
            for game in games:
                data = self.__parse_game(game)
                try:
                    self.storage.save("game_db", data)
                except Exception as e:
                    print("error", e, data)

    def fetch_data_all(self):
        self.storage.open()
        rlist = ["JA", "EN", "ZHCN", "ZHTW"]
        for region in rlist:
            logging.info(f"starting crawl region = {region}")
            self.fetch_data_by_region(region)
            logging.info(f"finish crawl region = {region}")
        logging.info("finish all")
        self.storage.close()
