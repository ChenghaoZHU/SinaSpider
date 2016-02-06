#-*- coding: UTF-8 -*-
__author__ = 'chzhu'

import Spider
from Spider import Spider as SP
from Dao import Task, Account

if __name__ == '__main__':

    # user_1 = Spider.User('shimiaohuirv1203@163.com', 'a123456')
    # user_2 = Spider.User('1352875156@qq.com', 'w1127401044')
    # user_list = [user_1, user_2]
    #
    # sp = SP(user_list)
    #
    # uid_list = Task.get_all()
    #
    # for uid in uid_list:
    #     sp.collect_user_profiles_only(uid)
    #     sp.save_only_profile()

    user = Spider.User('xded0o@mailnesia.com', 'pp9999')
    user_list = [user]
    sp = SP(user_list)

    from Utility import open_url

    uid = '2971804112'
    url = 'http://www.weibo.com/aj/v6/user/newcard?ajwvr=6&id=%s&type=0&refer_flag=0000011002_&callback=STK_145465715259821'
    r = open_url(sp.fetchers[sp.main_fetcher], url%uid)
    print 'dd'