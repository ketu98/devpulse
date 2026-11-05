using System;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

class Program
{
    static void Main()
    {
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(new[]
            {
                new { Key = "Database:Connection", Value = "server=localhost;database=test" },
                new { Key = "Logging:Level", Value = "Info" },
                new { Key = "Api:Port", Value = "8080" }
            })
            .Build();

        var services = new ServiceCollection();
        services.Configure<DatabaseSettings>(config.GetSection("Database"));
        services.Configure<LoggingSettings>(config.GetSection("Logging"));
        services.Configure<ApiSettings>(config.GetSection("Api"));

        var provider = services.BuildServiceProvider();

        var db = provider.GetRequiredService<DatabaseSettings>();
        var log = provider.GetRequiredService<LoggingSettings>();
        var api = provider.GetRequiredService<ApiSettings>();

        Console.WriteLine($"DB: {db.Connection}");
        Console.WriteLine($"Log: {log.Level}");
        Console.WriteLine($"API Port: {api.Port}");
    }
}

public class DatabaseSettings
{
    public string Connection { get; set; } = string.Empty;
}

public class LoggingSettings
{
    public string Level { get; set; } = string.Empty;
}

public class ApiSettings
{
    public int Port { get; set; } = 0;
}
