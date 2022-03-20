import pandas as pd
from switch_etl.pipeline import Pipeline


class ContentPipeline(Pipeline):
    def row_content(self, row):
        topic = str(row["topic"])
        en_name = row["en_name"]
        cn_name = row["cn_name"]
        if en_name in ("ARMS™", "1-2-Switch™", "NBA 2K21") or en_name == cn_name:
            title = en_name
        else:
            title = f"{en_name} {cn_name}"

        if topic == "nan" or not topic:
            topic = ""
        else:
            topic = f"\n* Topic:{topic}"
        ps = str(row["remark"])
        if ps == "nan" or not ps:
            ps = ""
        else:
            ps = f"\n* 备注:{ps}"
        game_desc = row["game_desc"].replace("\n", "")
        game_review = row["game_review"].replace("\n", "")

        content = f"""### {title}
![封面]({row['img']})
eshop链接： {row['url']}

游戏基本信息

* 开发商：{row['developers']} {row['developer_type']}
* 发行商：{row['publishers']}
* Switch独占：{row['switch_only']}
* 协作/竞争：{row['party_type']}
* Genre：{row['genre']}{topic}
* metacritic评分：{row['metacritic_rating']}
* 价格：${row['price']}
* 人数范围：{row['num_of_players']}
* 分屏/同屏：{row['screen_use']}
* 中文：{row['has_cn']}
* 体感：{row['somatic_game']}

介绍

* 简介：{game_desc}
* 简评：{game_review}{ps}

评分

* 综合推荐度：{row['rating']}分"""

        append_content = f"""\n* 易上手度：{row['rating_difficulty']}分
* 欢乐度：{row['rating_joy']}分
* 流畅度：{row['rating_smooth']}分
* 耐玩度：{row['rating_playable']}分

游玩指南

* 推荐人数：{row['recommend_num_of_player']}
* 适合阶段：{row['stage']}
* 单局时长：{row['duration_per_game']}
* 建议总时长：{row['recommend_total_duration']}
* 建议游戏水平：{row['recommend_level']}
"""
        if row["rating"] >= 2:
            content = content + append_content
        return content

    def md_content(self, input_path, output_path):
        rank_desc = {
            5: """## 5分\n极度推荐，最适合聚会，原价买也不亏\n""",
            4: """# 4分\n质量优秀，是对S级游戏的补充，可适当等个8折以下的优惠。\n""",
            3: """# 3分\n在场景合适的情况下可以玩，建议等5折以下入手。\n""",
            2: """# 2分\n一般不推荐，除非你很喜欢这个游戏对应的题材或者是系列作品的粉丝。\n""",
            1: """# 1分\n浪费钱，永远别买。这个级别我一般也不会给出各个细分项的评分，因为没有意义。\n""",
        }

        current_rank = 0
        df = pd.read_excel(input_path)
        df2 = df[df["game_review"] != "待评测"].fillna("")
        text_list = []

        for row in df2.to_dict("records"):
            row_rank = int(row["rating"])
            if current_rank != row_rank:
                current_rank = row_rank
                text_list.append(rank_desc[current_rank])
            c = self.row_content(row)
            text_list.append(c)

        rating_text = "\n".join(text_list)

        md_content = f"""本评测最大的特点是，**真实**。我所写的每一款游戏都是亲自体验并组织了聚会试验其效果的，其中推荐的游戏更是经过多次反复的测试。参与聚会的既有经验丰富的老玩家，也有什么都不懂的小白，覆盖了各种可能的聚会人群场景。对特定的游戏，会在简评中说明其适合游玩的场景。如果你想要组织聚会但不知道该玩什么游戏，看本文就好了，如果有进一步的需求，可以私信沟通。

本文会持续更新，目前已评测完毕60个游戏。对于重点推荐的游戏，后续还会写更详细的单篇评测，不仅会给出全方位的评测细节，还会说明如何组织玩法以发挥出游戏的最大乐趣，另外，针对部分需要解锁要素的，还会提供解锁攻略。在文章的最后还有待评测的游戏列表，会在后续进行更新，欢迎关注，如果有其它想要评测的游戏也欢迎私信我。

我建立了一套评测体系，评测打分的等级都是有依据的。对于每个评分的等级的含义，genre的解释等，请参考我的另一篇文章:
[聚会游戏评测细则](https://zhuanlan.zhihu.com/p/449010252)

为了方便大家排序筛选，我创建了一个腾讯文档供查看：
[Switch聚会游戏评测](https://docs.qq.com/sheet/DWGhRa3ZZRmRvc0JU)

{rating_text}

## 待评测列表

已购买未评测：

* 奶油蛋糕
* 超级再跳一次
* 飞盘对决
* 马力欧高尔夫 超级冲冲冲
* 超级爆裂网球


计划购买评测：

* 口袋铁拳锦标赛 DX
* 丸霸无双
* Gang Beasts
* 极速奔跑者
* 虹色战士
* 混乱快跑
* 马里奥与索尼克在 2020 东京奥运会
* 马力欧派对：超级明星
* 主宰
* 小三角大英雄
* 超级爆裂足球
* 王牌钓手
* 这里没有英雄
* 死亡方块
* Ubongo
* 枪、血、黑手党
* 墨西哥英雄大混战
* 超级马力欧3D世界 ＋ 狂怒世界
* 新超级马力欧兄弟U 豪华版"""

        with open(output_path, "w+") as out:
            out.write(md_content)
