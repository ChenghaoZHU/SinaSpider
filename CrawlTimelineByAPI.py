__author__ = 'chzhu'

from APISpider import Spider

if __name__ == '__main__':

    spider = Spider()
    spider.get_timelines('5540589017', '1')