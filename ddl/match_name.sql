CREATE TABLE `match_name` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cn_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jp_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `en_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jp_release_date` date,
  `na_release_date` date,
  `eu_release_date` date,
  `hk_release_date` date,
  `tw_release_date` date,
  `has_cn` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`cn_name`),
  KEY `ix_created_at` (`created_at`),
  KEY `ix_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


