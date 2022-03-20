import pandas as pd
from slugify import slugify
from switch_etl.pipeline import Pipeline


class SupplyExcelPipeline(Pipeline):

    def get_slug(self, name):
        name = name.replace("®", "").replace("&", "and")
        return f"{slugify(name)}-switch"

    def process(self, output_path):
        sql = """select
            cn_name,en_name,jp_name,purchased,played,
            if(gna.developers is not null and gna.developers!='',gna.developers,r.developers) developers,
            CASE
                WHEN gna.publishers is not null and gna.publishers!='' THEN gna.publishers
                WHEN geu.publisher is not null and geu.publisher!='' THEN geu.publisher
                ELSE r.publishers
            END publishers,
        developer_type,switch_only,party_type,genre,topic,metacritic_rating,
        if(gna.price!='' and gna.price is not null,gna.price,r.price) price,
        case
            when if(gna.price!='' and gna.price is not null,gna.price,r.price) ='' then null
            when if(gna.price!='' and gna.price is not null,gna.price,r.price) <5 then '$0 - $4.99'
            when if(gna.price!='' and gna.price is not null,gna.price,r.price) <10 then '$5 - $9.99'
            when if(gna.price!='' and gna.price is not null,gna.price,r.price) <20 then '$10 - $19.99'
            when if(gna.price!='' and gna.price is not null,gna.price,r.price) <40 then '$20 - $39.99'
            when if(gna.price!='' and gna.price is not null,gna.price,r.price) >=40 then '$40+'
            else null
        end price_range,
        r.num_of_players,
        screen_use,has_cn,somatic_game,
        r.game_desc,game_review,remark,rating,rating_difficulty,
        rating_joy,rating_smooth,rating_playable,recommend_num_of_player,
        stage,duration_per_game,recommend_total_duration,recommend_level,
        gna.url,
        gna.img
    from review r 
    left join game_na gna on r.en_name = gna.name
    left join game_eu geu on r.en_name = geu.name
    """
        df = pd.read_sql(sql, self.db.get_conn())

        def add_columns(row):
            supply_data = {
                "Jump Force: Deluxe Edition": {
                    "url": "数字版已下架",
                    "img": "https://getluxury.hk/wp-content/uploads/2020/08/jump-force-deluxe-edition-switch-hero.jpg",
                },
                "Fishing Spirits": {
                    "url": "https://store-jp.nintendo.com/list/software/70010000016824.html",
                    "img": "https://img-eshop.cdn.nintendo.net/i/f68fd45c8cd8d3a55248c3a6bfabfbd2a6fb3922f5e17ded8efe80cf368a5a90.jpg",
                    "developers": "Bandai Namco",
                },
                "Luigi's Mansion 3": {
                    "img": "https://assets.nintendo.com/image/upload/ncom/en_US/games/switch/l/luigis-mansion-3-switch/hero",
                },
                "Trials Rising": {
                    "img": "https://assets.nintendo.com/image/upload/ncom/en_US/games/switch/t/trials-rising-standard-edition-switch/hero",
                },
                "Gang Beasts": {"developers": "Boneloaf"},
                "Wanba Warriors": {"url": "", "img": ""},
            }

            if not row["url"]:
                en_name = row["en_name"]
                if en_name in supply_data:
                    data = supply_data[en_name]
                    for key, value in data.items():
                        row[key] = value
                else:
                    slug = self.get_slug(en_name)
                    row["url"] = f"https://www.nintendo.com/store/products/{slug}/"
                    row["img"] = f"https://assets.nintendo.com/image/upload/ncom/en_US/games/switch/{slug[0]}/{slug}/hero"
            return row
        df = df.apply(add_columns, axis=1)
        df = df.sort_values(["rating", "en_name"], ascending=[False, True])
        df.to_excel(output_path, index=False)
