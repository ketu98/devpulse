using Polly;
using Polly.Extensions.Http;
using System;
using System.Net.Http;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        // Create a policy that retries up to 3 times with 1 second delay
        var retryPolicy = Policy
            .Handle<HttpRequestException>()
            .OrResult<HttpResponseMessage>(r => r.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable)
            .WaitAndRetryAsync(3, _ => TimeSpan.FromSeconds(1));

        // Create a circuit breaker that opens after 2 failures
        var circuitBreaker = Policy
            .Handle<HttpRequestException>()
            .CircuitBreakerAsync(2, TimeSpan.FromSeconds(10));

        // Combine retry and circuit breaker
        var combinedPolicy = Policy
            .Handle<HttpRequestException>()
            .OrResult<HttpResponseMessage>(r => r.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable)
            .WaitAndRetryAsync(3, _ => TimeSpan.FromSeconds(1))
            .CircuitBreakerAsync(2, TimeSpan.FromSeconds(10));

        // Simulate a call that may fail
        var client = new HttpClient();
        var result = await combinedPolicy.ExecuteAsync(async () =>
        {
            var response = await client.GetAsync("https://httpbin.org/delay/1");
            if (response.IsSuccessStatusCode)
                return response.Content.ReadAsStringAsync();
            else
                throw new HttpRequestException("Request failed");
        });

        Console.WriteLine("Result: " + result);
    }
}
