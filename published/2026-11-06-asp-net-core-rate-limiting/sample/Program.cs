using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

// Add rate limiting with 10 requests per minute per client IP
builder.Services.AddRateLimiting(options =>
{
    options.AddHeaderFilter("X-RateLimit-Limit", "10");
    options.AddHeaderFilter("X-RateLimit-Remaining", "10");
    options.AddHeaderFilter("X-RateLimit-Reset", "60");
    options.DefaultPolicy = new RateLimitPolicyOptions
    {
        Limit = 10,
        Period = TimeSpan.FromMinutes(1),
        SkipIfHeaderPresent = "X-Client-Id"
    };
});

var app = builder.Build();

app.UseRateLimiting();

app.MapGet("/api/echo", (HttpContext context) =>
{
    return Results.Ok(new { Message = "Hello from rate-limited endpoint" });
});

app.Run();
