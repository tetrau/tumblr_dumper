import logging
import requests
import requests.exceptions

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from .exceptions import *
from .utility import *


class NetworkIO:
    """
    Class controls the network io. It must have a get(self, url) method which return HTTP get
    response in dict.
    """

    def __init__(self):
        self.session = requests.session()

    def get(self, url):
        logger.debug('GET {}'.format(url))
        try:
            r = self.session.get(url).json()
        except requests.exceptions.RequestException:
            raise ConnectionException()
        else:
            if r['meta']['status'] != 200:
                raise HTTPException(r['meta']['status'], r['meta']['msg'])
            else:
                return r


class TumblrPost(QuickAccessDict):
    """
    Tumblr post.
    """


class TumblrFetcher:
    """
    Fetch posts from tumblr blog.
    ------------mechanism------------
    posts:    00 01 02 03 04 05 06 07 08 09
    get:        |01 02 03|
    # bloger delete an post
    posts:    01 02 03 04 05 06 07 08 09
    get:                 |05 06 07|
    # oop! 04 is missing! so offset -= (total_post_now - total_posts_before)
    posts:    01 02 03 04 05 06 07 08 09
    get:              |04 05 06|
    # everything moves on...
    posts:    01 02 03 04 05 06 07 08 09
    get:                       |07 08 09|
    ------------mechanism------------
    Just call .fetch() repeatedly, it will return lists of TumblrBlog (There may be duplication).
    When done, exception NoPostException will raise.
    """
    API_URL = 'https://api.tumblr.com/v2/blog/{blog}/posts?reblog_info=true&offset={offset}&api_key={api_key}'

    def __init__(self, blog_identifier, api_key):
        self.blog = blog_identifier
        self.api_key = api_key
        self.network = NetworkIO()
        self.prev_result = None
        self.prev_offset = 0

    def fetch(self):
        def is_first_fetch():
            return self.prev_result is None

        def do_first_fetch():
            url = self.API_URL.format(blog=self.blog,
                                      offset=0,
                                      api_key=self.api_key)
            result = self.network.get(url)
            result = QuickAccessDict(result)
            self.prev_result = result
            return [TumblrPost(r) for r in result.response.posts]

        def do_fetch():
            url = self.API_URL.format(blog=self.blog,
                                      offset=self.prev_offset + 20,
                                      api_key=self.api_key)
            result = self.network.get(url)
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
            result = do_first_fetch()
        else:
            result = do_fetch()

        if not result:
            raise NoPostException()
        else:
            return result


class TumblrDumper:
    """
    The generator is used to dump all posts from a tumblr blog.
    It iterate all posts without duplication.
    """

    def __init__(self, blog_identifier, api_key):
        self.tumblr_fetcher = TumblrFetcher(blog_identifier, api_key)
        self.buffer = UniqueQueue(key=lambda x: (x.id, x.timestamp))
        self.stop = False

    def __iter__(self):
        return self

    def reload(self):
        result = self.tumblr_fetcher.fetch()
        self.buffer.push_many(result)

    def total_posts(self):
        return self.tumblr_fetcher.prev_result.response.blog.total_posts

    def __next__(self):
        if len(self.buffer) > 0:
            return self.buffer.get()
        else:
            try:
                if self.stop:
                    raise NoPostException()
                else:
                    self.reload()
            except NoPostException:
                self.stop = True
                if len(self.buffer) == 0:
                    raise StopIteration()
                else:
                    return self.buffer.get()
            else:
                return self.buffer.get()
