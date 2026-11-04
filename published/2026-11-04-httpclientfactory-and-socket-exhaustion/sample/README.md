## What this demonstrates

This POC demonstrates how `HttpClientFactory` in .NET can lead to socket exhaustion when improperly configured, especially with a large number of concurrent requests. It shows how default settings may not handle high concurrency, resulting in connection leaks and system instability.

## How it works

The POC creates a test client using `HttpClientFactory` to make thousands of concurrent HTTP requests to a dummy endpoint. Each request uses a new `HttpClient` instance, but without proper lifetime management or connection reuse, sockets are not released. Over time, the number of open sockets grows, exhausting available system resources.

## How to run

1. Copy the code into a .NET 6+ console app.
2. Build and run with `dotnet run`.
3. Observe console output and monitor system socket usage (e.g., via `netstat` or Task Manager).

## Things to try

- Reduce the number of concurrent requests to see less socket growth.
- Modify the timeout or max concurrent connections in `HttpClientFactory`.
- Add a `Dispose` call or use `using` statements to ensure proper cleanup.
