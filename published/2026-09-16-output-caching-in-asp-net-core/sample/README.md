## What this demonstrates

This POC demonstrates how to implement output caching in ASP.NET Core to serve static responses from cache, reducing server load and improving response time for frequently accessed pages.

## How it works

Output caching stores the rendered HTML output of an action method in memory or on disk. When a request comes in, ASP.NET Core checks if a cached version exists. If yes, it serves the cached response; otherwise, it executes the action and caches the result. The cache is invalidated on updates or with cache keys.

```csharp
[ResponseCache(Duration = 300, Location = ResponseCacheLocation.Any)]
public IActionResult Index()
{
    return View();
}
```

## How to run

1. Run the ASP.NET Core app locally.
2. Access `/Index` in the browser.
3. Open DevTools to observe network requests and response headers.

## Things to try

- Change `Duration` to 10 seconds and observe cache refresh.
- Add a parameter to the action and test cache invalidation.
- Use `Location = ResponseCacheLocation.Server` to cache only on server.
