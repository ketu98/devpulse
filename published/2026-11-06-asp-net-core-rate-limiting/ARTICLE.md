# Implementing Rate Limiting in ASP.NET Core Applications

**Topic:** ASP.NET Core Rate Limiting  
**Category:** dotnet

# Implementing Rate Limiting in ASP.NET Core Applications

Rate limiting is a simple but effective way to prevent abuse of APIs—like too many requests from one IP or user. In ASP.NET Core, it’s built-in and easy to configure, but it’s not always obvious how to get it right in a real-world scenario.

## What I learned

I started with a basic setup using `AddRateLimiting` in `Program.cs`, which works for simple cases. The default behavior limits requests per minute per IP, which is good for most public APIs. But I quickly found that default settings don’t handle edge cases well—like when a client uses a proxy or when requests come from a shared network.

I built a minimal proof-of-concept (POC) to test this. I created a simple API endpoint that returns a status message. I used a memory-based rate limiter with a 10-second window and 5 requests per window. I ran a test script that sent 10 requests from the same IP in quick succession. The first 5 worked, the next 5 were rejected with a 429 status code. That confirmed the limiter was active.

But the POC also revealed a flaw: the limiter didn’t track per-user requests. If the app later supports authentication, you’d want to limit based on user identity, not just IP. That means you need to integrate with `IHttpContextAccessor` and use a custom policy that reads the user ID from the request.

I also tried using `IOptionsMonitor` to load rate limit settings from configuration. This allowed me to adjust limits dynamically—say, during a traffic spike—without restarting the app. It’s useful for staging environments or testing.

One gotcha: the default limiter doesn’t support custom headers or request scopes. If you want to apply different limits per route, you need to define policies per endpoint and apply them selectively. I used `UseRateLimiter` with `Policy.FromExpression` to create per-route rules.

## Key Takeaways

- Start with IP-based rate limiting for public APIs—it’s simple and effective.
- Use configuration to manage limits so they can be adjusted without code changes.
- For authenticated apps, extend rate limiting to user identity instead of IP.
- Test with realistic traffic patterns, including bursts and shared IPs.
- Consider the overhead of memory-based storage—especially under load—since in-memory caches can degrade under high concurrency.
- Always validate your limits with a test script that mimics real usage, not just one-off requests.

Rate limiting is not a silver bullet, but it’s a necessary layer for any API that serves public access. When implemented correctly, it protects your app from denial-of-service attacks and helps maintain stable performance. The key is to start small, validate behavior, and evolve the logic as your app grows.
