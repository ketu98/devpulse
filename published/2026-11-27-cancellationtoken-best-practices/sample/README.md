## What this demonstrates

This POC demonstrates best practices for using `CancellationToken` in .NET applications to enable graceful cancellation of long-running operations, such as downloads or background tasks.

## How it works

The example shows a background task that listens for cancellation via a `CancellationToken`. When the token is triggered (e.g., via user action or timeout), the task safely exits using `CancellationToken.ThrowException()` and logs a cancellation message.

## How to run

1. Copy the code into a .NET Console App project.
2. Build and run the app.
3. Press Ctrl+C in the terminal to trigger cancellation.
4. Observe the output showing cancellation logic in action.

## Things to try

- Modify the delay in the task to test different cancellation times.
- Add a progress report to show real-time updates during operation.
- Use `CancellationToken` in a `Task.Run` with a timeout to simulate network operations.
- Apply it to a file download or HTTP request to see real-world benefits.
