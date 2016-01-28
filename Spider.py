# encoding=utf8
__author__ = 'chzhu'

from Weibo import Weibo
from Utility import emphasis_print, open_url
from Parser import HtmlParser
from datetime import datetime
import urllib
import json
from Log import logger as log
import time, random
import Config
from Dao import Database
import Dao

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
            self.database = Database()

        self.main_fetcher = 0 # current fetcher index
        self.follower_list = [] # store followers
        self.followee_list = [] # store followees
        self.timeline_list = [] # store timelines
        self.profile_list = [] # store profiles

    def ban_account(self):

        account = self.users[self.main_fetcher].acct
        Dao.Account.ban(account)

        self.users.pop(self.main_fetcher)
        self.fetchers.pop(self.main_fetcher)
        if self.main_fetcher == len(self.fetchers):
            self.main_fetcher = 0


    def collect_user_information(self, uid):
        print 'Collecting information for User %s...' % (uid,)
        pid = self.get_pid(uid)
        if pid == '':
            print 'User does not exist!'
            self.set_user_deleted_by_uid(uid)
            return 404

        self.get_followers(pid)
        print 'Followers crawled.'
        self.get_followees(pid)
        print 'Followees crawled.'
        self.get_timelines(uid)
        print 'Timelines crawled.'
        self.get_profile(pid)
        print 'Pofile crawled.'

    def collect_user_profiles_only(self, uid):
        print 'Collecting profile for User %s...' % (uid,)
        pid = self.get_pid(uid)
        if pid == '':
            print 'User does not exist!'
            self.set_user_deleted_by_uid(uid)
            return 404
        self.get_profile(pid)
        print 'Profile crawled.'

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
            else:
                log.error('Cannot get pid for uid:%s' % (uid,))
                time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))


    def get_followers(self, pid):

        url = 'http://www.weibo.com/p/' + pid + '/follow?relate=fans&from=' + pid[:6] + '&wvr=6&mod=headfans#place'
        while True:
            fetcher = self.fetchers[self.main_fetcher]
            html = open_url(fetcher, url)
            uid = self.parser.parse_uid(html)
            if uid == -1:
                self.ban_account()
                if len(self.fetchers) == 0:
                    raise Exception('No valid account!')
                continue
            fer_page_num = self.get_follower_page_num(html)
            if fer_page_num is not None:
                break
            else:
                log.warning('Cannot get total follower page number for pid:%s' % (pid,))
                time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))

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
                    time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))
                    followers = self.parser.parse_followers(html, pid, datetime.now())
                    if followers is None: # dirty html
                        log.warning('Cannot parse follower page - pid:%s, page num:%d' % (pid, i))
                        time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))
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

        url = 'http://www.weibo.com/p/' + pid + '/follow?from=page_' + pid[:6] + '&wvr=6&mod=headfollow#place'

        while True:
            fetcher = self.fetchers[self.main_fetcher]
            html = open_url(fetcher, url)
            uid = self.parser.parse_uid(html)
            if uid == -1:
                self.ban_account()
                if len(self.fetchers) == 0:
                    raise Exception('No valid account!')
                continue
            fee_page_num = self.get_followee_page_num(html)
            if fee_page_num is not None:
                break
            else:
                log.warning('Cannot get followee page total number - pid:%s' % (pid,))
                time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))

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
                    time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))
                    followees = self.parser.parse_followees(html, pid, datetime.now())
                    if followees is None: # dirty html
                        log.warning('Cannot parse followee page correctly - pid:%s' % (pid,))
                        time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))
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
                print 'He/She just has one page timeline.'
                return

        timelines = []
        for pnum in xrange(2, timeline_page_num+1):
            print 'There are totally %d timeline pages.' % (timeline_page_num,)
            for bnum in xrange(3):
                html = self.fetch_timelines_by_page_bar(uid, pnum, bnum)
                time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))
                if html is not None:
                    timelines = self.parser.parse_timelines(html, uid, datetime.now())
                    self.timeline_list.extend(timelines)
            time.sleep(random.randint(Config.SLEEP_BETWEEN_TIMELINE_PAGES, 2*Config.SLEEP_BETWEEN_TIMELINE_PAGES))

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
                if self.parser.is_frozen(jsn_data):
                    self.ban_account()
                    if len(self.fetchers) == 0:
                        raise Exception('No valid account!')
                    continue

                data = json.loads(jsn_data)
                html = data['data']
                if u'WB_feed_type SW_fun S_line2' in html:
                    return html
                else:
                    return None
            except Exception as e:
                if 'No valid account!' in e.message:
                    raise e
                log.warning(e.message)
                time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))
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

            time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))

            first_page_body = self.fetch_timelines_by_page_bar(uid, 1, 1)
            if first_page_body is None:
                return 1, htmls
            else:
                htmls.append(first_page_body)

            time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))

            first_page_tail = self.fetch_timelines_by_page_bar(uid, 1, 2)
            if first_page_tail is None: # just one page of timelines
                return 1, htmls
            else:
                htmls.append(first_page_tail)

            time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))

            pnum = self.parser.parse_timeline_page_num(first_page_tail) # this page number is not accurate, so we will recount it in the next step
            if pnum is None or pnum == 1:
                return 1, htmls

            while True:
                url = 'http://www.weibo.com/%s?page=%d&pids=Pl_Content_HomeFeed' % (uid, pnum)
                test_html = open_url(self.fetchers[self.main_fetcher], url)
                time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))
                no_post = 'W_icon icon_warnB'
                if no_post in test_html:
                    pnum -= 1 # fixing page number
                else:
                    break
            return pnum, htmls
    def get_profile(self, pid):
        '''
        get profile information for User marked with pid
        :param pid: page id
        :return:
        '''

        url = 'http://www.weibo.com/p/%s/info?mod=pedit_more' % (pid,)

        uid = pid[6:]
        is_taobao = None
        while is_taobao is None:
            is_taobao = self.is_taobao(uid) # get taobao information in advance
            if is_taobao == -1:
                self.ban_account()
                if len(self.fetchers) == 0:
                    raise Exception('No valid account!')
                is_taobao = None
            time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))

        profile = None
        print 'Getting profile page...'
        while profile is None:
            fetcher = self.fetchers[self.main_fetcher]
            html = open_url(fetcher, url)
            if self.parser.parse_uid(html) == -1:
                self.ban_account()
                if len(self.fetchers) == 0:
                    raise Exception('No valid account!')
                continue
            profile = self.parser.parse_profile(html, pid, is_taobao, datetime.now())
            time.sleep(random.randint(Config.SLEEP_BETWEEN_2FPAGES, 2*Config.SLEEP_BETWEEN_2FPAGES))
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

    def save(self):
        '''
        save crawled information to DB
        :return:
        '''



        self.transformation()
        self.clear_null_data() # this function must be called after self.transformation

        self.database.connect()

        for fee in self.followee_list:
            self.database.session.merge(Dao.Followee(fee))
        for fer in self.follower_list:
            self.database.session.merge(Dao.Follower(fer))
        for tl in self.timeline_list:
            tl['text'] = tl['text'].replace('', ' ') #  is /001, so it's necessary to eliminate it
            tl['text'] = tl['text'].replace('\r', ' ').replace('\n', ' ') # remove all the linefeed
            self.database.session.merge(Dao.Timeline(tl))
        for pf in self.profile_list:
            for jb in pf['Job']:
                self.database.session.merge(Dao.Job(jb))
            for edu in pf['Education']:
                self.database.session.merge(Dao.Education(edu))

            del pf['Job']
            del pf['Education']

            self.database.session.merge(Dao.User(pf))

        self.clear_buffer()


        self.database.close()

    def save_only_profile(self):

        self.transformation()
        self.clear_null_data() # this function must be called after self.transformation

        self.database.connect()

        for pf in self.profile_list:
            for jb in pf['Job']:
                self.database.session.merge(Dao.Job(jb))
            for edu in pf['Education']:
                self.database.session.merge(Dao.Education(edu))

            del pf['Job']
            del pf['Education']

            self.database.session.merge(Dao.User(pf))

        self.clear_buffer()


        self.database.close()


    def transformation(self):
        '''
        transfer keys of self.followee_list, self.follower_list, self.timeline_list and self.profile_list to fit field names in database
        :return:
        '''

        for fee in self.followee_list:
            fee['uid'] = fee.pop('uid')
            fee['fee_uid'] = fee.pop('fee_uid')
            fee['fee_name'] = fee.pop('name')
            fee['fee_profile_img_url'] = fee.pop('profile_img')
            fee['fee_description'] = fee.pop('description')
            fee['fee_gender'] = fee.pop('gender')
            fee['fee_location'] = fee.pop('location')
            fee['fee_by'] = fee.pop('app_source')
            fee['fee_followee_num'] = fee.pop('followee_num')
            fee['fee_follower_num'] = fee.pop('follower_num')
            fee['fee_weibo_num'] = fee.pop('weibo_num')
            fee['fee_verified_type'] = fee.pop('verified_type')
            fee['fee_is_vip'] = fee.pop('is_vip')
            fee['fee_vip_level'] = fee.pop('vip_level')
            fee['fee_is_daren'] = fee.pop('is_daren')
            fee['fee_is_taobao'] = fee.pop('is_taobao')
            fee['fee_is_suishoupai'] = fee.pop('is_suishoupai')
            fee['fee_is_vlady'] = fee.pop('is_vlady')
            fee['fee_timestamp'] = fee.pop('timestamp')

        for fer in self.follower_list:
            fer['uid'] = fer.pop('uid')
            fer['fer_uid'] = fer.pop('fer_uid')
            fer['fer_name'] = fer.pop('name')
            fer['fer_profile_img_url'] = fer.pop('profile_img')
            fer['fer_description'] = fer.pop('description')
            fer['fer_gender'] = fer.pop('gender')
            fer['fer_location'] = fer.pop('location')
            fer['fer_by'] = fer.pop('app_source')
            fer['fer_followee_num'] = fer.pop('followee_num')
            fer['fer_follower_num'] = fer.pop('follower_num')
            fer['fer_weibo_num'] = fer.pop('weibo_num')
            fer['fer_verified_type'] = fer.pop('verified_type')
            fer['fer_is_vip'] = fer.pop('is_vip')
            fer['fer_vip_level'] = fer.pop('vip_level')
            fer['fer_is_daren'] = fer.pop('is_daren')
            fer['fer_is_taobao'] = fer.pop('is_taobao')
            fer['fer_is_suishoupai'] = fer.pop('is_suishoupai')
            fer['fer_is_vlady'] = fer.pop('is_vlady')
            fer['fer_timestamp'] = fer.pop('timestamp')

        for tl in self.timeline_list:
            tl['mid'] = tl.pop('mid')
            tl['encrypt_mid'] = tl.pop('encrypted_mid')
            tl['uid'] = tl.pop('uid')
            tl['retweet_num'] = tl.pop('retweet')
            tl['comment_num'] = tl.pop('comment')
            tl['favourite_num'] = tl.pop('favourite')
            tl['created_at'] = tl.pop('created_at')
            tl['from'] = tl.pop('app_source')
            tl['text'] = tl.pop('text')
            tl['entity'] = tl.pop('entity')
            tl['source_mid'] = tl.pop('source_mid')
            tl['source_uid'] = tl.pop('source_uid')
            tl['mentions'] = tl.pop('mentions')
            tl['check_in'] = tl.pop('check_in')
            tl['check_in_url'] = tl.pop('check_in_url')
            tl['is_deleted'] = tl.pop('is_deleted')
            tl['timestamp'] = tl.pop('timestamp')

        for pf in self.profile_list:
            for jb in pf['Job']:
                jb['uid'] = pf['uid']
                jb['timestamp'] = pf['timestamp']

                jb['company'] = jb.pop('company')
                jb['location'] = jb.pop('location')
                jb['occupation'] = jb.pop('occupation')
                jb['time_period'] = jb.pop('period')

            for edu in pf['Education']:
                edu['uid'] = pf['uid']
                edu['timestamp'] = pf['timestamp']

                edu['school_name'] = edu.pop('university')
                edu['time_period'] = edu.pop('period')
                edu['department'] = edu.pop('department')
                edu['type'] = edu.pop('type')


            pf['uid'] = pf.pop('uid')
            pf['screen_name'] = pf.pop('nickname')
            pf['real_name'] = pf.pop('name')
            pf['location'] = pf.pop('location')
            pf['gender'] = pf.pop('gender')
            pf['sexual_orientation'] = pf.pop('sexual_orientation')
            pf['relationship_status'] = pf.pop('relationship_status')
            pf['birthday'] = pf.pop('birthday')
            pf['blood_type'] = pf.pop('blood_type')
            pf['blog'] = pf.pop('blog')
            pf['description'] = pf.pop('description')
            pf['email'] = pf.pop('email')
            pf['QQ'] = pf.pop('QQ')
            pf['MSN'] = pf.pop('MSN')
            pf['tag'] = pf.pop('tag')
            pf['followee_num'] = pf.pop('followee_num')
            pf['follower_num'] = pf.pop('follower_num')
            pf['weibo_num'] = pf.pop('weibo_num')
            pf['created_at'] = pf.pop('created_at')
            pf['profile_img_url'] = pf.pop('profile_img')
            pf['domain_id'] = pf.pop('domain_id')
            pf['domain_name'] = pf.pop('domain_name')
            pf['level'] = pf.pop('level')
            pf['experience'] = pf.pop('experience')
            pf['credit_level'] = pf.pop('credit_level')
            pf['credit_point'] = pf.pop('credit_point')
            pf['credit_history'] = pf.pop('credit_history')
            pf['is_vip'] = pf.pop('is_vip')
            pf['vip_level'] = pf.pop('vip_level')
            pf['is_yearly_pay'] = pf.pop('is_yearly_paid')
            pf['is_verified'] = pf.pop('is_verified')
            pf['verified_reason'] = pf.pop('verified_reason')
            pf['is_daren'] = pf.pop('is_daren')
            pf['daren_type'] = pf.pop('daren_type')
            pf['daren_point'] = pf.pop('daren_point')
            pf['daren_interest'] = pf.pop('daren_interest')
            pf['is_taobao'] = pf.pop('is_taobao')
            pf['not_exist'] = pf.pop('not_exist')
            pf['timestamp'] = pf.pop('timestamp')
    def clear_buffer(self):
        '''
        clear memory buffer after storing the information
        :return:
        '''

        self.followee_list = []
        self.follower_list = []
        self.timeline_list = []
        self.profile_list = []
    def clear_null_data(self):
        '''
        clear empty or None data for all information
        :return:
        '''
        followee_list = []
        follower_list = []
        timeline_list = []
        profile_list = []

        for fee in self.followee_list:
            dict = {}
            for key in fee:
                if fee[key] is None or fee[key] == '':
                    continue
                else:
                    dict[key] = fee[key]
            followee_list.append(dict)
        self.followee_list = followee_list

        for fer in self.follower_list:
            dict = {}
            for key in fer:
                if fer[key] is None or fer[key] == '':
                    continue
                else:
                    dict[key] = fer[key]
            follower_list.append(dict)
        self.follower_list = follower_list

        for tl in self.timeline_list:
            dict = {}
            for key in tl:
                if tl[key] is None or tl[key] == '':
                    continue
                else:
                    dict[key] = tl[key]
            timeline_list.append(dict)
        self.timeline_list = timeline_list


        for pf in self.profile_list:
            dict = {}
            for key in pf:
               if pf[key] is None or pf[key] == '':
                   continue
               else:
                   dict[key] = pf[key]
            profile_list.append(dict)
        self.profile_list = profile_list


        for pf in self.profile_list:
            job_list = []
            edu_list = []
            for job in pf['Job']:
                dict = {}
                for key in job:
                    if job[key] is None or job[key] == '':
                        continue
                    else:
                        dict[key] = job[key]
                job_list.append(dict)
            pf['Job'] = job_list

            for edu in pf['Education']:
                dict = {}
                for key in edu:
                    if edu[key] is None or edu[key] == '':
                        continue
                    else:
                        dict[key] = edu[key]
                edu_list.append(dict)
            pf['Education'] = edu_list



    def set_user_deleted_by_uid(self, uid):
        db = Database()
        db.connect()

        cursor = db.session.query(Dao.Task).filter(Dao.Task.uid == uid).one()
        cursor.is_deleted = '1'

        db.close()