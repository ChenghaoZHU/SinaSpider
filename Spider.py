__author__ = 'chzhu'


class Spider(object):

    def __init__(self, user_list):
        """
        constructed by users
        :param user_list: a list of users
        :return:
        """
        self.users = user_list

    def __init__(self, cookie_list):
        """
        constructed by cookies
        :param cookie_list: a list of cookies
        :return:
        """
        self.cookies = cookie_list