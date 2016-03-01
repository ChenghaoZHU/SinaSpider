/*
Navicat MySQL Data Transfer

Source Server         : DBS_Master01
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : sina_weibo

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-03-01 13:21:52
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for dump_time
-- ----------------------------
DROP TABLE IF EXISTS `dump_time`;
CREATE TABLE `dump_time` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for weibo_accounts
-- ----------------------------
DROP TABLE IF EXISTS `weibo_accounts`;
CREATE TABLE `weibo_accounts` (
  `account` varchar(50) NOT NULL,
  `passwd` varchar(20) NOT NULL DEFAULT 'tttt5555',
  `is_available` enum('1','0') NOT NULL DEFAULT '1',
  `is_deleted` enum('1','0') DEFAULT '0',
  PRIMARY KEY (`account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for weibo_educations
-- ----------------------------
DROP TABLE IF EXISTS `weibo_educations`;
CREATE TABLE `weibo_educations` (
  `id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `uid` varchar(20) NOT NULL,
  `type` varchar(20) DEFAULT NULL,
  `school_name` varchar(50) NOT NULL,
  `time_period` varchar(50) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4407 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for weibo_followees
-- ----------------------------
DROP TABLE IF EXISTS `weibo_followees`;
CREATE TABLE `weibo_followees` (
  `uid` varchar(20) NOT NULL,
  `fee_uid` varchar(80) NOT NULL,
  `fee_name` varchar(50) DEFAULT NULL,
  `fee_profile_img_url` varchar(100) DEFAULT NULL,
  `fee_description` varchar(512) DEFAULT NULL,
  `fee_gender` enum('M','F') DEFAULT NULL,
  `fee_location` varchar(50) DEFAULT NULL,
  `fee_by` varchar(20) DEFAULT NULL,
  `fee_followee_num` int(10) unsigned DEFAULT NULL,
  `fee_follower_num` int(10) unsigned DEFAULT NULL,
  `fee_weibo_num` int(11) unsigned DEFAULT NULL,
  `fee_verified_type` enum('0','1','2') NOT NULL,
  `fee_is_vip` enum('0','1') NOT NULL,
  `fee_vip_level` int(11) DEFAULT NULL,
  `fee_is_daren` enum('0','1') NOT NULL,
  `fee_is_taobao` enum('1','0') NOT NULL,
  `fee_is_suishoupai` enum('0','1') NOT NULL,
  `fee_is_vlady` enum('0','1') NOT NULL,
  `fee_timestamp` datetime NOT NULL,
  PRIMARY KEY (`uid`,`fee_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- ----------------------------
-- Table structure for weibo_followers
-- ----------------------------
DROP TABLE IF EXISTS `weibo_followers`;
CREATE TABLE `weibo_followers` (
  `uid` varchar(20) NOT NULL,
  `fer_uid` varchar(80) NOT NULL,
  `fer_name` varchar(50) DEFAULT NULL,
  `fer_profile_img_url` varchar(100) DEFAULT NULL,
  `fer_description` varchar(512) DEFAULT NULL,
  `fer_gender` enum('M','F') DEFAULT NULL,
  `fer_location` varchar(50) DEFAULT NULL,
  `fer_by` varchar(20) DEFAULT NULL,
  `fer_followee_num` int(10) unsigned NOT NULL,
  `fer_follower_num` int(10) unsigned NOT NULL,
  `fer_weibo_num` int(10) unsigned NOT NULL,
  `fer_is_vip` enum('0','1') NOT NULL,
  `fer_vip_level` int(11) DEFAULT NULL,
  `fer_verified_type` enum('0','1','2') NOT NULL,
  `fer_is_daren` enum('0','1') NOT NULL,
  `fer_is_taobao` enum('0','1') NOT NULL,
  `fer_is_suishoupai` enum('0','1') NOT NULL,
  `fer_is_vlady` enum('0','1') NOT NULL,
  `fer_timestamp` datetime NOT NULL,
  PRIMARY KEY (`uid`,`fer_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- ----------------------------
-- Table structure for weibo_jobs
-- ----------------------------
DROP TABLE IF EXISTS `weibo_jobs`;
CREATE TABLE `weibo_jobs` (
  `uid` varchar(20) NOT NULL,
  `company` varchar(50) NOT NULL,
  `location` varchar(50) DEFAULT NULL,
  `occupation` varchar(50) DEFAULT NULL,
  `time_period` varchar(50) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`uid`,`company`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for weibo_parameters
-- ----------------------------
DROP TABLE IF EXISTS `weibo_parameters`;
CREATE TABLE `weibo_parameters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `i` varchar(30) DEFAULT NULL,
  `s` varchar(30) DEFAULT NULL,
  `gsid` varchar(140) DEFAULT NULL,
  `is_available` enum('0','1') DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`i`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for weibo_tasks
-- ----------------------------
DROP TABLE IF EXISTS `weibo_tasks`;
CREATE TABLE `weibo_tasks` (
  `uid` varchar(20) NOT NULL,
  `is_available` enum('0','1') DEFAULT '1',
  `is_deleted` enum('0','1') DEFAULT '0',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for weibo_timelines
-- ----------------------------
DROP TABLE IF EXISTS `weibo_timelines`;
CREATE TABLE `weibo_timelines` (
  `mid` varchar(30) NOT NULL,
  `encrypt_mid` varchar(30) DEFAULT NULL,
  `uid` varchar(20) DEFAULT NULL,
  `retweet_num` int(10) unsigned DEFAULT NULL,
  `comment_num` int(10) unsigned DEFAULT NULL,
  `favourite_num` int(10) unsigned DEFAULT NULL,
  `created_at` varchar(50) DEFAULT NULL,
  `from` varchar(50) DEFAULT NULL,
  `text` varchar(1024) DEFAULT NULL,
  `entity` varchar(2048) DEFAULT NULL,
  `source_mid` varchar(30) DEFAULT NULL,
  `source_uid` varchar(20) DEFAULT NULL,
  `mentions` varchar(1024) DEFAULT NULL,
  `check_in` varchar(1024) DEFAULT NULL,
  `check_in_url` varchar(512) DEFAULT NULL,
  `is_deleted` enum('1','0') NOT NULL DEFAULT '0',
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`mid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- ----------------------------
-- Table structure for weibo_users
-- ----------------------------
DROP TABLE IF EXISTS `weibo_users`;
CREATE TABLE `weibo_users` (
  `uid` varchar(20) NOT NULL,
  `screen_name` varchar(50) NOT NULL,
  `real_name` varchar(30) DEFAULT NULL,
  `location` varchar(30) DEFAULT NULL,
  `gender` enum('M','F') DEFAULT NULL,
  `sexual_orientation` varchar(20) DEFAULT NULL,
  `relationship_status` varchar(20) DEFAULT NULL,
  `birthday` varchar(20) DEFAULT NULL,
  `blood_type` varchar(10) DEFAULT NULL,
  `blog` varchar(255) DEFAULT NULL,
  `description` varchar(512) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `QQ` varchar(20) DEFAULT NULL,
  `MSN` varchar(50) DEFAULT NULL,
  `tag` varchar(1024) DEFAULT NULL,
  `followee_num` int(10) unsigned DEFAULT NULL,
  `follower_num` int(10) unsigned DEFAULT NULL,
  `weibo_num` int(10) unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `profile_img_url` varchar(255) NOT NULL,
  `domain_id` varchar(20) NOT NULL,
  `domain_name` varchar(100) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `experience` int(11) DEFAULT NULL,
  `credit_level` varchar(10) DEFAULT NULL,
  `credit_point` int(11) DEFAULT NULL,
  `credit_history` varchar(1024) DEFAULT NULL,
  `is_vip` enum('1','0') NOT NULL,
  `vip_level` int(11) DEFAULT NULL,
  `is_yearly_pay` enum('1','0') DEFAULT NULL,
  `is_verified` enum('1','0') NOT NULL,
  `verified_reason` varchar(1024) DEFAULT NULL,
  `is_daren` enum('1','0') NOT NULL,
  `daren_type` varchar(10) DEFAULT NULL,
  `daren_point` float DEFAULT NULL,
  `daren_interest` varchar(1024) DEFAULT NULL,
  `is_taobao` enum('1','0') NOT NULL,
  `not_exist` enum('1','0') NOT NULL DEFAULT '0',
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
