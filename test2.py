# s = b'<HTML><HEAD><TITLE>Buttercup'

# with open('crawl_result.txt', 'ab') as f:
#     f.write(s + b'\n')

from my_crawler import UrlFilter

filter = UrlFilter()
print(filter.should_add('javascript: dfasdfa '))