import requests_oauthlib
import socket


def tumblr_oauth_helper(client_key, client_secret, proxy=None):
    REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
    AUTHORIZE_URL = 'https://www.tumblr.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'
    oauth = requests_oauthlib.OAuth1Session(client_key=client_key,
                                            client_secret=client_secret,
                                            callback_uri='http://127.0.0.1:5000')
    if proxy:
        oauth.proxies.update({'https': proxy})
    oauth.fetch_request_token(REQUEST_TOKEN_URL)
    authorize_url = oauth.authorization_url(AUTHORIZE_URL)
    print('go to', authorize_url)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 5000))
    s.listen(1)
    conn, addr = s.accept()
    data = conn.recv(1024)
    request_line = data.decode().split('\n')[0]
    call_back_url = 'http://127.0.0.1' + request_line.split()[1]
    print(call_back_url)
    oauth.parse_authorization_response(call_back_url)
    return oauth.fetch_access_token(ACCESS_TOKEN_URL)
