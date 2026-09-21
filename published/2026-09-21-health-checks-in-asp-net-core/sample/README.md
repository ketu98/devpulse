## What this demonstrates

This POC demonstrates how to implement health checks in ASP.NET Core to monitor application stability. It shows real-time status of services, database connectivity, and external dependencies using built-in health check mechanisms.

## How it works

Health checks are configured via `IHealthCheckService` and `HealthCheckBuilder`. Custom checks (e.g., database, HTTP endpoints) are registered with specific intervals and conditions. The endpoint `/health` returns a JSON response with status (OK, Warning, Critical) and details.

## How to run

1. Create a new ASP.NET Core project using `dotnet new webapp`.
2. Add `Microsoft.AspNetCore.HealthChecks` via `dotnet add package Microsoft.AspNetCore.HealthChecks`.
3. Register health checks in `Program.cs`:
   ```csharp
   builder.Services.AddHealthChecks()
       .AddCheck("self", () => HealthCheckResult.Success("Self check passed"));
   ```
4. Run the app with `dotnet run`.
5. Access `/health` in browser or via curl.

## Things to try

- Add a database health check with connection string.
- Implement a custom check for an external API.
- Test with a timeout or failure condition.
- Add health check middleware to log status to console.
