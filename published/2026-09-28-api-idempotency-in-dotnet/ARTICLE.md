# Implementing API Idempotency in .NET Services

**Topic:** API Idempotency  
**Category:** dotnet

# Implementing API Idempotency in .NET Services

In a real-world service, I often see duplicate requests—especially when clients retry after network errors. These retries can cause unintended side effects: multiple orders processed, payments applied twice, or inventory reduced unnecessarily. Idempotency helps prevent that by ensuring that a request has the same effect regardless of how many times it's sent.

Idempotency isn’t about making requests fail on duplicates. It’s about making them *safe* to repeat. For example, placing an order once or ten times should result in the same final state: one order placed, inventory updated, payment applied.

In .NET, you can implement idempotency by introducing a unique identifier—like a request ID—on each incoming request. When the service receives a request, it checks whether that ID has already been processed. If yes, it returns a response indicating the action was already completed. If no, it processes the request and stores the ID in a temporary store (like a memory cache or in-database record).

Here’s a minimal working example in a .NET API:

```csharp
[HttpPost("order")]
public async Task<IActionResult> CreateOrder([FromBody] OrderRequest request)
{
    var idempotencyKey = request.IdempotencyKey ?? Guid.NewGuid().ToString();

    // Check if we've already processed this key
    if (await _cache.GetAsync(idempotencyKey) is not null)
    {
        return new OkObjectResult(new { Message = "Request already processed" });
    }

    // Process the request
    await _orderService.CreateOrder(request);

    // Store the key so we don't reprocess
    await _cache.SetAsync(idempotencyKey, true, TimeSpan.FromMinutes(10));

    return new CreatedResult($"/orders/{request.Id}", new { Message = "Order created" });
}
```

This POC uses a simple in-memory cache (like `IMemoryCache` or `Redis`) to track processed keys. The key is stored with a TTL—say 10 minutes—so old requests don’t block new ones. In production, you’d use a persistent store (like a database) to avoid cache loss on restarts.

What I learned:
- Idempotency is not a feature to add for "nice-to-have" — it’s a necessity when retries are unavoidable.
- The key is not just generated; it must be validated and stored consistently.
- Using a well-defined key (e.g., a UUID or string) ensures uniqueness and avoids collisions.
- You don’t need to validate the entire request body—just the key. The rest of the logic can be idempotent by design.

Key Takeaways:
- Always consider idempotency when designing APIs that can be retried.
- Use a unique identifier (like `IdempotencyKey`) passed in the request.
- Store the key in a short-lived cache or database to avoid state drift.
- Keep the core business logic idempotent—e.g., update a record once, not multiple times.
- Test with duplicate requests to verify no side effects occur.

This pattern is simple, effective, and fits well with existing .NET tooling. It doesn’t require major refactors or new infrastructure—just a few lines of code and a clear design decision.
