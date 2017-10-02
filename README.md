## MyCrawler
An async web crawler using coroutines.

### Project Structure

- Single thread for each process, async/await for coroutine. No GIL, no fetcher class and callbacks of callbacks.
- Use (url, redirect_left) to avoid multiple URLs redirecting to the same end URL, if the redirecs are handled by web server.
- Use set or Bloom Filter for URL filtering.

Fetcher, Parser Saver not necessarily needed, since a coroutines triggered is able to store its state in local variables like a function does. In fact, function is a special case of coroutine.

#### How coroutines are used to minimize wait on I/O 

1. asyncio.Task(coro) wraps the coroutine in a future, and there will only be one task running in one event loop.
```
tasks_list = [asyncio.Task(self._work(index + 1), loop=self._loop)
              for index in range(self._num_fetchers)]
```

2. inside of _work(), fetch() is called, that coroutine will be suspended on the line below
```
fetch_result, content = await self._fetcher.fetch(url, max_redirect)
```

3. inside of fetch(), use the session provided by aiohttp to get response, similarly, that coroutine will be suspended on the line below
```
response = await self._session.get(
    url, allow_redirect=False, timeout=5
)
```

#### Tests

by crawling sites
  - use default settings

by querying DB
  - to be implemented
  - seprate client / server network environment
  - use aiomysql to manage connection pool (set to 10 for testing)
  - run aiohttp on gunicorn, set workers to be 5

by calling API
  - to be implemented

### Future Features

1. Items able to be saved to DB.
2. Redis for better URL queue, HTML queue and item queue.
3. Multiple processes on different machines, making it a distributed crawler.
