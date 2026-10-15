# Implementing Polly Retry and Circuit Breaker Patterns in .NET

**Topic:** Polly Retry and Circuit Breaker Patterns  
**Category:** dotnet

# Implementing Polly Retry and Circuit Breaker Patterns in .NET

In a recent side project, I needed to handle unreliable external APIs—some of which occasionally return 500s or timeout. I wanted to avoid crashing the app on transient failures and ensure recovery without manual retry logic. That’s when I turned to Polly, a lightweight .NET library that helps implement retry and circuit breaker patterns.

Polly is not a full-blown framework—it’s a set of policies you compose. It’s simple to integrate, and once configured, it handles the complexity of retry backoffs, failure detection, and state management.

I built a minimal proof-of-concept to test it. The setup was a simple HTTP client calling a mock endpoint that occasionally returns a 500 error (simulated via a random condition). I used `Polly.RetryPolicy` with exponential backoff and a max of 3 attempts. I also added a `CircuitBreakerPolicy` to prevent repeated failures from overwhelming the system.

Here’s the core code:

```csharp
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .OrResult<HttpResponseMessage>(r => r.StatusCode == System.Net.HttpStatusCode.InternalServerError)
    .WaitAndRetryAsync(
        retryCount: 3,
        sleepDurationProvider: retryAttempt => TimeSpan.FromMilliseconds(Math.Pow(2, retryAttempt)),
        onRetry: (exception, retryAttempt, context) =>
        {
            Console.WriteLine($"Attempt {retryAttempt} failed. Retrying in {sleepDurationProvider(retryAttempt)}...");
        });

var circuitBreaker = Policy
    .Handle<HttpRequestException>()
    .OrResult<HttpResponseMessage>(r => r.StatusCode == System.Net.HttpStatusCode.InternalServerError)
    .CircuitBreakerAsync(
        handleTimeout: TimeSpan.FromSeconds(30),
        allowFailures: 5,
        onOpen: (ex, context) => Console.WriteLine("Circuit breaker opened. Service is likely down."),
        onReset: (context) => Console.WriteLine("Circuit breaker reset. Service may be back online.")
    );

var result = await circuitBreaker.ExecuteAsync(async () =>
    await retryPolicy.ExecuteAsync(async () =>
        await httpClient.GetAsync("https://mock-endpoint.com/api/data")
    )
);
```

The flow is clear: if a request fails, it retries with increasing delays. If it fails 5 times in 30 seconds, the circuit breaker opens—no more calls are made. After 30 seconds, it resets and allows new attempts.

## What I learned

- Retry policies should be applied to specific failure types, not all exceptions. Broad exceptions can mask real issues.
- Exponential backoff is effective for avoiding overwhelming a server with repeated requests.
- Circuit breakers are useful for detecting systemic failures, but they should not be used for every call—only when you have a long-running, external dependency.
- The policies are composable. You can chain them, and the execution order matters.

## Key Takeaways

- Use Polly for transient error handling in production-like scenarios.
- Define clear failure conditions and limits to avoid infinite loops or over-retry.
- Test with realistic failure patterns—mocking 500s or timeouts is essential.
- Keep policies isolated and reusable. Don’t hardcode values; use configuration for flexibility.
- Monitor state changes (like circuit breaker open) in logs to understand system health.
