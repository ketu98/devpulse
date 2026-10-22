# Implementing a Background Service in ASP.NET Core

**Topic:** BackgroundService in ASP.NET Core  
**Category:** dotnet

# Implementing a Background Service in ASP.NET Core

In ASP.NET Core, background services allow you to run tasks independently of HTTP requests—like polling a service, processing files, or sending periodic notifications. These services run alongside your app and don’t block the main request pipeline.

The core pattern uses `IHostedService`, which is implemented by a class that inherits from `BackgroundService`. This service is registered in `Program.cs` and automatically started when the app launches.

Here’s a minimal working example:

```csharp
public class FileProcessorService : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<FileProcessorService> _logger;

    public FileProcessorService(IServiceProvider serviceProvider, ILogger<FileProcessor-ProcessorService> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var file = await _serviceProvider.GetRequiredService<IFileService>().ProcessNextFileAsync();
                if (file != null)
                {
                    _logger.LogInformation("Processed file: {FileName}", file.Name);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing file.");
            }

            // Wait 5 seconds before next attempt
            await Task.Delay(5000, stoppingToken);
        }
    }

    public override async Task StopAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("File processor stopping.");
        await base.StopAsync(stoppingToken);
    }
}
```

This service runs in a loop, checks for new files, processes them, and logs results. It uses dependency injection to access services like `IFileService`, which is injected via the `IServiceProvider`.

In a real POC, I built a simple file watcher that monitors a folder and processes CSV files when they appear. The service runs in a background thread, doesn’t interfere with HTTP endpoints, and can be stopped gracefully when the app shuts down.

I learned that background services don’t require a dedicated endpoint or HTTP route. They run on app startup and are managed by the host. The `StopAsync` method is called when the app stops, allowing cleanup. Also, cancellation tokens are essential—without them, a service could hang indefinitely.

Another key point: background services don’t automatically restart on failure. If your service crashes, the app may not recover unless you add resilience patterns (like retry logic or health checks). In my POC, I added a retry mechanism using `Policy` from `Microsoft.Extensions.Hosting`.

I also noticed that when using `IHostedService`, the service runs in the same process as the app, so memory and resource usage should be considered. If the service is CPU-heavy or I/O-bound, it might affect performance.

## What I learned
- Background services run independently of HTTP requests and are launched at app startup.
- They use cancellation tokens to allow graceful shutdown.
- You must handle exceptions to avoid crashes that prevent service recovery.
- Services don’t auto-restart on failure—resilience must be built in.

## Key Takeaways
- Use `BackgroundService` for long-running, non-blocking tasks.
- Inject dependencies via `IServiceProvider` for flexibility.
- Always include error handling and cancellation.
- Avoid blocking operations—use async/await and avoid tight loops.
- Add retry logic for transient failures.
