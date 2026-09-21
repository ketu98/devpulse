using Microsoft.AspNetCore.HealthChecks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // Add health checks service
        builder.Services.AddHealthChecks();

        var app = builder.Build();

        // Configure the health endpoint
        app.UseHealthChecks("/health");

        app.Run();
    }
}
