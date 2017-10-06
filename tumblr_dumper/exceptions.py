class NoPostException(Exception):
    '''
    Raise if a tumblr blog have no post left.
    '''


class NetworkException(Exception):
    pass


class HTTPException(NetworkException):
    """
    Raise if http status is not OK (200).
    """


class ConnectionException(NetworkException):
    """
    Raise if could not return a valid response.
    """


class NoPostException(Exception):
    """
    raise if a tumblr blog has no post left.
    """
