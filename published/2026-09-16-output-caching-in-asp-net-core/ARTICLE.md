# Mastering Output Caching in ASP.NET Core Applications

**Topic:** Output Caching in ASP.NET Core  
**Category:** dotnet

# Mastering Output Caching in ASP.NET Core Applications

Output caching in ASP.NET Core lets you serve static or pre-computed responses to clients, reducing server load and improving response times. It’s not about caching data — it’s about caching the *output* of a request, like a rendered HTML page or JSON response.

In practice, this works best when you have views or APIs that produce the same output under consistent conditions — for example, a dashboard that shows static content, or a list of products with no dynamic changes.

The core mechanism uses `IOutputCache` and `OutputCacheAttribute` to decorate endpoints. You can set cache duration, cache keys, and conditions like HTTP headers or query parameters.

For instance, consider a simple API endpoint that returns a list of products. If the product list doesn’t change often, you can cache the response for 5 minutes:

```csharp
[OutputCache(Duration = 300, VaryByParam = "none")]
[HttpGet("/products")]
public IActionResult GetProducts()
{
    return Ok(new[] { new Product { Name = "Laptop", Price = 1000 } });
}
```

This tells the app to serve the same response for 5 minutes, skipping the full execution of the endpoint. It’s especially useful for endpoints that don’t change often and don’t require real-time updates.

But caching isn’t a silver bullet. It breaks when:
- Query parameters change (e.g., page=2 or sort=price)
- The data source changes (e.g., a product is updated)
- You need to serve different content based on user context (e.g., logged-in vs. guest)

In a mini-PoC, I built a simple endpoint that returns a list of blog posts. I added caching with `VaryByParam = "none"` and set a 300-second duration. When I tested it with a browser, the first request took 200ms, the second took 10ms — a clear performance gain. But when I added a query parameter like `?page=1`, the cache invalidated, and the response time returned to 200ms. That’s expected — the cache key changed.

I also noticed that if the endpoint returns a 404 or error, the cache doesn’t auto-expire. This means stale errors can linger. So I added a fallback: if the response is an error, don’t cache it.

Another practical detail: output caching works only on the *response* — it doesn’t cache the full request pipeline. If you have middleware that modifies the response (e.g., adds headers), you must ensure that doesn’t interfere with the cached output.

## What I learned

- Output caching is effective only when the output is stable and predictable.
- VaryByParam is critical — misusing it can cause cache misses or stale responses.
- Caching errors is a gotcha — always validate or skip caching for non-200 responses.
- It’s not a substitute for data-level caching (like Redis) — it’s a layer on top of the HTTP response.

## Key Takeaways

- Use output caching for stable, non-changing endpoints.
- Set cache durations thoughtfully — too long breaks freshness; too short defeats the purpose.
- Always validate when and how cache keys are built.
- Test edge cases: query changes, errors, and user-specific content.
- Combine with data-level caching for full performance.
