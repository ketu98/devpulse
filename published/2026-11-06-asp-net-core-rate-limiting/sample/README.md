## What this demonstrates

This POC demonstrates implementing rate limiting in ASP.NET Core to prevent abuse and ensure fair usage of APIs by limiting the number of requests per client.

## How it works

Rate limiting is configured using `UseRateLimiter` in the pipeline. It applies a policy that restricts requests based on IP address, with a default limit of 100 requests per minute. The policy uses a sliding window approach to track usage over time.

## How to run

1. Create a new ASP.NET Core Web API project using `dotnet new webapi`.
2. Add the `Microsoft.AspNetCore.RateLimiting` package via `dotnet add package Microsoft.AspNetCore.RateLimiting`.
3. In `Program.cs`, configure rate limiting:
   ```csharp
   builder.Services.AddRateLimiter(options =>
   {
       options.AddFixedWindowLimiter("default", config =>
       {
           config.PermitLimit = 100;
           config.SlitWindow = TimeSpan.FromMinutes(1);
           config.QueueLimit = 10;
       });
   });
   ```
4. Add middleware in `Program.cs`:
   ```csharp
   app.UseRateLimiter();
   ```
5. Run the app and test with multiple requests from the same IP.

## Things to try

- Change the limit or time window to observe effects.
- Test with different IPs to see if limits are applied per client.
- Add custom headers to identify clients for more granular control.
