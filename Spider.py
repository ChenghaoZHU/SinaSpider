__author__ = 'chzhu'

from Weibo import Weibo
from Utility import emphasis_print, open_url
from Parser import HtmlParser
from datetime import datetime

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
        self.followee_list = [] # store followees

    def collect_user_information(self, uid):
        print 'Collecting information for User %s...' % (uid,)
        pid = self.get_pid(uid)

        # self.get_followers(pid)
        print 'Followers crawled.'
        self.get_followees(pid)
        print 'Followees crawled.'
        self.get_timelines(uid)
        self.get_profile(uid)

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
        print 'Get all fetchers by users!\n'
    def get_fetchers_by_cookie(self):
        """
        initialize self.fetchers by cookie
        :return:
        """
        pass

    def get_pid(self, uid):
        """

        :param uid:
        :return: corresponding pid
        """
        fetcher = self.fetchers[self.main_fetcher]
        url = 'http://www.weibo.com/u/%s' % (uid,)
        while True:
            html = open_url(fetcher, url)
            pid = self.parser.parse_pid(html)
            if pid is not None:
                return pid

    def get_followers(self, pid):
        fetcher = self.fetchers[self.main_fetcher]
        url = 'http://www.weibo.com/p/' + pid + '/follow?relate=fans&from=' + pid[:6] + '&wvr=6&mod=headfans#place'
        while True:
            html = open_url(fetcher, url)
            fer_page_num = self.get_follower_page_num(html)
            if fer_page_num is not None:
                break

        if fer_page_num == 0:
            print 'He/She does not have any followers.'
            return
        else:
            print 'Getting follower page 1 of %d...' % (fer_page_num,)
            followers = self.parser.parse_followers(html, pid, datetime.now())
            self.follower_list.extend(followers) # followers cannot be None since it's been tested in self.get_follower_page_num(html)-> self.parser.parse_follower_page_num(html)
            if fer_page_num == 1:
                return
            for i in xrange(2, fer_page_num+1):
                while True:
                    url = 'http://www.weibo.com/p/%s/follow?relate=fans&from=%s&wvr=6&mod=headfans&page=%d#place' % (pid, pid[:6], i)
                    print 'Getting follower page %d of %d...' % (i, fer_page_num)
                    html = open_url(fetcher, url)
                    print 'Sleeping...'
                    followers = self.parser.parse_followers(html, pid, datetime.now())
                    if followers is None: # dirty html
                        continue
                    self.follower_list.extend(followers)
                    break
    def get_follower_page_num(self, html):
        """
        get the number of follower pages, up to 5.
        :param html:
        :return:
        """
        fer_pnum = self.parser.parse_follower_page_num(html)
        if fer_pnum is None:
            return None
        if fer_pnum > 6:
            fer_pnum = 5
        return fer_pnum

    def get_followees(self, pid):
        fetcher = self.fetchers[self.main_fetcher]
        url = 'http://www.weibo.com/p/' + pid + '/follow?from=page_' + pid[:6] + '&wvr=6&mod=headfollow#place'

        while True:
            html = open_url(fetcher, url)
            fee_page_num = self.get_followee_page_num(html)
            if fee_page_num is not None:
                break

        if fee_page_num == 0:
            print 'He/She does not follow any one.'
            return
        else:
            print 'Getting followee page 1 of %d...' % (fee_page_num,)
            followees = self.parser.parse_followees(html, pid, datetime.now())
            self.followee_list.extend(followees) # followees cannot be None since it's been tested in self.get_followee_page_num(html)-> self.parser.parse_followee_page_num(html)
            if fee_page_num == 1:
                return
            for i in xrange(2, fee_page_num+1):
                while True:
                    url = 'http://www.weibo.com/p/%s/follow?from=page_%s&wvr=6&mod=headfollow&page=%d#place' % (pid, pid[:6], i)
                    print 'Getting followee page %d of %d...' % (i, fee_page_num)
                    html = open_url(fetcher, url)
                    print 'Sleeping...'
                    followees = self.parser.parse_followees(html, pid, datetime.now())
                    if followees is None: # dirty html
                        continue
                    self.followee_list.extend(followees)
                    break
    def get_followee_page_num(self, html):
        """
        get the number of followee pates, no value more than five
        :param html:
        :return:
        """
        fee_pnum = self.parser.parse_followee_page_num(html)
        if fee_pnum is None:
            return None
        if fee_pnum > 6:
            fee_pnum = 5
        return fee_pnum


