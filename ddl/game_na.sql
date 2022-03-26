CREATE TABLE `game_na` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unique_id` varchar(100) COLLATE utf8mb4_unicode_ci,
  `object_id` varchar(40),
  `nsuid` varchar(20),
  `name` varchar(255),
  `game_desc` text,
  `release_date` date,
  `url` varchar(255),
  `img` varchar(255),
  `boxart` varchar(255),
  `developers` varchar(255),
  `publishers` varchar(255),
  `genres` varchar(255),
  `price` decimal(10,2) COMMENT '建议售价(美元)',
  `lowest_price` decimal(10,2) COMMENT '史低价格(美元)',
  `price_range` varchar(100),
  `esrb_rating` varchar(100),
  `num_of_players` int(4) COMMENT '支持本地最大人数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk` (`unique_id`),
  KEY `ix_created_at` (`created_at`),
  KEY `ix_updated_at` (`updated_at`),
  KEY `nsu_idx` (`nsuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


