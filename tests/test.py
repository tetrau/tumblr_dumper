import sys
import os
import logging
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tumblr_dumper

api_key = os.getenv('api_key')
logger = logging.getLogger('tumblr_dumper')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
tumblr_fetcher = tumblr_dumper.TumblrFetcher('staff', api_key=api_key)
f = open('dump', 'w+')
while True:
    try:
        r = tumblr_fetcher.fetch()
        time.sleep(1)
    except tumblr_dumper.NoPostException:
        break
    else:
        for post in r:
            f.write(json.dumps(post.to_dict()))
f.close()
logger.debug('Finish')
