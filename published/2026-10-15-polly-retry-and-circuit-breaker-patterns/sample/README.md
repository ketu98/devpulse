## What this demonstrates

This POC demonstrates implementing the Polly Retry and Circuit Breaker patterns in .NET to improve resilience in distributed systems. It shows how to handle transient failures and prevent cascading failures in API calls.

## How it works

The code uses Polly to wrap a simulated HTTP call with retry logic (up to 3 attempts) and a circuit breaker (that opens after 3 failures). On failure, it retries with exponential backoff and stops if too many failures occur. The circuit breaker prevents further calls when the system is down.

## How to run

1. Open the project in Visual Studio or .NET CLI.
2. Build and run the console app.
3. Observe output: successful calls, retries, and circuit breaker opening after failures.

## Things to try

- Modify the retry count or delay to see impact on performance.
- Change the failure threshold to test circuit breaker behavior.
- Replace the mock service with a real API to observe real-world behavior.
