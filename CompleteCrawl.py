__author__ = 'chzhu'

from Utility import loop_increase
from Spider import Spider
from datetime import datetime

def initialization():
    # get a list of user ids as tasks
    uid_list = get_uid()
    # get a list of users as crawling accounts
    user_list = get_users()
    spider = Spider(user_list)

    return spider, uid_list



if __name__ == '__main__':

    print 'Initializing...'
    spider, uid_list = initialization()

    start_time = datetime.now()
    while True:
        for uid in uid_list:
            print 'Collecting user information for UID: %s...' % (uid,)
            spider.collect_user_information(uid)
            end_time = datetime.now()
            duration = end_time - start_time
            if duration.minute > 30:
                spider.main_fetcher = loop_increase(spider.main_fetcher, len(spider.fetchers))
                start_time = datetime.now()

        print 'Complete a batch of tasks!'
        print 'Getting new tasks...'
        uid_list = get_uid()