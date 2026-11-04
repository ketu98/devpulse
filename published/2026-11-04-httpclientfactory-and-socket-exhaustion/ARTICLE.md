# Understanding HttpClientFactory and Socket Exhaustion in .NET

**Topic:** HttpClientFactory and Socket Exhaustion  
**Category:** dotnet

# Understanding HttpClientFactory and Socket Exhaustion in .NET

In a recent project, I was tasked with improving the reliability of HTTP calls made by a background service that polls external APIs. Initially, the service used `HttpClient` instances directly—creating a new instance per call. While this worked for small-scale usage, we started seeing intermittent connection failures, especially under load. After some debugging, I realized the root cause wasn’t the API itself—it was socket exhaustion.

## What I learned

`HttpClient` is not thread-safe and should not be reused across threads without proper configuration. When you create a new `HttpClient` instance per call, each one holds a socket connection. If you have many concurrent requests, and each one keeps its own `HttpClient`, you quickly exhaust the available socket connections on the process. On Windows, the default limit is around 65,535 sockets, but even that can be hit with a few hundred concurrent calls.

I built a minimal proof-of-concept (POC) to demonstrate this. The POC spins up a thread pool with 100 threads, each making 100 HTTP calls to a public endpoint (e.g., `https://httpbin.org/get`). Each thread creates its own `HttpClient` instance. After 10 seconds, the app crashes with a socket error—specifically, `System.Net.Sockets.SocketException: 'Only 1000 sockets available'`.

I then replaced the per-call `HttpClient` with `HttpClientFactory`, which allows you to create a shared, pooled `HttpClient` instance. The factory manages lifecycle and reuses connections. In the same POC, with the same 100 threads and 100 calls, the app runs smoothly for 30 seconds without errors.

The difference is clear: without `HttpClientFactory`, each request consumes a socket. With it, connections are reused, and the socket pool is managed efficiently.

## Key Takeaways

- Never create a new `HttpClient` per request. It leads to socket exhaustion under load.
- Use `HttpClientFactory` to manage a shared, reusable client instance. This reduces socket usage and improves stability.
- Configure `HttpClientFactory` with proper settings like `MaxPoolSize`, `ConnectionLifetime`, and `Timeout` to match your workload.
- In production, monitor socket usage and connection pool metrics—especially when calling external services.
- Even small services with many background calls can hit socket limits. A simple refactor can prevent runtime failures.

In practice, this isn’t just about code—it’s about understanding how network resources are consumed. A well-designed HTTP client setup is a foundational part of robust, scalable .NET applications. The POC didn’t require complex setup—just a few lines of code and a clear understanding of how sockets work under the hood.

If you're building services that make many HTTP calls, treat `HttpClient` like a resource pool. Reuse, don’t create. It’s not glamorous, but it’s essential.
