__author__ = 'chzhu'

from Weibo import Weibo
from Utility import emphasis_print
from Parser import HtmlParser

class User(object):
    def __init__(self, account, password):
        self.acct = account
        self.pswd = password

class Spider(object):
    def __init__(self, user_list, cookie_list=None):
        """

        :param user_list: a list of users
        :param cookie_list: a list of cookies, default to be None
        :return:
        """
        if cookie_list is not None:
            self.cookies = cookie_list
            self.fetchers = []
            self.get_fetchers_by_cookie()
            self.parser = HtmlParser()
        else: # need login by users
            self.users = user_list
            self.fetchers = []
            self.get_fetchers_by_user()
            self.parser = HtmlParser()

        self.main_fetcher = 0 # current fetcher index
        self.follower_list = [] # store followers


    def collect_user_information(self, uid):
        self.get_followers(uid)
        self.get_followees(uid)
        self.get_timelines(uid)
        self.get_profile(uid)


    def get_followers(self, uid):
        fetcher = self.fetchers[self.main_fetcher]

        pass


    def get_fetchers_by_user(self):
        """
        initialize self.fetchers by user
        :return:
        """
        wb = Weibo()
        for user in self.users:
            fetcher = wb.login(user)
            if fetcher is not None:
                emphasis_print('User: %s login success!' % (user.acct,))
                self.fetchers.append(fetcher)
            else:
                emphasis_print('User: %s login failure!' % (user.acct,))
        print 'Get all fetchers by users!'
    def get_fetchers_by_cookie(self):
        """
        initialize self.fetchers by cookie
        :return:
        """
        pass