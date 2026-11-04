using System;
using System.Net.Http;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        // Create HttpClientFactory instance with default settings
        var httpClient = new HttpClient();
        
        // Simulate multiple concurrent requests to a dummy endpoint
        // This demonstrates how many sockets are opened and if they exhaust
        var tasks = new List<Task>();
        
        for (int i = 0; i < 100; i++)
        {
            var task = Task.Run(async () =>
            {
                try
                {
                    using (var client = new HttpClient())
                    {
                        var response = await client.GetAsync("https://httpbin.org/get");
                        Console.WriteLine($"Request {i} completed: {response.StatusCode}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Request {i} failed: {ex.Message}");
                }
            });
            tasks.Add(task);
        }
        
        // Wait for all tasks to complete
        await Task.WhenAll(tasks);
    }
}
