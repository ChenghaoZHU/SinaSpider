__author__ = 'chzhu'


class User(object):
    def __init__(self, account, password):
        self.acct = account
        self.pswd = password



class Spider(object):
    def __init__(self, user_list=None, cookie_list=None):
        """

        :param user_list: a list of users
        :param cookie_list: a list of cookies
        :return:
        """
        if user_list is not None:
            self.users = user_list
            self.fetchers = self.get_fetchers_by_users()

    def get_fetchers_by_users(self):
        """
        generate fetchers by users
        :return:
        """
