import logging
import aiohttp
import json
import json.decoder

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from .exceptions import *
from .utility import *


class TumblrPost(QuickAccessDict):
    """
    Tumblr post.
    """


class AsyncNetworkIO:
    """
    Same like NetworkIO, but it's asynchronous.
    """

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def get(self, url):
        logger.debug('GET {}'.format(url))
        try:
            r = await self.session.get(url)
            r = json.loads(await r.text())
        except aiohttp.ClientError as e:
            raise ConnectionException(e)
        except json.decoder.JSONDecodeError as e:
            raise ConnectionError(e)
        else:
            if r['meta']['status'] != 200:
                raise HTTPException(r['meta']['status'], r['meta']['msg'])
            else:
                return r


class AsyncTumblrFetcher:
    """
    Fetch posts from tumblr blog. Just like TumblrFetcher, but it's asynchronous.
    """
    API_URL = 'https://api.tumblr.com/v2/blog/{blog}/posts?reblog_info=true&offset={offset}&api_key={api_key}'

    def __init__(self, blog_identifier, api_key):
        self.blog = blog_identifier
        self.api_key = api_key
        self.network = AsyncNetworkIO()
        self.prev_result = None
        self.prev_offset = 0

    async def fetch(self):
        def is_first_fetch():
            return self.prev_result is None

        async def do_first_fetch():
            url = self.API_URL.format(blog=self.blog,
                                      offset=0,
                                      api_key=self.api_key)
            result = await self.network.get(url)
            result = QuickAccessDict(result)
            self.prev_result = result
            return [TumblrPost(r) for r in result.response.posts]

        async def do_fetch():
            url = self.API_URL.format(blog=self.blog,
                                      offset=self.prev_offset + 20,
                                      api_key=self.api_key)
            result = await self.network.get(url)
            result = QuickAccessDict(result)
            self.prev_result = result
            if (result.response.blog.total_posts >=
                    self.prev_result.response.blog.total_posts):
                self.prev_offset += 20
                return [TumblrPost(r) for r in result.response.posts]
            else:
                delta_posts = (self.prev_result.response.blog.total_posts
                               - result.response.blog.total_posts)
                self.prev_offset -= delta_posts
                return self.fetch()

        if is_first_fetch():
            result = await do_first_fetch()
        else:
            result = await do_fetch()

        if not result:
            raise NoPostException()
        else:
            return result


class AsyncTumblrDumper:
    """
    The generator is used to dump all posts from a tumblr blog.
    It iterate all posts without duplication.
    It's asynchronous.
    """

    def __init__(self, blog_identifier, api_key):
        self.tumblr_fetcher = AsyncTumblrFetcher(blog_identifier, api_key)
        self.buffer = UniqueQueue(key=lambda x: (x.id, x.timestamp))
        self.stop = False

    async def __aiter__(self):
        return self

    async def reload(self):
        result = await self.tumblr_fetcher.fetch()
        self.buffer.push_many(result)

    def total_posts(self):
        return self.tumblr_fetcher.prev_result.response.blog.total_posts

    async def __anext__(self):
        if len(self.buffer) > 0:
            return self.buffer.get()
        else:
            try:
                if self.stop:
                    raise NoPostException()
                else:
                    await self.reload()
            except NoPostException:
                self.stop = True
                if len(self.buffer) == 0:
                    await self.tumblr_fetcher.network.session.close()
                    raise StopAsyncIteration()
                else:
                    return self.buffer.get()
            else:
                return self.buffer.get()
