__author__ = 'chzhu'

import Spider
from Spider import Spider as SP
from Dao import Task

if __name__ == '__main__':

    user_1 = Spider.User('helloh622@gmail.com', 'hello1234567890')
    user_2 = Spider.User('1352875156@qq.com', 'w1127401044')
    user_list = [user_1, user_2]

    sp = SP(user_list)

    uid_list = Task.get_all()

    for uid in uid_list:
        sp.collect_user_profiles_only(uid)
        sp.save_only_profile()
