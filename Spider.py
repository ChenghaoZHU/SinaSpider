# encoding=utf8
__author__ = 'chzhu'

from Weibo import Weibo
from Utility import emphasis_print, open_url
from Parser import HtmlParser
from datetime import datetime
import urllib
import json

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
        self.timeline_list = [] # store timelines
        self.profile_list = [] # store profiles

    def collect_user_information(self, uid):
        print 'Collecting information for User %s...' % (uid,)
        pid = self.get_pid(uid)

        # self.get_followers(pid)
        print 'Followers crawled.'
        # self.get_followees(pid)
        print 'Followees crawled.'
        # self.get_timelines(uid)
        print 'Timelines crawled.'
        self.get_profile(pid)
        print 'Pofile crawled.'

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
    def get_timelines(self, uid):
        """
        get all timelines of user with this uid
        :param uid:
        :return:
        """
        fetcher = self.fetchers[self.main_fetcher]

        timeline_page_num, first_page = self.get_timeline_page_num(uid)
        if timeline_page_num == 0:
            print 'No any posts.'
            return
        else:
            for pt in first_page:
                self.timeline_list.extend(self.parser.parse_timelines(pt, uid, datetime.now()))
            if timeline_page_num == 1:
                return

        timelines = []
        for pnum in xrange(2, timeline_page_num+1):
            for bnum in xrange(3):
                    html = self.fetch_timelines_by_page_bar(uid, pnum, bnum)
                    if html is not None:
                        timelines = self.parser.parse_timelines(html, uid, datetime.now())
                        self.timeline_list.extend(timelines)
    def fetch_timelines_by_page_bar(self, uid, pnum, bnum):
        """
        fetch timelines by specifying page number and bar number
        :param uid:
        :param pnum: page number
        :param bnum: bar number
        :return: html containing timelines or None if there are no timelines
        """
        body = { # 这个是有抓包得出的，因为新浪微博用了瀑布流动态加载，所以不能一次性得到一页中所有信息
            '__rnd':1343647638078,
            '_k':1343647471134109,
            '_t':0,
            'count':15,
            'end_id':3473519214542343,
            'max_id':3473279479126179,
            'page':1,
            'pagebar':1,
            'pre_page':1,
            'uid':uid
       }

        body['page'] = pnum

        if bnum == 0:
            body['count'] = '50'
            body['pagebar'] = ''
            body['pre_page'] = pnum-1
        elif bnum == 1:
            body['count'] = '15'
            body['pagebar'] = '0'
            body['pre_page'] = pnum
        elif bnum == 2:
            body['count'] = '15'
            body['pagebar'] = '1'
            body['pre_page'] = pnum

        url = 'http://weibo.com/aj/mblog/mbloglist?' + urllib.urlencode(body)
        while True:
            try:
                print 'Getting timeline page %d part %d...' % (pnum, bnum+1) # bnum starts with zero up to two
                jsn_data = open_url(self.fetchers[self.main_fetcher], url)
                print 'Sleeping...'

                data = json.loads(jsn_data)
                html = data['data']
                if u'WB_feed_type SW_fun S_line2' in html:
                    return html
                else:
                    return None
            except Exception as e:
                print e
                continue
    def get_timeline_page_num(self, uid):
        """

        :param uid:
        :return: page number and one or two pages, which will decrease accesses to Sina server
        """
        htmls = [] # keep the pages to decrease accesses to Sina
        while True:
            first_page_head = self.fetch_timelines_by_page_bar(uid, 1, 0)
            if first_page_head is None: # no any posts
                return 0, htmls
            else:
                htmls.append(first_page_head)

            first_page_body = self.fetch_timelines_by_page_bar(uid, 1, 1)
            if first_page_body is None:
                return 1, htmls
            else:
                htmls.append(first_page_body)

            first_page_tail = self.fetch_timelines_by_page_bar(uid, 1, 2)
            if first_page_tail is None: # just one page of timelines
                return 1, htmls
            else:
                htmls.append(first_page_tail)

            pnum = self.parser.parse_timeline_page_num(first_page_tail) # this page number is not accurate, so we will recount it in the next step
            if pnum is None or pnum == 1:
                return 1, htmls

            while True:
                url = 'http://www.weibo.com/%s?page=%d&pids=Pl_Content_HomeFeed' % (uid, pnum)
                test_html = open_url(self.fetchers[self.main_fetcher], url)
                no_post = 'W_icon icon_warnB'
                if no_post in test_html:
                    pnum -= 1 # fixing page number
                else:
                    print 'Sleeping...'
                    break
            return pnum, htmls
    def get_profile(self, pid):
        '''
        get profile information for User marked with pid
        :param pid: page id
        :return:
        '''
        fetcher = self.fetchers[self.main_fetcher]
        url = 'http://www.weibo.com/p/%s/info?mod=pedit_more' % (pid,)

        uid = pid[6:]
        is_taobao = None
        while is_taobao is None:
            is_taobao = self.is_taobao(uid) # get taobao information in advance

        profile = None
        while profile is None:
            html = open_url(fetcher, url)
            profile = self.parser.parse_profile(html, pid, is_taobao, datetime.now())
        self.profile_list.append(profile)
    def is_taobao(self, uid):
        '''

        :param uid: user ID
        :return: a boolean value ('1' or '0') indicating whether user is a taobao shopkeeper
        '''
        fetcher = self.fetchers[self.main_fetcher]
        url = 'http://www.weibo.com/u/' + uid
        html = open_url(fetcher, url)

        return self.parser.parse_is_taobao(html)



