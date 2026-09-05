## What this demonstrates

This POC shows how to implement global exception handling in .NET using custom filters and resilience patterns. It demonstrates catching unhandled exceptions across controllers, logging errors, and returning consistent error responses to clients.

## How it works

A global exception filter is applied to all actions. When an exception occurs, the filter intercepts it, logs the error using a simple logger, and returns a standardized JSON error response. Resilience is added via retry logic for transient errors using Polly, applied at the controller level.

## How to run

1. Open the project in Visual Studio or VS Code.
2. Ensure the project targets .NET 6+.
3. Run `dotnet run` to start the application.
4. Access `/api/test` to trigger a test exception.
5. Observe the error response and logs in the console.

## Things to try

- Modify the exception filter to include detailed error messages in logs.
- Add custom headers or status codes to error responses.
- Test with different exception types (e.g., NullReference, DivideByZero).
- Replace Polly with a custom retry policy using a timeout.
