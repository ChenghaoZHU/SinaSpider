__author__ = 'chzhu'

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
