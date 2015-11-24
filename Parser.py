#coding=utf-8
__author__ = 'chzhu'

from bs4 import BeautifulSoup
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
            followee_list.extend(flist)
        followee_list = followee_list.find_all('li', 'follow_item S_line2')
        for fee in followee_list: # start to parse...
            followee['uid'] = pid[6:]
            followee['fer_uid'] = self.parse_followee_uid(fee)
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


















