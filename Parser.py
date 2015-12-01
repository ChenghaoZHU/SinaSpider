#coding=utf-8
__author__ = 'chzhu'

from bs4 import BeautifulSoup
from Utility import strip_blanks, deparentheses
import json
import re

class HtmlParser(object):
    def parse_pid(self, html):
        """

        :param html:
        :return: pid if exception occurs return None
        """
        soup = BeautifulSoup(html)
        script = soup.find('script', text=re.compile("\$CONFIG\[\'page_id\'\]"))

        try:
            script = script.text
            attributes = script.split(';')
            pid = ''
            for attr in attributes:
                if 'page_id' in attr:
                    pid = attr.split('=')[1][1:-1]
                    pid = str(pid) # convert unicode to string
                    return pid
        except Exception as e:
            print e
            return None
    def covert_script_to_hmtl(self, script):
        """

        :param script: a bs4 tag object
        :return: html if failed return None
        """
        script = script.text
        try:
            jsn = script[8:-1]
            return json.loads(jsn)['html']
        except Exception as e:
            print e
            return None
    def get_max_page_num(self, links):
        '''

        :param links: a list of links, which contain page numbers
        :return: max page number
        '''

        max_pnum = 0

        for link in links:
            pnum = link.text
            if pnum.isdigit():
                pnum = int(pnum)
                if pnum > max_pnum:
                    max_pnum = pnum
            else:
                continue

        return max_pnum
    def parse_is_taobao(self, html):
        '''

        :param html:
        :return: '1' is taobao, '0' is not
        '''
        keyword = 'W_icon icon_taobao'
        soup = BeautifulSoup(html)
        scripts = soup.find_all('script')
        script = None
        for scr in scripts:
            if u'PCD_person_info' in scr.text:
                script = scr
                break
        if script is None:
            return None # dirty html

        html = self.covert_script_to_hmtl(script)
        soup = BeautifulSoup(html)
        person_info = soup.find('div', 'PCD_person_info')
        taobao = person_info.find('em', keyword)

        if taobao is not None:
            return '1'
        else:
            return '0'

    ######################################## follower parsing ###################################################
    def parse_followers(self, html, pid, timestamp):
        """

        :param html:
        :param pid:
        :param timestamp: crawled time
        :return: a list of followers
        """
        followers = []
        follower = {
            'uid':'',
            'fer_uid':'',
            'name':'',
            'profile_img':'',
            'description':'',
            'gender':'',
            'location':'',
            'app_source':'',
            'followee_num':'',
            'follower_num':'',
            'weibo_num':'',
            'is_vip':'0',
            'vip_level':'',
            'verified_type':'0',
            'is_daren':'0',
            'is_taobao':'0', # deprecated
            'is_suishoupai':'0', # deprecated
            'is_vlady':'0',
            'timestamp':''
        }

        soup = BeautifulSoup(html)
        scripts = soup.find_all('script')
        script = None
        for scr in scripts:
            if 'follow_item S_line2' in scr.text: # follow_item S_line2 denotes for one follower
                script = scr
                break
        if script is None:
            return [] # no followers to parse

        html = self.covert_script_to_hmtl(script)
        if html is None:
            return None # dirty html

        soup = BeautifulSoup(html)
        follower_list = soup.find('ul', 'follow_list')
        follower_list = follower_list.find_all('li', 'follow_item S_line2')
        for fer in follower_list: # start to parse...
            follower['uid'] = pid[6:]
            follower['fer_uid'] = self.parse_follower_uid(fer)
            follower['name'] = self.parse_follower_name(fer)
            follower['profile_img'] = self.parse_follower_profile_img(fer)
            follower['description'] = self.parse_follower_description(fer)
            follower['gender'] = self.parse_follower_gender(fer)
            follower['location'] = self.parse_follower_location(fer)
            follower['app_source'] = self.parse_follower_app_source(fer)
            follower['followee_num'] = self.parse_follower_followee_num(fer)
            follower['follower_num'] = self.parse_follower_follower_num(fer)
            follower['weibo_num'] = self.parse_follower_weibo_num(fer)
            follower['vip_level'] = self.parse_follower_vip_level(fer)
            follower['verified_type'] = self.parse_follower_verified_type(fer)
            follower['is_daren'] = self.parse_follower_daren(fer)
            follower['is_vlady'] = self.parse_follower_vlady(fer)
            if follower['vip_level'] is not None:
                follower['is_vip'] = '1'
            follower['timestamp'] = timestamp
            # end parsing
            followers.append(follower)
            follower = self.reset_follower(follower)

        return followers
    def parse_follower_page_num(self, html):
        """

        :param html:
        :return: follower page number if exception return None
        """
        soup = BeautifulSoup(html)

        scripts = soup.find_all('script')
        script = None
        for scr in scripts:
            if 'follow_item S_line2' in scr.text: # follow_item S_line2 denotes for one follower
                script = scr
                break

        if script is None:
            return 0
        else: # followers exist
           html = self.covert_script_to_hmtl(script)
           if html is not None:
               soup = BeautifulSoup(html)
               W_pages = soup.find('div', 'W_pages')
               if W_pages is not None:
                   page_links = W_pages.find_all('a', attrs={'bpfilter':'page'})
                   return self.get_max_page_num(page_links)
               else:
                   return 1
           else: # dirty html
               return None
    def reset_follower(self, follower):
        """

        :param follower: a dict standing for a follower
        :return:
        """
        follower = {
            'uid':'',
            'fer_uid':'',
            'name':'',
            'profile_img':'',
            'description':'',
            'gender':'',
            'location':'',
            'app_source':'',
            'followee_num':'',
            'follower_num':'',
            'weibo_num':'',
            'is_vip':'0',
            'vip_level':'',
            'verified_type':'0',
            'is_daren':'0',
            'is_taobao':'0',
            'is_suishoupai':'0',
            'is_vlady':'0',
            'timestamp':''
        }
        return follower
    def parse_follower_uid(self, follower):
        """

        :param follower: li tag containing follower information
        :return: uid of the follower
        """
        try:
            action_data = follower['action-data']
            datas = action_data.split('&')
            for dt in datas:
                if 'uid' in dt:
                    uid = dt
                    return uid.split('=')[-1]
            return None
        except Exception as e:
            print e
            return None
    def parse_follower_name(self, follower):
        """

        :param follower: li tag
        :return: name of the follower
        """
        try:
            action_data = follower['action-data']
            datas = action_data.split('&')
            for dt in datas:
                if 'fnick' in dt:
                    name = dt
                    return name.split('=')[-1]
            return None
        except Exception as e:
            print e
            return None
    def parse_follower_gender(self, follower):
        """

        :param follower: a li tag
        :return: gender of the follower
        """
        try:
            action_data = follower['action-data']
            datas = action_data.split('&')
            for dt in datas:
                if 'sex' in dt:
                    gender = dt.split('=')[-1]
                    return gender.upper()
            return None
        except Exception as e:
            print e
            return None
    def parse_follower_profile_img(self, follower):
        """

        :param follower: a li tag
        :return: profile img url of the follower
        """
        try:
            dt = follower.find('dt', 'mod_pic')
            img = dt.find('img')
            return img['src']
        except Exception as e:
            print e
            return None
    def parse_follower_description(self, follower):
        """

        :param follower: a lit tag
        :return: description of follower
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            intro = dd.find('div', 'info_intro')
            if intro is None:
                return None
            intro = intro.find('span').text
            return intro
        except Exception as e:
            print e
            return None
    def parse_follower_location(self, follower):
        """

        :param follower: li tag
        :return: location
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            addr = dd.find('div', 'info_add')
            return addr.find('span').text
        except Exception as e:
            print e
            return None
    def parse_follower_app_source(self, follower):
        """

        :param follower: li tag in html
        :return: app source by which two users are involved
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            app_src = dd.find('a', 'from')
            return app_src.text
        except Exception as e:
            print e
            return None
    def parse_follower_followee_num(self, follower):
        """

        :param follower:
        :return: number of followees
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_connect')
            info = info.find_all('span')
            for i in info:
                if u'关注' in i.text:
                    return i.find('a').text
            return None
        except Exception as e:
            print e
            return None
    def parse_follower_follower_num(self, follower):
        """

        :param follower:
        :return: number of followers
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_connect')
            info = info.find_all('span')
            for i in info:
                if u'粉丝' in i.text:
                    return i.find('a').text
            return None
        except Exception as e:
            print e
            return None
    def parse_follower_weibo_num(self, follower):
        """

        :param follower:
        :return: number of weibo
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_connect')
            info = info.find_all('span')
            for i in info:
                if u'微博' in i.text:
                    return i.find('a').text
            return None
        except Exception as e:
            print e
            return None
    def parse_follower_vip_level(self, follower):
        """

        :param follower: li tag
        :return: vip level
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_name W_fb W_f14')
            vip = info.find('a', attrs={'title':u'微博会员'})
            if vip is None:
                return None
            vip = vip.find('em')
            level = vip['class'][-1][-1]
            return level
        except Exception as e:
            print e
            return None
    def parse_follower_verified_type(self, follower):
        """

        :param follower: li tag
        :return: verified type 0 not verified 1 personal verified 2 organization verified
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_name W_fb W_f14')
            types = info.find_all('i')
            for type in types:
                try:
                    title = type['title']
                except KeyError:
                    continue
                if u'微博个人认证' in title:
                    return '1'
                elif u'微博机构认证' in title:
                    return '2'
            return '0'
        except Exception as e:
            print e
            return '0'
    def parse_follower_daren(self, follower):
        """

        :param follower: a li tag of html
        :return: boolean value 1 is daren 0 is not daren
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_name W_fb W_f14')
            daren = info.find('i', attrs={'node-type':'daren'})
            if daren is not None:
                return '1'
            else:
                return '0'
        except Exception as e:
            print e
            return '0'
    def parse_follower_vlady(self, follower):
        """

        :param follower: li tag
        :return: 1 is vlady 0 is not
        """
        try:
            dd = follower.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_name W_fb W_f14')
            vlady = info.find('i', 'W_icon icon_vlady')
            if vlady is not None:
                return '1'
            else:
                return '0'
        except Exception as e:
            print e
            return '0'
    #############################################################################################################

    ####################################### followee parsing ####################################################
    def parse_followee_page_num(self, html):
        """

        :param html:
        :return: followee page number, None if dirty html
        """
        soup = BeautifulSoup(html)

        scripts = soup.find_all('script')
        script = None
        for scr in scripts:
            if 'follow_item S_line2' in scr.text: # follow_item S_line2 denotes one followee
                script = scr
                break

        if script is None:
            return 0
        else: # user followed someones
            html = self.covert_script_to_hmtl(script)
            if html is not None:
                soup = BeautifulSoup(html)
                W_pages = soup.find('div', 'W_pages')
                if W_pages is not None:
                    page_links = W_pages.find_all('a', attrs={'bpfilter':'page'})
                    return self.get_max_page_num(page_links)
                else:
                    return 1
            else: # dirty html
                return None
    def parse_followees(self, html, pid, timestamp):
        """

        :param html:
        :param pid:
        :param timestamp: crawled time
        :return: a list of followees
        """
        followees = [] # to return
        followee = {
            'uid':'',
            'fee_uid':'',
            'name':'',
            'profile_img':'',
            'description':'',
            'gender':'',
            'location':'',
            'app_source':'',
            'followee_num':'',
            'follower_num':'',
            'weibo_num':'',
            'is_vip':'0',
            'vip_level':'',
            'verified_type':'0',
            'is_daren':'0',
            'is_taobao':'0', # deprecated
            'is_suishoupai':'0', # deprecated
            'is_vlady':'0',
            'timestamp':''
        }

        soup = BeautifulSoup(html)
        scripts = soup.find_all('script')
        script = None
        for scr in scripts:
            if 'follow_item S_line2' in scr.text: # follow_item S_line2 denotes for one follower
                script = scr
                break
        if script is None:
            return [] # no followees

        html = self.covert_script_to_hmtl(script)
        if html is None:
            return None # dirty html

        soup = BeautifulSoup(html)
        followee_list = []
        for flist in soup.find_all('ul', 'follow_list'): # maybe there are two follow list one is the common one, the other is the recommendation one
            followee_list.extend(flist.find_all('li', 'follow_item S_line2'))

        for fee in followee_list: # start to parse...
            followee['uid'] = pid[6:]
            followee['fee_uid'] = self.parse_followee_uid(fee)
            followee['name'] = self.parse_followee_name(fee)
            followee['profile_img'] = self.parse_followee_profile_img(fee)
            followee['description'] = self.parse_followee_description(fee)
            followee['gender'] = self.parse_followee_gender(fee)
            followee['location'] = self.parse_followee_location(fee)
            followee['app_source'] = self.parse_followee_app_source(fee)
            followee['followee_num'] = self.parse_followee_followee_num(fee)
            followee['follower_num'] = self.parse_followee_follower_num(fee)
            followee['weibo_num'] = self.parse_followee_weibo_num(fee)
            followee['vip_level'] = self.parse_followee_vip_level(fee)
            followee['verified_type'] = self.parse_followee_verified_type(fee)
            followee['is_daren'] = self.parse_followee_daren(fee)
            followee['is_vlady'] = self.parse_followee_vlady(fee)
            if followee['vip_level'] is not None:
                followee['is_vip'] = '1'
            followee['timestamp'] = timestamp
            # end parsing
            followees.append(followee)
            followee = self.reset_followee(followee)

        return followees
    def reset_followee(self, followee):
        """

        :param followee: a dict standing for a followee
        :return:
        """
        followee = {
            'uid':'',
            'fee_uid':'',
            'name':'',
            'profile_img':'',
            'description':'',
            'gender':'',
            'location':'',
            'app_source':'',
            'followee_num':'',
            'follower_num':'',
            'weibo_num':'',
            'is_vip':'0',
            'vip_level':'',
            'verified_type':'0',
            'is_daren':'0',
            'is_taobao':'0',
            'is_suishoupai':'0',
            'is_vlady':'0',
            'timestamp':''
        }
        return followee
    def parse_followee_uid(self, followee):
        """

        :param followee: a li tag
        :return:
        """
        try:
            data = followee['action-data']
            data = data.split('&')
            for dt in data:
                if u'uid' in dt:
                    return dt.split('=')[-1]
            return None
        except Exception as e:
            print e
            return None
    def parse_followee_name(self, followee):
        """

        :param followee: a li tag
        :return:
        """
        try:
            data = followee['action-data']
            data = data.split('&')
            for dt in data:
                if u'fnick' in dt:
                    return dt.split('=')[-1]
            return None
        except Exception as e:
            print e
            return None
    def parse_followee_profile_img(self, followee):
        """

        :param followee: li tag
        :return:
        """
        try:
            dt = followee.find('dt', 'mod_pic')
            img = dt.find('a').find('img')
            return img['src']
        except Exception as e:
            print e
            return None
    def parse_followee_description(self, followee):
        """

        :param followee: li tag
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            des = dd.find('div', 'info_intro')
            if des is None:
                return None
            return des.find('span').text
        except Exception as e:
            print e
            return None
    def parse_followee_gender(self, followee):
        """

        :param followee: a li tag of html
        :return:
        """
        try:
            data = followee['action-data']
            data = data.split('&')
            for dt in data:
                if u'sex' in dt:
                    return dt.split('=')[-1].upper()
            return None
        except Exception as e:
            print e
            return None
    def parse_followee_location(self, followee):
        """

        :param followee: li
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            loc = dd.find('div', 'info_add')
            return loc.find('span').text
        except Exception as e:
            print e
            return None
    def parse_followee_app_source(self, followee):
        """

        :param followee: a li
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            app = dd.find('div', 'info_from')
            return app.find('a', 'from').text
        except Exception as e:
            print e
            return None
    def parse_followee_followee_num(self, followee):
        """

        :param followee:  list item of unordered list
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_connect')
            if info is None:
                return None # recommended followees are without statistics information
            for i in info.find_all('span'):
                if u'关注' in i:
                    return i.find('a').text
            return None
        except Exception as e:
            print e
            return None
    def parse_followee_follower_num(self, followee):
        """

        :param followee: li tag
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_connect')
            if info is None:
                return None # recommended followees are without statistics information
            for i in info.find_all('span'):
                if u'粉丝' in i:
                    return i.find('a').text
            return None
        except Exception as e:
            print e
            return None
    def parse_followee_weibo_num(self, followee):
        """

        :param followee: li tag
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            info = dd.find('div', 'info_connect')
            if info is None:
                return None # recommended followees are without statistics information
            for i in info.find_all('span'):
                if u'微博' in i:
                    return i.find('a').text
            return None
        except Exception as e:
            print e
            return None
    def parse_followee_vip_level(self, followee):
        """

        :param followee: li tag of html
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            icons = dd.find('div', 'info_name W_fb W_f14')
            vip = icons.find('a', attrs={'title':u'微博会员'})
            if vip is None:
                return None
            level = vip.find('em')['class'][-1][-1]
            return level
        except Exception as e:
            print e
            return None
    def parse_followee_verified_type(self, followee):
        """

        :param followee: li tag
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            icons = dd.find('div', 'info_name W_fb W_f14')
            types = icons.find_all('i')
            for tp in types:
                try:
                    title = tp['title']
                except KeyError:
                    continue
                if u'微博个人认证' in title:
                    return '1'
                elif u'微博机构认证' in title:
                    return  '2'
            return '0'
        except Exception as e:
            print e
            return '0'
    def parse_followee_daren(self, followee):
        """

        :param followee: li tag
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            icons = dd.find('div', 'info_name W_fb W_f14')
            daren = icons.find('i', attrs={'node-type':'daren'})
            if daren is not None:
                return '1'
            else:
                return '0'
        except Exception as e:
            print e
            return '0'
    def parse_followee_vlady(self, followee):
        """

        :param followee: a li of ul
        :return:
        """
        try:
            dd = followee.find('dd', 'mod_info S_line1')
            icons = dd.find('div', 'info_name W_fb W_f14')
            vlady = icons.find('i', 'W_icon icon_vlady')
            if vlady is not None:
                return '1'
            return '0'
        except Exception as e:
            print e
            return '0'
    #############################################################################################################

    ######################################## timelines parsing ##################################################
    def parse_timeline_page_num(self, html):
        """

        :param html:
        :return: timeline page number or None if exception
        """
        soup = BeautifulSoup(html)
        more_pages = soup.find('div', attrs={'action-type':'feed_list_page_morelist'})
        if more_pages is None:
            return 1
        else:
            pages = more_pages.find_all('a', attrs={'action-type':'feed_list_page'})
            try:
                pnum = pages[0]['href'].strip(u'&pids=Pl_Content_HomeFeed').split('=')[1]
                return int(pnum)
            except Exception as e:
                print e
                return None
    def parse_timelines(self, html, uid, timestamp):
        """

        :param html:
        :param uid:
        :param timestamp:
        :return: a list of timelines
        """
        timeline_list = [] # result list

        soup = BeautifulSoup(html)
        timelines = soup.find_all('div', 'WB_feed_type SW_fun S_line2 ') # the empty space after WB_feed_type SW_fun S_line2 is a trick, maybe some problems would come up if Sina modify his strategy

        for tmln in timelines:
            tmln_type = len(tmln.find_all('div', 'WB_text'))
            if tmln_type == 1:
                timeline = self.parse_timeline_original(tmln, uid, timestamp)
                timeline_list.append(timeline)
            else: # this timeline contains retweeted contents
                timeline = self.parse_timeline_retweeted(tmln, uid, timestamp)
                timeline_list.extend(timeline)


        return timeline_list

    def parse_timeline_original(self, tmln, uid, timestamp):
        """
        parse original part of timeline
        :param tmln: timeline
        :param uid:
        :param timestamp:
        :return: a timeline dict
        """
        timeline = {
            'mid':'',
            'encrypted_mid':'',
            'uid':'',
            'retweet':'',
            'comment':'',
            'favourite':'',
            'created_at':'',
            'app_source':'',
            'text':'',
            'entity':'',
            'source_mid':'',
            'source_uid':'',
            'mentions':'',
            'check_in':'',
            'check_in_url':'',
            'is_deleted':'0',
            'timestamp':timestamp
        }

        timeline['mid'] = self.parse_timeline_original_mid(tmln)
        timeline['encrypted_mid'] = self.parse_timeline_original_encrypted_mid(tmln) # www.weibo.com/uid/encrypted_mid is the page of timeline
        timeline['uid'] = uid
        timeline['retweet'] = self.parse_timeline_original_retweet(tmln)
        timeline['comment'] = self.parse_timeline_original_comment(tmln)
        timeline['favourite'] = self.parse_timeline_original_favourite(tmln)
        timeline['created_at'] = self.parse_timeline_original_created_at(tmln)
        timeline['app_source'] = self.parse_timeline_original_app_source(tmln)
        timeline['text'] = self.parse_timeline_original_text(tmln)
        timeline['entity'] = self.parse_timeline_original_entities(tmln)
        timeline['mentions'] = self.parse_timeline_original_mentions(tmln)
        timeline['check_in'] = self.parse_timeline_original_check_in(tmln)
        timeline['check_in_url'] = self.parse_timeline_original_check_in_url(tmln)

        return timeline
    def parse_timeline_original_mid(self, timeline):
        """

        :param timeline:
        :return: mid
        """
        try:
            mid = timeline['mid']
            return mid
        except Exception as e:
            print e
            return None
    def parse_timeline_original_encrypted_mid(self, timeline):
        """

        :param timeline:
        :return: encrypted mid
        """
        try:
            created_time = timeline.find('a', 'S_link2 WB_time')
            encrypted_mid = created_time['href'].split('/')[-1]
            return encrypted_mid
        except Exception as e:
            print e
            return None
    def parse_timeline_original_retweet(self, timeline):
        """

        :param timeline:
        :return: retweet number
        """
        try:
            handle = timeline.find('div', 'WB_handle')
            statuses = handle.find_all('a')
            for stat in statuses:
                if u'feed_list_forward' in stat['action-type']:
                    retweet = stat.text.strip(u'转发 ')
                    retweet = deparentheses(retweet)
                    if retweet.isdigit():
                        return retweet
                    else:
                        return '0'
        except Exception as e:
            print e
            return None
    def parse_timeline_original_comment(self, timeline):
        """

        :param timeline:
        :return: comment num
        """
        try:
            handle = timeline.find('div', 'WB_handle')
            statuses = handle.find_all('a')
            for stat in statuses:
                if u'feed_list_comment' in stat['action-type']:
                    comment = stat.text.strip(u'评论 ')
                    comment = deparentheses(comment)
                    if comment.isdigit():
                        return comment
                    else:
                        return '0'
        except Exception as e:
            print e
            return None
    def parse_timeline_original_favourite(self, timeline):
        """

        :param timeline:
        :return: favourite number
        """
        try:
            handle = timeline.find('div', 'WB_handle')
            statuses = handle.find_all('a')
            for stat in statuses:
                if u'feed_list_like' in stat['action-type']:
                    favor = stat.text
                    favor = deparentheses(favor)
                    if favor.isdigit():
                        return favor
                    else:
                        return '0'
        except Exception as e:
            print e
            return None
    def parse_timeline_original_created_at(self, timeline):
        """

        :param timeline:
        :return: timeline created time
        """
        created_time = timeline.find('a', 'S_link2 WB_time')
        try:
            return created_time['title']
        except Exception as e:
            print e
            return None
    def parse_timeline_original_app_source(self, timeline):
        """

        :param timeline:
        :return: created app source
        """
        app_source = timeline.find('a', attrs={'action-type':'app_source', 'class':'S_link2'})
        if app_source is not None:
            return app_source.text
        else:
            return None
    def parse_timeline_original_text(self, timeline):
        """

        :param timeline:
        :return: weibo text
        """
        try:
            text = timeline.find('div', 'WB_text').text
            # text = strip_blanks(text)
            return text
        except Exception as e:
            print e
            return None
    def parse_timeline_original_entities(self, timeline):
        """

        :param timeline:
        :return: entities such as links, videos, audios and so on
        """
        entities = {
            'img':'',
            'link':'',
            'audio':'',
            'video':'',
            'event':'',
            'product':'',
            'others':''
        }

        entities['img'] = self.parse_timeline_original_img(timeline)

        try:
            text = timeline.find('div', 'WB_text')
            media_box = text.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')
            for media in media_box:
                if media.find('i', 'W_ficon ficon_cd_link S_ficon') is not None:
                    entities['link'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_music S_ficon') is not None:
                    entities['audio'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_video S_ficon') is not None:
                    entities['video'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_event S_ficon') is not None:
                    entities['event'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_product S_ficon') is not None:
                    entities['product'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    continue # exclude check in
                else: # for unknown situations
                    entities['others'] += media['title'] + ', ' + media['href'] + '; '

            entity_str = ''
            for key in entities:
                if entities[key] == '':
                    continue
                entities[key] = entities[key].strip('; ')
                entity_str += key + ':' + entities[key].strip('; ') + ' & '
            return entity_str.strip(' & ')
        except Exception as e:
            print e
            return ''
    def parse_timeline_original_mentions(self, timeline):
        """

        :param timeline:
        :return: people be mentioned by the user
        """
        try:
            text = timeline.find('div', 'WB_text')
            mention_list = text.find_all('a', {'extra-data':'type=atname'})
            mentions = ''
            for mention in mention_list:
                mentions += mention.text + ', '
            return mentions.strip(', ')
        except Exception as e:
            print e
            return None
    def parse_timeline_original_check_in(self, timeline):
        """

        :param timeline:
        :return: check in location
        """
        try:
            text = timeline.find('div', 'WB_text')
            media_box = text.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')
            for media in media_box:
                if media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    check_in = media['title']
                    return check_in
            return None
        except Exception as e:
            print e
            return None
    def parse_timeline_original_check_in_url(self, timeline):
        """

        :param timeline:
        :return: check in location url
        """
        try:
            text = timeline.find('div', 'WB_text')
            media_box = text.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')
            for media in media_box:
                if media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    check_in_url = media['href']
                    return check_in_url
            return None
        except Exception as e:
            print e
            return None
    def parse_timeline_original_img(self, timeline):
        """

        :param timeline:
        :return: img urls
        """
        imgs = timeline.find('ul', 'WB_media_list clearfix')
        if imgs is None:
            return ''
        img_urls = ''
        for i in imgs.find_all('img', 'bigcursor'):
            img_urls += i['src'] + ', '
        return img_urls.strip(', ')

    def parse_timeline_retweeted(self, timeline, uid, timestamp):
        """

        :param timeline:
        :param uid:
        :param timestamp:
        :return: timeline and source timeline
        """
        rtmln = { # retweet timeline
            'mid':'',
            'encrypted_mid':'',
            'uid':uid,
            'retweet':'',
            'comment':'',
            'favourite':'',
            'created_at':'',
            'app_source':'',
            'text':'',
            'entity':'',
            'source_mid':'',
            'source_uid':'',
            'mentions':'',
            'check_in':'',
            'check_in_url':'',
            'is_deleted':'0',
            'timestamp':timestamp
        }
        stmln = { # source timeline
            'mid':'',
            'encrypted_mid':'',
            'uid':'',
            'retweet':'',
            'comment':'',
            'favourite':'',
            'created_at':'',
            'app_source':'',
            'text':'',
            'entity':'',
            'source_mid':'',
            'source_uid':'',
            'mentions':'',
            'check_in':'',
            'check_in_url':'',
            'is_deleted':'0',
            'timestamp':timestamp
        }
        rtmln['mid'], stmln['mid'] = self.parse_timeline_retweeted_mid(timeline)
        rtmln['encrypted_mid'], stmln['encrypted_mid'] = self.parse_timeline_retweeted_encrypted_mid(timeline)
        stmln['uid'] = self.parse_timeline_retweeted_uid(timeline)
        rtmln['retweet'], stmln['retweet'] = self.parse_timeline_retweeted_retweet(timeline)
        rtmln['comment'], stmln['comment'] = self.parse_timeline_retweeted_comment(timeline)
        rtmln['favourite'], stmln['favourite'] = self.parse_timeline_retweeted_favourite(timeline)
        rtmln['created_at'], stmln['created_at'] = self.parse_timeline_retweeted_created_time(timeline)
        rtmln['app_source'], stmln['app_source'] = self.parse_timeline_retweeted_app_source(timeline)
        rtmln['text'], stmln['text'] = self.parse_timeline_retweeted_text(timeline)
        rtmln['entity'], stmln['entity'] = self.parse_timeline_retweeted_entities(timeline)
        rtmln['source_mid'] = stmln['mid']
        rtmln['source_uid'] = stmln['uid']
        rtmln['mentions'], stmln['mentions'] = self.parse_timeline_retweeted_mentions(timeline)
        rtmln['check_in'], rtmln['check_in_url'], stmln['check_in'], stmln['check_in_url'] = self.parse_timeline_retweeted_check_in(timeline)


        return rtmln, stmln
    def parse_timeline_retweeted_mid(self, timeline):
        """

        :param timeline:
        :return: mid rmid and source mid smid
        """
        try:
            rmid = timeline['mid']
            smid = timeline['omid']
            return rmid, smid
        except KeyError as ke:
            print ke
            return None, None
    def parse_timeline_retweeted_encrypted_mid(self, timeline):
        """

        :param timeline:
        :return: encrypted mid ret_encrypted_mid and source encrypted mid src_encrypted_mid
        """
        ret_created_time = timeline.find('a', 'S_link2 WB_time')
        src_created_time = timeline.find('a', 'S_func2 WB_time')
        try:
            ret_encrypted_mid = ret_created_time['href'].split('/')[-1]
            src_encrypted_mid = src_created_time['href'].split('/')[-1]
            return  ret_encrypted_mid, src_encrypted_mid
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_uid(self, timeline):
        """

        :param timeline:
        :return: source uid
        """
        try:
            uids = timeline['tbinfo'].split(u'&')
            suid = uids[1].split('=')[1]
            return suid
        except Exception as e:
            print e
            return None
    def parse_timeline_retweeted_retweet(self, timeline):
        '''

        :param timeline:
        :return: retweet number rretweet and source weibo retweet number ssretweet
        '''

        try:
            handles = timeline.find_all('div', 'WB_handle')

            rstatuses = handles[1].find_all('a')
            sstatuses = handles[0].find_all('a')

            for stat in rstatuses:
                if u'feed_list_forward' in stat['action-type']:
                    rretweet = stat.text.strip(u'转发')
                    rretweet = deparentheses(rretweet)
                    if rretweet.isdigit():
                        break
                    else:
                        rretweet = '0'
                        break

            for stat in sstatuses:
                if u'转发' in stat.text:
                    ssretweet = stat.text.strip(u'转发')
                    ssretweet = deparentheses(ssretweet)
                    if ssretweet.isdigit():
                        return rretweet, ssretweet
                    else:
                        return rretweet, '0'
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_comment(self, timeline):
        '''

        :param timeline:
        :return: comment number rcomment and source weibo comment number scomment
        '''
        try:
            handles = timeline.find_all('div', 'WB_handle')

            rstatuses = handles[1].find_all('a')
            sstatuses = handles[0].find_all('a')

            for stat in rstatuses:
                if u'feed_list_comment' in stat['action-type']:
                    rcomment = stat.text.strip(u'评论')
                    rcomment = deparentheses(rcomment)
                    if rcomment.isdigit():
                        break
                    else:
                        rcomment = '0'
                        break

            for stat in sstatuses:
                if u'评论' in stat.text:
                    scomment = stat.text.strip(u'评论')
                    scomment = deparentheses(scomment)
                    if scomment.isdigit():
                        return rcomment, scomment
                    else:
                        return rcomment, '0'
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_favourite(self, timeline):
        '''

        :param timeline:
        :return: favourite number fvrt1 and source weibo favourite number fvrt2
        '''
        try:
            handles = timeline.find_all('div', 'WB_handle')

            rstatuses = handles[1].find_all('a')
            sstatuses = handles[0].find_all('a')

            for stat in rstatuses:
                if u'feed_list_like' in stat['action-type']:
                    fvrt1 = stat.text
                    fvrt1 = deparentheses(fvrt1)
                    if fvrt1.isdigit():
                        break
                    else:
                        fvrt1 = '0'
                        break

            for stat in sstatuses:
                if u'评论' in stat.text:
                    continue
                elif u'转发' in stat.text:
                    continue
                else:
                    fvrt2 = stat.text
                    fvrt2 = deparentheses(fvrt2)
                    if fvrt2.isdigit():
                        return fvrt1, fvrt2
                    else:
                        return fvrt1, '0'
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_created_time(self, timeline):
        '''

        :param timeline:
        :return: created time ct1 and source weibo created time ct2
        '''

        ct1 = timeline.find('a', 'S_link2 WB_time')
        ct2 = timeline.find('a', 'S_func2 WB_time')
        try:
            ct1 = ct1['title']
            ct2 = ct2['title']
            return ct1, ct2
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_app_source(self, timeline):
        '''

        :param timeline:
        :return: weibo app source app1 and source weibo app source app2
        '''
        app1 = timeline.find('a', attrs={'action-type':'app_source', 'class':'S_link2'})
        app2 = timeline.find('a', attrs={'action-type':'app_source', 'class':'S_func2'})

        try:
            app1 = app1.text
            app2 = app2.text
            return app1, app2
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_text(self, timeline):
        '''

        :param timeline:
        :return: weibo text txt1 and source weibo text txt2
        '''
        texts = timeline.find_all('div', 'WB_text')
        mention = timeline.find('a', 'WB_name S_func3').text

        try:
            txt1 = texts[0].text
            txt2 = texts[1].text
            txt1 += '//' + mention + ' ' + txt2
        except Exception as e:
            print e
            return None, None

        return txt1, txt2
    def parse_timeline_retweeted_entities(self, timeline):
        '''

        :param timeline:
        :return: entities ent1 and source weibo entities ent2 such as links, audio, video and so on
        '''
        ents1 = {
            'img':'',
            'link':'',
            'audio':'',
            'video':'',
            'event':'',
            'product':'',
            'others':''
        }
        ents2 = {
            'img':'',
            'link':'',
            'audio':'',
            'video':'',
            'event':'',
            'product':'',
            'others':''
        }

        ents1['img'], ents2['img'] = self.parse_timeline_retweeted_img(timeline)

        txts = timeline.find_all('div', 'WB_text')
        try:
            txt1 = txts[0]
            txt2 = txts[1]

            media_box1 = txt1.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')
            media_box2 = txt2.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')

            for media in media_box1: # parse entities
                if media.find('i', 'W_ficon ficon_cd_link S_ficon') is not None:
                    ents1['link'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_music S_ficon') is not None:
                    ents1['audio'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_video S_ficon') is not None:
                    ents1['video'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_event S_ficon') is not None:
                    ents1['event'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_product S_ficon') is not None:
                    ents1['product'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    continue # exclude check in
                else: # for unknown situations
                    ents1['others'] += media['title'] + ', ' + media['href'] + '; '

            for media in media_box2: # parse source weibo entities
                if media.find('i', 'W_ficon ficon_cd_link S_ficon') is not None:
                    ents2['link'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_music S_ficon') is not None:
                    ents2['audio'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_video S_ficon') is not None:
                    ents2['video'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_event S_ficon') is not None:
                    ents2['event'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_product S_ficon') is not None:
                    ents2['product'] += media['title'] + ', ' + media['href'] + '; '
                elif media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    continue # exclude check in
                else: # for unknown situations
                    ents2['others'] += media['title'] + ', ' + media['href'] + '; '
        except Exception as e:
            print e
            return None, None

        # glue to strings
        ent1 = ''
        for key in ents1:
            if ents1[key] is None or ents1[key] == '':
                continue
            ents1[key] = ents1[key].strip('; ')
            ent1 += key + ':' + ents1[key] + ' & '
        ent1 = ent1.strip(' & ')

        ent2 = ''
        for key in ents2:
            if ents2[key] is None or ents2[key] == '':
                continue
            ents2[key] = ents2[key].strip('; ')
            ent2 += key + ':' + ents2[key] + ' & '
        ent2 = ent2.strip(' & ')

        return ent1, ent2
    def parse_timeline_retweeted_img(self, timeline):
        '''

        :param timeline:
        :return: pics and source weibo pics in the form of url string, i.e., img1 and img2
        '''
        img1 = ''
        img2 = ''

        img1_elements = timeline.find('div', 'WB_arrow')
        # img1_elements = img1_elements.find_all('img', attrs={'class':'bigcursor', 'action-type':'fl_pics'})
        if img1_elements is not None:
            img1_elements = img1_elements.find_all('img', 'bigcursor')
        else:
            img1_elements = []

        img2_elements = timeline.find('div', attrs={'node-type':'feed_list_media_prev'})
        # img2_elements = img2_elements.find_all('img', attrs={'class':'bigcursor', 'action-type':'fl_pics'})
        if img2_elements is not None:
            img2_elements = img2_elements.find_all('img', 'bigcursor')
        else:
            img2_elements = []

        try:
            for ie in img1_elements:
                img1 += ie['src'] + ', '
            img1 = img1.strip(', ')

            for ie in img2_elements:
                img2 += ie['src'] + ', '
            img2 = img2.strip(', ')
        except Exception as e:
            print e
            return None, None

        return img1, img2
    def parse_timeline_retweeted_mentions(self, timeline):
        '''

        :param timeline:
        :return: mentions string and source weibo mentions string, mnt1 and mnt2
        '''
        mnt1 = ''
        mnt2 = ''

        txts = timeline.find_all('div', 'WB_text')
        mention = timeline.find('a', 'WB_name S_func3').text

        try:
            txt1 = txts[0].text
            txt2 = txts[1].text

            mentions1 = txts[0].find_all('a', attrs={'extra-data':'type=atname'})
            mentions2 = txts[1].find_all('a', attrs={'extra-data':'type=atname'})

            for m in mentions1:
                mnt1 += m.text + ', '

            for m in mentions2:
                mnt2 += m.text + ', '
            mnt2 = mnt2.strip(', ')

            mnt1 += mention + ', ' +mnt2
            mnt1 = mnt1.strip(', ')

            return mnt1, mnt2
        except Exception as e:
            print e
            return None, None
    def parse_timeline_retweeted_check_in(self, timeline):
        '''

        :param timeline:
        :return: check_in1:check in location, url1:check in url, check_in2:source weibo check in location, url2:source weibo check in url
        '''
        txts = timeline.find_all('div', 'WB_text')

        check_in1 = url1 = check_in2 = url2 = ''

        try:
            txt1 = txts[0]
            txt2 = txts[1]

            media_box1 = txt1.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')
            media_box2 = txt2.find_all('a', 'W_btn_b btn_22px W_btn_cardlink')

            for media in media_box1:
                if media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    check_in1 = media['title']
                    url1 = media['href']
                    break

            for media in media_box2:
                if media.find('i', 'W_ficon ficon_cd_place S_ficon') is not None:
                    check_in2 = media['title']
                    url2 = media['href']
                    break

            return check_in1, url1, check_in2, url2

        except Exception as e:
            print e
            return None, None, None, None

    def parse_profile(self, html, pid, is_taobao, timestamp):
        '''
        parse profile information
        :param html:
        :param pid:
        :param is_taobao:
        :param timestamp:
        :return: a dict displaying profile
        '''
        soup = BeautifulSoup(html)
        scripts = soup.find_all('script')
        frame_a = None # frame that contains avatar, background ...
        frame_b = None # frame that contains daren and credit information
        frame_c = None # frame that contains basic information
        counter = None # counter statistic for the followee number, follower number and weibo number

        for scr in scripts:
            if ur'<h2 class=\"main_title W_fb W_f14\">基本信息' in scr.text:
                frame_c = scr
            elif ur'<a class=\"S_txt1\" href=\"javascript:void(0);\">等级信息' in scr.text:
                frame_b = scr
            elif ur'class=\"photo\"' in scr.text:
                frame_a = scr
            elif ur'<table class=\"tb_counter\"' in scr.text:
                counter = scr

        if frame_a is None or frame_b is None or frame_c is None or counter is None:
            return None # dirty html

        html = self.covert_script_to_hmtl(frame_a)
        frame_a = BeautifulSoup(html)

        html = self.covert_script_to_hmtl(frame_b)
        frame_b = BeautifulSoup(html)

        html = self.covert_script_to_hmtl(frame_c)
        frame_c = BeautifulSoup(html)

        html = self.covert_script_to_hmtl(counter)
        counter = BeautifulSoup(html)

        profile = self.init_profile({})
        profile['uid'] = pid[6:]
        profile['nickname'] = self.parse_profile_nick(frame_a)
        profile['name'] = self.parse_profile_name(frame_c)
        profile['location'] = self.parse_profile_location(frame_c)
        profile['gender'] = self.parse_profile_gender(frame_a)
        profile['sexual_orientation'] = self.parse_profile_sexual_orientation(frame_c)
        profile['relationship_status'] = self.parse_profile_relationship_status(frame_c)
        profile['birthday'] = self.parse_profile_birthday(frame_c)
        profile['blood_type'] = self.parse_profile_blood_type(frame_c)
        profile['blog'] = self.parse_profile_blog(frame_c)
        profile['description'] = self.parse_profile_description(frame_c)
        profile['email'] = self.parse_profile_email(frame_c)
        profile['QQ'] = self.parse_profile_QQ(frame_c)
        profile['MSN'] = self.parse_profile_MSN(frame_c)
        profile['tag'] = self.parse_profile_tag(frame_c)

        profile['followee_num'] = self.parse_profile_followee_num(counter)
        profile['follower_num'] = self.parse_profile_follower_num(counter)
        profile['weibo_num'] = self.parse_profile_weibo_num(counter)
        profile['created_at'] = self.parse_profile_created_time(frame_c)
        profile['profile_img'] = self.parse_profile_img(frame_a)
        profile['domain_id'] = pid
        profile['domain_name'] = self.parse_profile_domain(frame_c)

        return profile

    def parse_profile_nick(self, frame):
        '''

        :param frame: bs object
        :return: nick name
        '''
        nick = frame.find('h1', 'username')
        try:
            nick = nick.text
            return nick
        except Exception as e:
            print e
            return None
    def parse_profile_name(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'真实姓名：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no real name found
    def parse_profile_location(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'所在地：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no location found
    def parse_profile_gender(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        if frame.find('i', 'W_icon icon_pf_male') is not None:
            return 'M'
        elif frame.find('i', 'W_icon icon_pf_female') is not None:
            return 'F'
        else:
            return None # 双兔傍地走，安能辨我是雄雌？
    def parse_profile_sexual_orientation(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'性取向：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return strip_blanks(value.text) # original text contains lots of \t, it's waste of space
            except Exception as e:
                print e
                return None

        return '' # no sexual orientation
    def parse_profile_relationship_status(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'感情状况：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return strip_blanks(value.text) # original text contains lots of \t, it's waste of space
            except Exception as e:
                print e
                return None

        return '' # no relationship status
    def parse_profile_birthday(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'生日：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no birthday
    def parse_profile_blood_type(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'血型：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no blood type
    def parse_profile_blog(self, frame):
        '''

        :param frame:bs object
        :return: blog url
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'博客：' in key.text:
                    value = it.find('a')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no blog
    def parse_profile_description(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'简介：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no description
    def parse_profile_email(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        contact_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'联系信息' in title.text:
                contact_information = cd

        if contact_information is None:
            return '' # no contact information

        items = contact_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'邮箱：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no email address
    def parse_profile_QQ(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        contact_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'联系信息' in title.text:
                contact_information = cd

        if contact_information is None:
            return '' # no contact information

        items = contact_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'QQ：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no QQ
    def parse_profile_MSN(self, frame):
        '''

        :param frame:
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        contact_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'联系信息' in title.text:
                contact_information = cd

        if contact_information is None:
            return '' # no contact information

        items = contact_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'MSN：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return value.text
            except Exception as e:
                print e
                return None

        return '' # no MSN
    def parse_profile_tag(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        tag_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'标签信息' in title.text:
                tag_information = cd

        if tag_information is None:
            return '' # no tag information

        tags = tag_information.find_all('a', 'W_btn_b W_btn_tag')
        tag = ''
        for t in tags:
            try:
                item = t.text
                item = strip_blanks(item) # save space
            except Exception as e:
                print e
                continue
            tag += item + ', '
        tag = tag.strip(', ')
        return tag
    def parse_profile_followee_num(self, counter):
        '''

        :param counter: bs object
        :return:
        '''
        table = counter.find('table', 'tb_counter') # can not be None, since be checked in counter
        data = table.find_all('td', 'S_line1')

        for d in data:
            try:
                if u'关注' in d.text:
                    num = d.find('strong', 'W_f18').text
                    return num
            except Exception as e:
                print e
                return None
        return None # problem
    def parse_profile_follower_num(self, counter):
        '''

        :param counter: bs object
        :return:
        '''
        table = counter.find('table', 'tb_counter') # can not be None, since be checked in counter
        data = table.find_all('td', 'S_line1')

        for d in data:
            try:
                if u'粉丝' in d.text:
                    num = d.find('strong', 'W_f18').text
                    return num
            except Exception as e:
                print e
                return None
        return None # problem
    def parse_profile_weibo_num(self, counter):
        '''

        :param counter: bs object
        :return:
        '''
        table = counter.find('table', 'tb_counter') # can not be None, since be checked in counter
        data = table.find_all('td', 'S_line1')

        for d in data:
            try:
                if u'微博' in d.text:
                    num = d.find('strong', 'W_f18').text
                    return num
            except Exception as e:
                print e
                return None
        return None # problem
    def parse_profile_created_time(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'注册时间：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return strip_blanks(value.text) # save storage
            except Exception as e:
                print e
                return None

        return '' # created time missing
    def parse_profile_img(self, frame):
        '''

        :param frame: bs object
        :return: avatar url
        '''
        photo = frame.find('img', 'photo')
        try:
            return photo['src']
        except Exception as e:
            print e
            return None
    def parse_profile_domain(self, frame):
        '''

        :param frame: bs object
        :return:
        '''
        cards = frame.find_all('div', 'WB_cardwrap S_bg2')
        basic_information = None
        for cd in cards:
            title = cd.find('h2', 'main_title W_fb W_f14')
            if title is None:
                continue
            if u'基本信息' in title.text:
                basic_information = cd

        if basic_information is None:
            return None # dirty page, may not happen

        items = basic_information.find_all('li', 'li_1 clearfix')
        for it in items:
            key = it.find('span', 'pt_title S_txt2')
            try:
                if u'个性域名：' in key.text:
                    value = it.find('span', 'pt_detail')
                    return strip_blanks(value.text) # save room
            except Exception as e:
                print e
                return None

        return '' # domain not defined

    def init_profile(self, dict):
        '''

        :param dict: a dict reference
        :return: a dict defines a profile
        '''
        dict = {
            'uid':'',
            'nickname':'',
            'name':'',
            'location':'',
            'gender':'',
            'sexual_orientation':'',
            'relationship_status':'',
            'birthday':'',
            'blood_type':'',
            'blog':'',
            'description':'',
            'email':'',
            'QQ':'',
            'MSN':'',
            'tag':'',
            'followee_num':'',
            'follower_num':'',
            'weibo_num':'',
            'created_at':'',
            'profile_img':'',
            'domain_id':'',
            'domain_name':'',
            'level':'',
            'experience':'',
            'credit_level':'',
            'credit_point':'',
            'credit_history':'',
            'is_vip':'',
            'vip_level':'',
            'is_yearly_paid':'',
            'is_verified':'',
            'verified_reason':'',
            'is_daren':'',
            'daren_type':'',
            'daren_point':'',
            'daren_interest':'',
            'is_taobao':'',
            'not_exist':'0',
            'timestamp':'',
            'Education':[],
            'Job':[]
        }

        return dict