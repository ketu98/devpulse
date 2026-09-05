using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading.Tasks;

public class GlobalExceptionFilter : IExceptionFilter
{
    public async Task OnExceptionAsync(ExceptionContext context)
    {
        // Log the exception (in real app, use logging framework)
        Console.WriteLine($"Exception caught: {context.Exception.Message}");

        // Create a standardized error response
        var errorResponse = new ErrorResponse
        {
            Message = "An unexpected error occurred",
            Timestamp = DateTime.UtcNow
        };

        // Set response to JSON error
        context.Result = new ObjectResult(errorResponse)
        {
            StatusCode = StatusCodes.Status500InternalServerError
        };

        // Prevent further execution
        context.ExceptionHandled = true;
    }
}

public class ErrorResponse
{
    public string Message { get; set; }
    public DateTime Timestamp { get; set; }
}

// Example usage in a minimal app (main entry point)
public class Program
{
    public static async Task Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        builder.Services.AddControllers();

        var app = builder.Build();

        app.UseExceptionHandler("/error");
        app.UseRouting();
        app.UseEndpoints(endpoints =>
        {
            endpoints.MapControllers();
        });

        // Apply the filter globally
        app.Use(async (context, next) =>
        {
            try
            {
                await next();
            }
            catch (Exception ex)
            {
                // This is a fallback if filter doesn't catch it
                Console.WriteLine($"Fallback: {ex.Message}");
                context.Response.StatusCode = 500;
                await context.Response.WriteAsync("Internal error");
            }
        });

        app.Run();
    }
}
