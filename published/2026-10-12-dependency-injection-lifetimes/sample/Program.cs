using System;
using Microsoft.Extensions.DependencyInjection;

class Program
{
    static void Main()
    {
        var services = new ServiceCollection();
        
        // Register a service with singleton lifetime
        services.AddSingleton(new Logger());
        
        // Register a service with transient lifetime
        services.AddTransient(new DatabaseService());
        
        // Build the service provider
        var provider = services.BuildServiceProvider();
        
        // Use the services
        var logger = provider.GetRequiredService<Logger>();
        var dbService = provider.GetRequiredService<DatabaseService>();
        
        logger.Log("Starting app");
        dbService.Connect();
        
        // Show lifetime behavior
        Console.WriteLine("Logger is same instance: " + (logger == provider.GetRequiredService<Logger>()));
        Console.WriteLine("DatabaseService is new each time: " + (dbService != provider.GetRequiredService<DatabaseService>()));
    }
}

class Logger
{
    public void Log(string message)
    {
        Console.WriteLine($"[LOG] {message}");
    }
}

class DatabaseService
{
    public void Connect()
    {
        Console.WriteLine("[DB] Connecting...");
    }
}
