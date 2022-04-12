from switch_etl.pipeline import Pipeline
import json
import pandas as pd
import re


class GameMultPipeline(Pipeline):
    def process(self):
        self.db.open()
        conn = self.db.get_conn()
        sql1 = "select uncompress(raw_data) raw_data from game_raw where region='deku'"
        df_deku = pd.read_sql(sql1, conn)

        def process_deku(row):
            mode_list = ["local", "wireless", "online"]
            jdict = json.loads(row["raw_data"])
            row["en_name"] = jdict.get("name")
            if jdict.get("number_of_players"):
                pjlist = json.loads(jdict.get("number_of_players"))
                mode_map = {"Offline": "local", "Local Wireless": "wireless", "Online": "online"}
                for data in pjlist:
                    mode = mode_map.get(data["key"])
                    value = data["value"]
                    if mode and value:
                        value = value.replace(" ", "")
                        row[f"{mode}_num_of_players"] = value
                        row[f"{mode}_max_num_of_players"] = value.split("-")[-1]
            for mode in mode_list:
                num_players = row.get(f"{mode}_num_of_players")
                max_num_players = row.get(f"{mode}_max_num_of_players")
                row[f"{mode}_num_of_players"] = num_players if num_players else None
                row[f"{mode}_max_num_of_players"] = max_num_players if max_num_players else None
            return row

        df_deku = df_deku.apply(process_deku, axis=1)
        df_deku = df_deku[
            [
                "en_name",
                "local_num_of_players",
                "wireless_num_of_players",
                "online_num_of_players",
                "local_max_num_of_players",
                "wireless_max_num_of_players",
                "online_max_num_of_players",
            ]
        ]
        df_deku = df_deku[df_deku["local_num_of_players"].notnull()]

        sql2 = """
            select gn.name,mul.local,mul.wireless,mul.online
            from (select *,replace(substring_index(url,'/',-2),'-switch/','') slug from game_na) gn
            join (select replace(substring_index(url,'/',-2),'-switch/','') slug,local,wireless,online
            from game_na_mult where local is not null) mul on gn.slug = mul.slug
        """
        df_na_mul = pd.read_sql(sql2, conn)

        def process_mul(row):
            row["en_name"] = re.sub("[™®]", "", row["name"])
            mode_list = ["local", "wireless", "online"]
            for mode in mode_list:
                num_players = row.get(mode)
                if num_players:
                    row[f"{mode}_num_of_players"] = num_players
                    row[f"{mode}_max_num_of_players"] = num_players.split("-")[-1]
                else:
                    row[f"{mode}_num_of_players"] = None
                    row[f"{mode}_max_num_of_players"] = None
            return row

        df_na_mul = df_na_mul.apply(process_mul, axis=1)
        df_na_mul = df_na_mul[
            [
                "en_name",
                "local_num_of_players",
                "wireless_num_of_players",
                "online_num_of_players",
                "local_max_num_of_players",
                "wireless_max_num_of_players",
                "online_max_num_of_players",
            ]
        ]
        df_na_mul = df_na_mul[df_na_mul["local_num_of_players"].notnull()]
        df_all = pd.concat([df_deku, df_na_mul]).drop_duplicates(["en_name"])
        for row in df_all.to_dict("records"):
            self.db.save("game_mult", row)
        self.db.close()
