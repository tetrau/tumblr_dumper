# tumblr_dumper: dump all posts from a tumblr blog

## Usage
```python
import os
from tumblr_dumper import TumblrDumper


API_KEY = os.getenv('api_key') # the tumblr api key
BLOG = 'staff'
td =  TumblrDumper(BLOG, API_KEY)
for post in td:
    print(post)
    # do something with the post
```
It's that **>>simple<<**.

Or, use `tumblr.async`

```python
import os
from tumblr_dumper.async import AsyncTumblrDumper
import asyncio


API_KEY = os.getenv('api_key')
BLOG = 'staff'
async def main():
    td = AsyncTumblrDumper(BLOG, API_KEY)
    async for post in td:
        print(post)
        # do something with the post

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

The post that iterated from TumblrDumper will be an instance of TumblrPost.
```python
>>> post.to_dict()
{'blog_name': 'staff', ...}
>>> post.blog_name # Equivalent to post.to_dict['id']
'staff'
```
## Using HTTP proxy
```python
tp = TumblrDumper(BLOG, API_KEY,
                  proxy='http://127.0.0.1:1024')
# or
tp = TumblrDumper(BLOG, API_KEY,
                  proxy='http://user:password@127.0.0.1:1024')
```
## Using OAuth1.0a
```python
oauth = {'client_key':'...',
         'client_secret':'...',
         'resource_owner_key':'...',
         'resource_owner_secret':'...'}
tp = TumblrDumper(BLOG, API_KEY, oauth=oauth)
```
Notice that **oauth will override api_key**.
## Exceptions
It is now known that wrong blog name will raise `tumblr_dumper.exceptions.HTTPException((404, 'Not Found'))`.

 And wrong api key will raise `tumblr_dumper.exceptions.HTTPException((401, 'Unauthorized'))`.

## Handle exceptions in for loop
when exception rasied in an iterator, for loop will break and can't continue again.
You can write an exception_handler to handle exceptions inside for loop.
```python
from tumblr_dumper import TumblrDumper, ConnectionException
class MyTumblrDumper(TumblrDumper):
    def __init__(self, *args, **kwargs):
        self.retry = 0
        super().__init__(*args, **kwargs)
    # write a subclass of TumblrDumper and override exception_handler method.
    # exception_handler takes two position arguments. self and the raised exception.
    # return self.RAISE_EXCEPTION or None rasied the exception.
    # return self.CONTINUE or anything but None will continue the for loop.
    def exception_handler(self, e):
        if isinstance(e, ConnectionException):
            if self.retry == 5:
                print('retry too many times')
                raise StopIteration()
            self.retry += 1
            print(e)
            print('sleep 5 sec')
            time.sleep(5)
            return self.CONTINUE
```


## API key
Check out the tumblr offical [api document](https://www.tumblr.com/docs/en/api/v2#auth).
