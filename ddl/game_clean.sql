CREATE TABLE `game_clean` (
  `code` varchar(40),
  `db_name` varchar(255) COMMENT 'db游戏名',
  `en_name` varchar(255) COMMENT '游戏名-英文',
  `jp_name` varchar(255) COMMENT '游戏名-日文',
  `cn_name` varchar(255) COMMENT '游戏名-中文',
  `num_of_players` int(4) COMMENT '支持本地最大人数',
  `jp_nsuid` varchar(20),
  `hk_nsuid` varchar(20),
  `eu_nsuid` varchar(20),
  `na_nsuid` varchar(20),
  `eu_lowest_price` decimal(10,2) COMMENT '史低价格(欧元)',
  `na_lowest_price` decimal(10,2) COMMENT '史低价格(美元)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  KEY `ix_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;





code	db_name	en_name	jp_name	cn_name	num_of_players	jp_nsuid	hk_nsuid	eu_nsuid	na_nsuid	eu_lowest_price	na_lowest_price
AEA2A	Yoshi's Crafted World (EN,FR,DE,ES,IT,NL,JA,KO,ZHCN,RU)	Yoshi's Crafted World	ヨッシークラフトワールド	耀西的手工世界	2	70010000000735	70010000018872	70010000000733	70010000000734	49.99	59.99