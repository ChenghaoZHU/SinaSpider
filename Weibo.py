#-*- coding: UTF-8 -*-
__author__ = 'chzhu'

from Utility import open_url
import cookielib, urllib2, urllib
import re, json
import base64, rsa, binascii
import random
import StringIO, Image

class Weibo(object):
    def __init__(self):

        self.server_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_=1379834957683'
        self.login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
        self.post_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}

    def login(self, user):
        """

        :param user:
        :return: a url opener logined by the user, if login fails, return None
        """
        print 'User: ', user.acct
        print 'login...'
        opener = self.init_opener()
        server_data = self.get_server_data(opener)

        post_data = self.encrypt_post_data(user, server_data)

        redirect_response = self.get_redirect_response(post_data, opener)

        while 'retcode=0' not in redirect_response:
            if 'retcode=101' in redirect_response:
                print 'User Name or Password is not correct!'
                return None
            else: # need captcha
                print 'Captcha Needed!'
                verification_url = 'http://login.sina.com.cn/cgi/pin.php?r=' + str(random.randint(1, 1000000)) + '&s=0&p=' + server_data['pcid']
                response = opener.open(verification_url).read()
                captcha = StringIO.StringIO(response)
                img = Image.open(captcha)
                # img.show() # for windows
                img.convert('RGB').save('captcha.jpg')
                from subprocess import call
                call(['cacaview', 'captcha.jpg']) # for linux, it's noting that you should install caca-utils at first

                captcha = raw_input('Input the verification code:')

                post_data['door'] = captcha
                post_data['pagerefer'] = ''
                post_data['pcid'] = server_data['pcid']
                post_data['sp'] = self.encrypt_user_passwd(user.pswd, server_data)

                redirect_response = self.get_redirect_response(post_data, opener)
                if 'retcode=0' in redirect_response:
                    print 'Success!'
                elif 'retcode=2093' in redirect_response:
                    print 'Login fails, please try again.'
                elif 'retcode=2070' in redirect_response:
                    print 'Invalid verification code! Please try again.'

        try:
            redirect_url = self.get_redirect_url(redirect_response)
            opener.open(redirect_url, timeout=30)
        except Exception as e:
            print e
            return None

        return opener

    def init_opener(self):
        cookie_jar = cookielib.LWPCookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        return opener

    def get_redirect_url(self, redirect_response):
        pattern = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        url = pattern.search(redirect_response).group(1)
        print 'redirect url:', url
        return url
    def get_redirect_response(self, post_data, opener):
         post_data = urllib.urlencode(post_data)
         request = urllib2.Request(self.login_url, post_data, self.post_header)

         while True:
             try:
                 print "Posting encrypted message..."
                 return opener.open(request).read()
             except Exception as e:
                 print e

    def get_server_data(self, opener):
        print "Getting server time and nonce..."

        server_data = open_url(opener, self.server_url) # get sever_data
        return self.parse_server_data(server_data)
    def parse_server_data(self, server_data):
        pattern = re.compile('\((.*)\)')
        json_data = pattern.search(server_data).group(1)
        data = json.loads(json_data)

        parsed_server_data = {}
        parsed_server_data['servertime'] = str(data['servertime'])
        parsed_server_data['nonce'] = data['nonce']
        parsed_server_data['pubkey'] = data['pubkey']
        parsed_server_data['rsakv'] = data['rsakv']
        parsed_server_data['pcid'] = data['pcid']

        for key in parsed_server_data:
            print '%s : %s' % (key, parsed_server_data[key])

        return parsed_server_data

    def encrypt_user_name(self, user_name):
        """
        encrypt user name with base64
        :param user_name:
        :return:
        """
        encrypted_user_name = urllib.quote(user_name)
        return base64.encodestring(encrypted_user_name)[:-1]
    def encrypt_user_passwd(self, user_passwd, server_data):
        """
        encrypt user password with rsa
        :param user_passwd:
        :param server_data:
        :return:
        """
        public_key = int(server_data['pubkey'], 16)
        public_key = rsa.PublicKey(public_key, 65537) # generate public key

        message = str(server_data['servertime']) + '\t' + str(server_data['nonce']) + '\n' + str(user_passwd) # group message
        encrypted_message = rsa.encrypt(message, public_key) # encrypt message
        encrypted_passwd = binascii.b2a_hex(encrypted_message) # translate encrypted message to hexadecimal

        return encrypted_passwd
    def encrypt_post_data(self, user, serve_data):
        encrypted_user_name = self.encrypt_user_name(user.acct)
        encrypted_user_passwd = self.encrypt_user_passwd(user.pswd, serve_data)

        post_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': encrypted_user_name,
            'service': 'miniblog',
            'servertime': serve_data['servertime'],
            'nonce': serve_data['nonce'],
            'pwencode': 'rsa2',
            'sp': encrypted_user_passwd,
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': serve_data['rsakv'],
            'pcid':"",
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        return post_data






