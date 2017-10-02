import reprlib
import collections.abc


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
