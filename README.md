## MyCrawler
A web crawler with async coroutine.

#### Project Structure

- Single thread for each process, async/await for coroutine. No GIL, no fetcher class and callbacks of callbacks.
- Use (url, redirect_left) to avoid multiple URLs redirecting to the same end URL, if the redirecs are handled by web server.


#### Tests

by querying DB
  - seprate client / server network environment
  - use aiomysql to manage connection pool (set to 10 for testing)
  - run aiohttp on gunicorn, set workers to be 5

by calling API
  - to be implemented

#### Future Features

1. Bloom Filter for URL filtering.
2. Redis for better URL queue, HTML queue and item queue.
3. Multiple processes on different machines, making it a distributed crawler.
