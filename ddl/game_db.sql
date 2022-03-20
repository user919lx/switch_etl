CREATE TABLE `game_db` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(40),
  `region` varchar(40),
  `languages` varchar(255) COMMENT '语言',
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
  UNIQUE KEY `uk` (`code`),
  KEY `ix_created_at` (`created_at`),
  KEY `ix_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


