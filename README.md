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

The post that iterated from TumblrDumper will be an instance of TumblrPost.
```python
>>> post.to_dict()
{'blog_name': 'staff', ...}
>>> post.blog_name # Equivalent to post.to_dict['id']
'staff'
```

## Exceptions
It is now known that wrong blog name will raise `tumblr_dumper.exceptions.HTTPException((404, 'Not Found'))`.

 And wrong api key will raise `tumblr_dumper.exceptions.HTTPException((401, 'Unauthorized'))`.

## API key
Check out the tumblr offical [api document](https://www.tumblr.com/docs/en/api/v2#auth).
