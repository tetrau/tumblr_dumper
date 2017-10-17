import sys
import os
import logging
import time
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tumblr_dumper.async import AsyncTumblrDumper

api_key = os.getenv('api_key')
logger = logging.getLogger('tumblr_dumper')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

count = 0


async def main():
    global count
    tumblr_dumper = AsyncTumblrDumper('staff', api_key=api_key)
    async for post in tumblr_dumper:
        count += 1
        print('fetch posts {:06}/{:06}'.format(count, tumblr_dumper.blog_info.total_posts()))
        time.sleep(0.05)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

logger.debug('Finish')