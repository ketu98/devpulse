using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Hosting;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);
        
        // Add middleware in reverse order to show ordering impact
        builder.Services.Configure<RequestLocalizationOptions>(options =>
        {
            options.DefaultRequestCulture = new RequestCulture("en");
        });

        var app = builder.Build();

        // Middleware order: 1. Logging, 2. Localization, 3. Error handling
        app.Use(async (context, next) =>
        {
            Console.WriteLine("Logging middleware: Request received");
            await next();
        });

        app.Use(async (context, next) =>
        {
            Console.WriteLine("Localization middleware: Setting culture");
            await next();
        });

        app.Use(async (context, next) =>
        {
            Console.WriteLine("Error handling middleware: Before error handling");
            try
            {
                await next();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error caught: {ex.Message}");
            }
        });

        app.Run(async context =>
        {
            await context.Response.WriteAsync("Hello from endpoint");
        });
    }
}
