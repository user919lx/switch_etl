# Switch ETL(WIP)

任天堂Eshop爬虫数据的后续清洗工作，请结合[Eshop爬虫](https://github.com/user919lx/crawler)使用
尚在建设中

## 使用前的配置

* 修改位于`switch_etl/settings.py`下的`MYSQL_CONFIG`，填入你自己的MySQL数据库参数
* 安装pipenv，并切换到项目环境下使用，已配置好`Pipfile`
* 查看`ddl`，复制ddl建表



## 两个额外的爬虫

因为处理有些麻烦所以放到本项目中

* game_db:从gametdb.com下载数据存入`game_raw` ，此网站的数据较全且很方便获取，可以很方便地通过code来连接不同region的同一个游戏信息
* game_na:获取美区的游戏信息，存入`game_raw`



## 使用方法

使用pipenv进入项目环境
在项目根目录下执行 `python3 cli.py {command}`

可用命令如下

* game-pipeline:清洗对应region，存入数据库表，需要加上参数 `-r {region}`来指定region
* na-spider:启动美区游戏信息爬虫，存入`game_raw`,region='na'
* db-spider:从gametdb.com获取数据，存入`game_raw`,region='db'
* game-mult:获取游戏的人数上限信息

其余部分还在开发中，请勿使用

## 定时任务

项目使用Airflow进行每日调度，包括另一个项目的爬虫在内，详细依赖关系设置可参考`dags/eshop.py`
