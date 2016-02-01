__author__ = 'chzhu'

import time, random
import Config

# decorators
def star_segment(func):
    """
    decorator which encloses printed contents with stars
    :param func:
    :return:
    """
    def _star_segment(content):
        print '********************************************************************************'
        func(content)
        print '********************************************************************************'
    return _star_segment
def Excalibur(func):
    """
    a decorator which guarantees the success of running func
    :param func:
    :return:
    """
    def _Excalibur(opener, url):
        while True:
            try:
                return func(opener, url)
            except Exception as e:
                print e
                if 'HTTP Error 501: Not Implemented' in e.message:
                    time.sleep(random.randint(Config.SLEEP_WHEN_EXCEPTION, 2*Config.SLEEP_WHEN_EXCEPTION))
    return _Excalibur

# utilities
@Excalibur
def open_url(opener, url):
    return opener.open(url, timeout=30).read()
@star_segment
def emphasis_print(content):
    print content

def loop_increase(integer, base):
    """
    increase integer by 1 if it exceeds base then reset integer
    :param integer:
    :param base:
    :return:
    """
    return (integer + 1) % base

def strip_blanks(string):
    string = string.replace('\r', '').replace('\n', '').replace('\t', '')
    string = string.strip(' ')
    return string
def deparentheses(string):
    """
    strip '(' and ')'
    :param string:
    :return:
    """
    return string.strip('(').strip(')')