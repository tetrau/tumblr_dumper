import reprlib
import collections.abc
import collections
import operator
import logging
import pprint
import requests

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class NoPostException(Exception):
    '''
    Raise if a tumblr blog have no post left.
    '''


class QuickAccessDict:
    """
    A dict like object with shortcut that function like object in javascript.
    >>> data = {'key_a': 'value_a',
    ... 'key_b': 'value_b',
    ... 'key_c': [{'key_c1': 'value_c1'}, {'key_c2': 'value_c2'}],
    ... 'key_d':{'e':'f'}}
    >>> qad = QuickAccessDict(data)
    >>> qad.key_a
    'value_a'
    >>> qad.key_c
    [QuickAccessDict(data={'key_c1': 'value_c1'}), QuickAccessDict(data={'key_c2': 'value_c2'})]
    >>> qad.no_such_key
    Traceback (most recent call last):
        ...
    KeyError: 'no_such_key'
    >>> QuickAccessDict(qad) # doctest: +ELLIPSIS
    QuickAccessDict(data={'key_a': 'value_a', ... {'key_c2': 'value_c2'}], 'key_d': {'e': 'f'}})
    >>> qad.key_d
    QuickAccessDict(data={'e': 'f'})
    """

    def __init__(self, data):
        if isinstance(data, QuickAccessDict):
            self._data = data.to_dict()
        else:
            self._data = dict(data)

    def __repr__(self):
        return 'QuickAccessDict(data={})'.format(reprlib.repr(self._data))

    def to_dict(self):
        return self._data

    def __getattr__(self, item):
        if hasattr(self._data, item):
            return getattr(self._data, item)
        try:
            result = self._data[item]
        except KeyError:
            raise
        else:
            if isinstance(result, collections.abc.Mapping):
                return QuickAccessDict(result)
            elif isinstance(result, collections.abc.MutableSequence):
                return [QuickAccessDict(i) for i in result]
            else:
                return result


class NetworkIO:
    """
    Class controls the network io. It must have a get(self, url) method which return HTTP get
    response in dict.
    """

    def __init__(self):
        self.session = requests.session()


    def get(self, url):
        logger.debug('GET {}'.format(url))
        r = self.session.get(url).json()
        return r


class UniqueQueue:
    """
    A FIFO queue, but all items pass through the queue will be unique.
    >>> uq = UniqueQueue()
    >>> uq.push(1)
    >>> uq.push_many([1,2,3,4,5])
    >>> len(uq)
    5
    >>> def print_all(uq):
    ...     while True:
    ...         try:
    ...             print(uq.get(),end=',')
    ...         except IndexError:
    ...             break
    >>> print_all(uq)
    1,2,3,4,5,
    >>> non_hashable_items = [{'key': i} for i in range(3)]
    >>> non_hashable_items.append({'key': 2})
    >>> non_hashable_items
    [{'key': 0}, {'key': 1}, {'key': 2}, {'key': 2}]
    >>> uq.push_many(non_hashable_items) # put non-hashable will make it slower
    >>> print_all(uq)
    {'key': 0},{'key': 1},{'key': 2},
    >>> uqwk = UniqueQueue(key=operator.itemgetter('key')) # using key reduce memory usage, and faster in some case
    >>> uqwk.push_many(non_hashable_items)
    >>> print_all(uqwk)
    {'key': 0},{'key': 1},{'key': 2},
    """

    def __init__(self, key=None):
        self.key = (lambda x: x) if key is None else key
        self.hashable_record = set()
        self.non_hashable_record = []
        self.queue = collections.deque()

    def _push_hashable(self, item, key):
        if key in self.hashable_record:
            return
        else:
            self.hashable_record.add(key)
            self.queue.append(item)

    def _push_non_hashable(self, item, key):
        if key in self.non_hashable_record:
            return
        else:
            self.non_hashable_record.append(key)
            self.queue.append(item)

    def push(self, item):
        if isinstance(item, collections.abc.Hashable):
            self._push_hashable(item, self.key(item))
        else:
            self._push_non_hashable(item, self.key(item))

    def push_many(self, items):
        for item in items:
            self.push(item)

    def get(self):
        return self.queue.popleft()

    def __len__(self):
        return len(self.queue)


class TumblrPost(QuickAccessDict):
    """
    Tumblr post.
    """


class NoPostException(Exception):
    """
    raise if a tumblr blog has no post left.
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
