__author__ = 'chzhu'

LOG_FILE = 'Log/log.txt'

SLEEP_BETWEEN_2FPAGES = 15 # also for parts in one timeline page
SLEEP_BETWEEN_TIMELINE_PAGES = 45
SLEEP_WHEN_EXCEPTION = 60*10

ACCOUNT_CHANGE_TIME = 30*60

TABLES = {
    'followee':'weibo_followees',
    'follower':'weibo_followers',
    'timeline':'weibo_timelines',
    'job':'weibo_jobs',
    'education':'weibo_educations',
    'user':'weibo_users',
    'account':'weibo_accounts',
    'task':'weibo_tasks',
    'parameter':'weibo_parameters'
}

DB_USER = 'root'
DB_PASSWD = 'admin'
DB_HOST = '127.0.0.1'
DB_DATABASE = 'sina_weibo'
DB_CHARSET = 'utf8mb4'

ACCOUNT_NUM = 3
TASK_NUM = 100

OS = 1 # 0 is for Windows, 1 is for Linux