import sys
import os
import logging
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tumblr_dumper import TumblrDumper

api_key = os.getenv('api_key')
http_proxy = os.getenv('http_proxy')
oauth = {'client_key': os.getenv('client_key'),
         'client_secret': os.getenv('client_secret'),
         'resource_owner_key': os.getenv('resource_owner_key'),
         'resource_owner_secret': os.getenv('resource_owner_secret')}
logger = logging.getLogger('tumblr_dumper')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

tumblr_dumper = TumblrDumper('staff', api_key=api_key, proxy=http_proxy, oauth=oauth)

count = 0

for post in tumblr_dumper:
    count += 1
    print('fetch posts {:06}/{:06}'.format(count, tumblr_dumper.blog_info.total_posts))
    time.sleep(0.05)

logger.debug('Finish')
