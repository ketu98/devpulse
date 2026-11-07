using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using System;

namespace MinimalApisVsControllers
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Minimal API: Direct route with no controller
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            var app = builder.Build();

            // Minimal API route
            app.MapGet("/minimal/hello", () => "Hello from Minimal API");

            // Controller-based route
            app.UseRouting();
            app.MapControllers();

            app.Run();
        }
    }

    // Simple controller for comparison
    [ApiController]
    [Route("[controller]")]
    public class ValuesController : ControllerBase
    {
        [HttpGet("world")]
        public IActionResult GetWorld() => Ok("Hello from Controller");
    }
}
