# Global Exception Handling in .NET with Custom Filters and Resilience

**Topic:** Global Exception Handling  
**Category:** dotnet

# Global Exception Handling in .NET with Custom Filters and Resilience

In a real-world .NET app, exceptions aren’t just thrown—they propagate through layers, get logged, and can silently break user flows. Global exception handling lets you catch unhandled exceptions at the application level and respond consistently, whether it’s a database failure or a malformed request.

The standard way is using `Program.cs` with `HostBuilder` and `UseExceptionHandler`, but that’s limited. For richer control—like logging, user-facing messages, or retry logic—you need custom filters or middleware. In .NET 6+, this is easier with `IHostedService` and `IEndpointRouteBuilder`, but the real power comes from combining exception handling with resilience patterns like retry and circuit breaking.

I built a minimal proof-of-concept (POC) to show how to wrap global exception handling with a custom filter that logs errors and returns a consistent error response. The POC runs on a simple API with a single endpoint that simulates a failure by throwing an exception.

Here’s what I did:

- Created a custom exception filter that inherits from `IExceptionFilter`.
- Injected `ILogger` to log all unhandled exceptions with context (request path, user ID, etc.).
- Used `IHostedService` to run a background task that retries failed operations after a delay.
- Added a custom response filter to return a standardized error JSON instead of a 500 Internal Server Error.

The filter runs per-request, so it catches exceptions before they reach the final response. I tested it with a route that intentionally throws a `DivideByZeroException`. The app logs the error, and instead of crashing, it returns a clean error message: `{ "error": "An unexpected error occurred" }`.

What I learned:

- Global exception handling doesn’t just mean logging—it means shaping the user experience.
- Custom filters are more flexible than built-in middleware when you need per-exception behavior.
- Resilience patterns (like retry) must be applied *after* exception handling, not before, or you’ll loop in failures.
- Logging context (like request ID) is critical for debugging. Without it, errors are hard to trace.

Key Takeaways:

- Use custom exception filters for fine-grained control over error responses and logging.
- Combine exception handling with resilience patterns like retry, but apply them in a safe, bounded way.
- Always return user-friendly error messages—don’t expose internal stack traces.
- Test your error handling with intentional failures (e.g., divide-by-zero, null reference) to validate behavior.
- Avoid overusing retry—some exceptions (like network timeouts) should be handled with circuit breaking instead.

In practice, this setup works best in microservices or APIs where consistency in error responses matters. It’s not a silver bullet, but it’s a solid foundation for building reliable, maintainable services. The POC was small, but it proved that with minimal code, you can achieve predictable error behavior across your app.

The real value isn’t in catching every exception—it’s in making sure the app doesn’t just crash, but responds in a way that’s predictable and debuggable. That’s what developers actually need.
