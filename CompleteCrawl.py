__author__ = 'chzhu'

from Utility import loop_increase
from Spider import Spider
from datetime import datetime
from Dao import Database, Task, Account
from Spider import User
from Config import ACCOUNT_NUM, TASK_NUM, ACCOUNT_CHANGE_TIME
from Utility import emphasis_print
import pymysql

def initialization():
    # get a list of user ids as tasks
    uid_list = get_tasks(TASK_NUM)
    # get a list of users as crawling accounts
    user_list = get_accounts(ACCOUNT_NUM)
    spider = Spider(user_list)

    return spider, uid_list, user_list

def get_tasks(limit):
    '''

    :param limit: specify how many tasks we are going to fetch from db
    :return: task_list: a list with uids
    '''

    db = Database()
    db.connect()

    task_list = []

    tasks = db.session.query(Task).filter(Task.is_available=='1', Task.is_deleted=='0').limit(limit)
    for t in tasks:
        t.is_available = '0'
        task_list.append(t.uid)

    db.close()

    return task_list
def get_accounts(limit):
    '''

    :param limit:
    :return: user_list: a list of User objects denoting for Sina accounts
    '''
    db = Database()
    db.connect()

    user_list = []
    users = db.session.query(Account).filter(Account.is_available=='1', Account.is_deleted=='0').limit(limit)
    for u in users:
        u.is_available = '0'
        user_list.append(User(u.account, u.passwd))

    db.close()
    return user_list

def reset(user_list, uid_list, crawled_list):
    '''

    :param user_list: accounts
    :param uid_list:  tasks
    :param crawled_list: completed tasks
    :return:
    '''
    Account.reset(user_list)
    uncrawled_list = []
    for uid in uid_list:
        if uid not in crawled_list:
            uncrawled_list.append(uid)
    Task.reset(uncrawled_list)



if __name__ == '__main__':

    print 'Initializing...'
    crawled_list = []
    spider, uid_list, user_list = initialization()

    try:
        while True:
            for uid in uid_list:
                emphasis_print('Now %d of %d accounts are working!' % (spider.main_fetcher+1, len(spider.fetchers)))
                spider.collect_user_information(uid)

                while True: # in case of connection lost
                    try:
                        spider.save()
                        break
                    except pymysql.err.OperationalError:
                        continue

                crawled_list.append(uid)
                spider.end_time = datetime.now()
                duration = spider.end_time - spider.start_time
                if duration.seconds > ACCOUNT_CHANGE_TIME:
                    spider.main_fetcher = loop_increase(spider.main_fetcher, len(spider.fetchers))
                    spider.start_time = datetime.now()
                    emphasis_print('Account changed!!!')

            print 'Complete a batch of tasks!'
            print 'Getting new tasks...'
            uid_list = get_tasks(TASK_NUM)
            if len(uid_list) == 0:
                print 'No tasks to proceed!'
                exit(-1)
    except Exception as e:
        print e.message
    finally:
        reset(user_list, uid_list, crawled_list) # reset