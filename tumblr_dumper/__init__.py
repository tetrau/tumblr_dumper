import reprlib
import collections.abc
import collections
import functools
import operator


class QuickAccessDict:
    """
    A dict like object with shortcut that function like object in javascript.
    >>> data = {'key_a': 'value_a',
    ... 'key_b': 'value_b',
    ... 'key_c': [{'key_c1': 'value_c1'}, {'key_c2': 'value_c2'}]}
    >>> qad = QuickAccessDict(data)
    >>> qad.key_a
    'value_a'
    >>> qad.key_c
    [<QuickAccessDict data={'key_c1': 'value_c1'}>, <QuickAccessDict data={'key_c2': 'value_c2'}>]
    >>> qad.no_such_key
    Traceback (most recent call last):
        ...
    KeyError: 'no_such_key'
    """

    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return '<QuickAccessDict data={}>'.format(reprlib.repr(self._data))

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
    Class controls the network io. It must have a get(self, url, header) method which return HTTP get
    response in str.
    """

    def get(self, url, header):
        pass


class UniqueQueue:
    """
    A FIFO queue, but all items pass through the queue will be unique.
    >>> uq = UniqueQueue()
    >>> uq.push(1)
    >>> uq.push_many([1,2,3,4,5])
    >>> len(uq)
    5
    >>> def print_all():
    ...     while True:
    ...         try:
    ...             print(uq.get(),end=',')
    ...         except IndexError:
    ...             break
    >>> print_all()
    1,2,3,4,5,
    >>> non_hashable_items = [{'key': i} for i in range(3)]
    >>> non_hashable_items.append({'key': 2})
    >>> non_hashable_items
    [{'key': 0}, {'key': 1}, {'key': 2}, {'key': 2}]
    >>> uq.push_many(non_hashable_items) # put non-hashable will make it slower
    >>> print_all()
    {'key': 0},{'key': 1},{'key': 2},
    >>> uqwk = UniqueQueue(key=operator.itemgetter('key')) # using key reduce memory usage, and faster in some case
    >>> uqwk.push_many(non_hashable_items)
    >>> uqwk.queue
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
