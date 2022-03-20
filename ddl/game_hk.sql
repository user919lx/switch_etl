CREATE TABLE `game_hk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unique_id` varchar(100) COLLATE utf8mb4_unicode_ci,
  `nsuid` varchar(20),
  `name` varchar(255),
  `name_sc` varchar(255),
  `release_date` date,
  `url` varchar(255),
  `maker_publisher` varchar(255),
  `product_code` varchar(255),
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk` (`unique_id`),
  KEY `ix_created_at` (`created_at`),
  KEY `ix_updated_at` (`updated_at`),
  KEY `ix_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;