__author__ = 'chzhu'

class Spider():
    def __init__(self, access_token):
        self.ACCESS_TOKEN = access_token
        self.APIs = {
            'user_timeline_batch': 'https://c.api.weibo.com/2/statuses/user_timeline_batch.json',
        }


    