## What this demonstrates

This POC shows how to implement a `BackgroundService` in ASP.NET Core to run long-running tasks independently of HTTP requests, such as monitoring, data processing, or periodic checks.

## How it works

The `BackgroundService` inherits from `BackgroundService` and overrides `ExecuteAsync` to run a task (e.g., logging or polling) in the background. It uses `IHostedService` to register the service in the application lifecycle. The service runs continuously until the app shuts down.

## How to run

1. Create a new ASP.NET Core project using `dotnet new webapp`.
2. Add a class `MyBackgroundService` that inherits from `BackgroundService`.
3. Override `ExecuteAsync` to include a periodic task (e.g., logging every 5 seconds).
4. Register the service in `Program.cs` using `builder.Host.ConfigureServices(...)` with `.AddHostedService<MyBackgroundService>()`.
5. Run the app with `dotnet run`.

## Things to try

- Change the interval to 10 seconds.
- Add a real-world task like fetching data from a service or writing to a database.
- Use `IHostedService` with dependency injection to pass configuration or services.
