__author__ = 'chzhu'

import Spider
from Spider import Spider as SP
import Weibo

if __name__ == '__main__':

    user_1 = Spider.User('helloh622@gmail.com', 'hello1234567890')
    user_2 = Spider.User('1352875156@qq.com', 'w1127401044')
    user_list = [user_1, user_2]
    # fetcher_1 = Weibo.Weibo().login(user_1)
    # fetcher_2 = Weibo.Weibo().login(user_2)
    #
    # url = 'http://www.weibo.com/u/1934183965?from=feed&loc=nickname'

    # if fetcher_1 is not None:
    #     html = fetcher_1.open(url).read()
    #     print html
    # if fetcher_2 is not None:
    #     html = fetcher_2.open(url).read()
    #     print html

    sp = SP(user_list)