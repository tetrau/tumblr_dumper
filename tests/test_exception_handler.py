import sys
import os
import logging
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tumblr_dumper import TumblrDumper, HTTPException

api_key = 'WrongAPIKey'
logger = logging.getLogger('tumblr_dumper')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MyTumblrDumper(TumblrDumper):
    def __init__(self, *args, **kwargs):
        self.retry = 0
        super().__init__(*args, **kwargs)

    def exception_handler(self, e):
        if isinstance(e, HTTPException):
            if self.retry == 5:
                print('retry too many times')
                raise StopIteration()
            self.retry += 1

            print(e)
            print('sleep 5 sec')
            time.sleep(5)
            return True


tumblr_dumper = MyTumblrDumper('staff', api_key=api_key)
count = 0

for post in tumblr_dumper:
    count += 1
    print('fetch posts {:06}/{:06}'.format(count, tumblr_dumper.blog_info.total_posts))
    time.sleep(0.05)

logger.debug('Finish {} posts fetched'.format(count))
