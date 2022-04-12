CREATE TABLE `game_mult` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `en_name` varchar(255) COMMENT '游戏名-英文',
  `local_num_of_players` varchar(100) COMMENT '支持本地人数范围',
  `wireless_num_of_players` varchar(100) COMMENT '无线人数范围',
  `online_num_of_players` varchar(100) COMMENT '线上人数范围',
  `local_max_num_of_players` int(4) COMMENT '本地最大人数',
  `wireless_max_num_of_players` int(4) COMMENT '无线最大人数',
  `online_max_num_of_players` int(4) COMMENT '线上最大人数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk` (`en_name`),
  KEY `ix_created_at` (`created_at`),
  KEY `ix_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
