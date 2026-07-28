-- ============================================================
-- 日常记账APP (DailyTracker) — 数据库初始化脚本
-- 版本: V1.0
-- 数据库: account
-- 引擎: MySQL 8.0 / InnoDB
-- 说明: 建库、建表、索引、默认分类数据
-- ============================================================

-- ----------------------------
-- 0. 创建数据库
-- ----------------------------
CREATE DATABASE IF NOT EXISTS `account`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `account`;

-- ----------------------------
-- 1. users 用户表
-- 存储注册用户的基本信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id`            INT             NOT NULL AUTO_INCREMENT  COMMENT '主键',
  `username`      VARCHAR(50)     NOT NULL                 COMMENT '用户名，唯一',
  `email`         VARCHAR(100)    NOT NULL                 COMMENT '邮箱，唯一',
  `password_hash` VARCHAR(255)    NOT NULL                 COMMENT 'bcrypt 密码哈希',
  `avatar_url`    VARCHAR(500)    DEFAULT NULL             COMMENT '头像 URL',
  `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_username` (`username`),
  UNIQUE KEY `uq_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ----------------------------
-- 2. categories 分类表
-- 系统默认分类 (user_id=NULL) + 用户自定义分类
-- ----------------------------
CREATE TABLE IF NOT EXISTS `categories` (
  `id`            INT             NOT NULL AUTO_INCREMENT  COMMENT '主键',
  `user_id`       INT             DEFAULT NULL             COMMENT '所属用户，NULL=系统默认分类',
  `name`          VARCHAR(30)     NOT NULL                 COMMENT '分类名称',
  `icon`          VARCHAR(50)     NOT NULL                 COMMENT '图标 (emoji)',
  `color`         VARCHAR(7)      NOT NULL                 COMMENT '颜色 #RRGGBB',
  `type`          ENUM('income','expense') NOT NULL        COMMENT '收入/支出类型',
  `is_default`    TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '是否系统默认 0=否 1=是',
  `sort_order`    INT             NOT NULL DEFAULT 0       COMMENT '排序值，越小越靠前',
  `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_type` (`type`),
  CONSTRAINT `fk_category_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收支分类表';

-- ----------------------------
-- 3. bills 账单表
-- 每一条收入/支出记录
-- ----------------------------
CREATE TABLE IF NOT EXISTS `bills` (
  `id`            INT             NOT NULL AUTO_INCREMENT  COMMENT '主键',
  `user_id`       INT             NOT NULL                 COMMENT '所属用户',
  `type`          ENUM('income','expense') NOT NULL        COMMENT '收入/支出',
  `amount`        DECIMAL(12,2)   NOT NULL                 COMMENT '金额 (0.01 ~ 999,999,999.99)',
  `category_id`   INT             NOT NULL                 COMMENT '分类',
  `bill_date`     DATE            NOT NULL                 COMMENT '账单日期',
  `note`          VARCHAR(200)    DEFAULT NULL             COMMENT '备注',
  `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_date` (`user_id`, `bill_date`),
  KEY `idx_user_category` (`user_id`, `category_id`),
  CONSTRAINT `fk_bill_user`     FOREIGN KEY (`user_id`)     REFERENCES `users`(`id`)      ON DELETE CASCADE,
  CONSTRAINT `fk_bill_category` FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账单表';

-- ----------------------------
-- 4. budgets 预算表
-- 月度总预算 / 分类预算
-- ----------------------------
CREATE TABLE IF NOT EXISTS `budgets` (
  `id`            INT             NOT NULL AUTO_INCREMENT  COMMENT '主键',
  `user_id`       INT             NOT NULL                 COMMENT '所属用户',
  `category_id`   INT             DEFAULT NULL             COMMENT '分类，NULL=月度总预算',
  `amount`        DECIMAL(12,2)   NOT NULL                 COMMENT '预算金额',
  `month`         VARCHAR(7)      NOT NULL                 COMMENT '预算月份 YYYY-MM',
  `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_month_category` (`user_id`, `month`, `category_id`),
  KEY `idx_user_month` (`user_id`, `month`),
  CONSTRAINT `fk_budget_user`     FOREIGN KEY (`user_id`)     REFERENCES `users`(`id`)       ON DELETE CASCADE,
  CONSTRAINT `fk_budget_category` FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预算表';

-- ============================================================
-- 5. 插入系统默认分类数据
-- 根据 PRD §2.3.2 定义: 8 个支出分类 + 5 个收入分类
-- ============================================================

-- 5.1 支出分类 (8个)
INSERT INTO `categories` (`user_id`, `name`, `icon`, `color`, `type`, `is_default`, `sort_order`) VALUES
(NULL, '餐饮', '🍽️', '#E07B5A', 'expense', 1, 1),
(NULL, '交通', '🚗', '#C0826B', 'expense', 1, 2),
(NULL, '购物', '🛒', '#D4956B', 'expense', 1, 3),
(NULL, '居住', '🏠', '#B8846E', 'expense', 1, 4),
(NULL, '娱乐', '🎮', '#D4A574', 'expense', 1, 5),
(NULL, '医疗', '💊', '#E8916B', 'expense', 1, 6),
(NULL, '教育', '📚', '#C0956E', 'expense', 1, 7),
(NULL, '其他', '📌', '#B0A090', 'expense', 1, 8);

-- 5.2 收入分类 (5个)
INSERT INTO `categories` (`user_id`, `name`, `icon`, `color`, `type`, `is_default`, `sort_order`) VALUES
(NULL, '工资', '💰', '#7BA587', 'income', 1, 1),
(NULL, '兼职', '💼', '#6B9EB3', 'income', 1, 2),
(NULL, '投资', '📈', '#8B8BA7', 'income', 1, 3),
(NULL, '红包', '🧧', '#C49B7A', 'income', 1, 4),
(NULL, '其他', '📌', '#B0A090', 'income', 1, 5);

-- ============================================================
-- 执行完毕
-- ============================================================
-- 验证:
--   SHOW DATABASES;          — 确认 account 库已创建
--   USE account; SHOW TABLES; — 确认 4 张表已创建
--   SHOW CREATE TABLE users;  — 查看表结构
--   SELECT * FROM categories; — 查看默认分类数据
