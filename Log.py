__author__ = 'chzhu'

import logging
import Config

format = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
logging.basicConfig(filename=Config.LOG_FILE, format=format)


