CREATE TABLE `game_db` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COMMENT '游戏名',
  `demo_available` varchar(100) COMMENT 'demo 可用地区',
  `released` varchar(255) COMMENT '语言',
  `name` varchar(255) COMMENT '游戏名',
  `en_name` varchar(255) COMMENT '游戏名-英文',
  `jp_name` varchar(255) COMMENT '游戏名-日文',
  `cn_name` varchar(255) COMMENT '游戏名-中文',
  `developer` varchar(255),
  `publisher` varchar(255),
  `genres` varchar(255),
  `esrb_rating` varchar(100),
  `esrb_rating_desc` varchar(255),
  `pegi_rating` varchar(100),
  `pegi_rating_desc` varchar(255),
  `num_of_players` int(4) COMMENT '支持本地最大人数',
  `num_of_online_players` int(4) COMMENT '支持线上最大人数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk` (`name`),
  KEY `ix_created_at` (`created_at`),
  KEY `ix_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

released	string	发售日期	多个地区分开，使用json，并且把日期标准化
genre	string	游戏类型	多个类型，使用逗号隔开
number_of_players	string	玩家人数	多类分开，使用json
developer	string	开发商	
publisher	string	发行商	
download_size	string	下载大小	
metacritic_url	string	MC评分url	
metacritic_media	int	MC媒体评分	
metacritic_user	float	MC用户评分	
how_long_to_beat_url	string	游玩时长url	
how_long_to_beat	string	游玩时长	多类分开，使用json
esrb_rating	string	ESRB评级	
play_modes	string	游玩模式	
languages	string	支持语言	
history_price	blob	历史价格	json格式转blob
