__author__ = 'chzhu'

import os.path
from Dao import Account
from Dao import Database

if __name__ == '__main__':

    file_name = 'weibo_accounts.txt'
    if not os.path.isfile(file_name):
        print 'The file containing accounts must be named as "%s" !' % (file_name, )
        exit(-1)

    account_list = []

    with open(file_name, 'r') as reader:
        for line in reader:
            if line.strip('\r\n\t') == '':
                continue
            act = line.split('----')[0]
            pwd = line.split('----')[1].strip('\n')
            account = Account({'account':act, 'passwd':pwd})
            account_list.append(account)

    db = Database()
    db.connect()
    for act in account_list:
        db.session.merge(act)
    db.close()

    print 'Adding accounts finished!'

