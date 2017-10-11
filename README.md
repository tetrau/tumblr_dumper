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

## API key
Check out the tumblr offical [api document](https://www.tumblr.com/docs/en/api/v2#auth).
