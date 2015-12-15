__author__ = 'chzhu'

from Dao import Parameter
from Log import logger as log
import json, urllib2



class Spider(object):
    def __init__(self):

        # there are six parameters to fill up: fid, i, s, gsid, page and containerid (Ordered here)
        # i, s, gsid are decided by different accounts, and they can be obtained by intercepting web packages

        self.public_timeline_API = 'http://api.weibo.cn/2/cardlist' \
               '?fid=107603%s' \
               '&uid=5794206490' \
               '&afr=ad' \
               '&count=20' \
               '&c=android' \
               '&wm=5091_0008' \
               '&mark=1_1_40C3B7F67BDAF7CAE2E2BA31B7C40E9F876A9665E15639F0A9ABB393BEE972AB1BB3079B81576BF3F92C7DC263D644B7C12C4283157E8E65022C9A1E3EF44775DA506CD64004A8DDFDAEF980DF395ABE03ECE756A17ABE4A6ECA093F9E2D33FEBCD2DD1998BD978CDDED207D7D51E1A4' \
               '&luicode=10000001' \
               '&from=1043595010' \
               '&skin=default' \
               '&i=%s' \
               '&s=%s' \
               '&gsid=%s' \
               '&page=%s' \
               '&containerid=107603%s' \
               '&ua=TiantianVM-TianTian__weibo__4.3.5__android__android4.3' \
               '&oldwm=5091_0008' \
               '&v_p=10' \
               '&uicode=10000198' \
               '&featurecode=10000088' \
               '&lang=zh_CN'
        self.user_paras_list = Parameter.get_all()
        self.user_API_list = self.generate_timeline_APIs()


    def generate_timeline_APIs(self):

        APIs = []

        for user_paras in self.user_paras_list:
            paras = {
                'fid':'', # target user id
                'i':'',
                's':'',
                'gsid':'',
                'page':'',
                'containerid':'', # target user id
            }
            paras['i'] = user_paras.i
            paras['s'] = user_paras.s
            paras['gsid'] = user_paras.gsid
            APIs.append(paras)

        return APIs


    def get_timelines(self, uid, page_num):
        paras = self.user_API_list[0] # get a user paras
        paras['fid'] = uid
        paras['containerid'] = uid
        paras['page'] = page_num
        API_params = (paras['fid'], paras['i'], paras['s'], paras['gsid'], paras['page'], paras['containerid'])
        API = self.public_timeline_API % API_params
        message, body = self.post_request(API)
        return body



    def post_request(self, API):
        try:
            response = urllib2.urlopen(API, timeout=30)
        except Exception as e:
            log.warning(e)
            return None, None
        return response.info(), json.loads(response.read())



