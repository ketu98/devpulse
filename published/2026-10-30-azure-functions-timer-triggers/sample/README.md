## What this demonstrates

This POC shows how to use Azure Functions with Timer Triggers to schedule precise, recurring workloads in C#. It demonstrates scheduling background tasks—like data backups or report generation—using a simple, lightweight serverless approach.

## How it works

The function runs on a schedule defined by a cron expression (e.g., every 5 minutes). It executes a C# method that logs a message to the console and writes a timestamped log entry. The function uses Azure Functions' built-in timer trigger to execute at specified intervals without requiring a persistent service.

## How to run

1. Clone or create a new Azure Functions project in C#.
2. Add a `TimerTrigger` attribute to a function.
3. Implement a method that logs a message using `ILogger`.
4. Deploy the function to Azure using the Azure CLI or Azure Portal.
5. Set the timer schedule (e.g., `0 */5 * * * *` for every 5 minutes).

## Things to try

- Change the schedule to run hourly or daily.
- Add a real task (e.g., process files, send email).
- Test with different time zones.
- Add error handling and retry logic.
