using System;
using System.Threading;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        Console.WriteLine("Press Ctrl+C to cancel the operation.");
        
        var cts = new CancellationTokenSource();
        
        // Register a handler for cancellation
        cts.Token.Register(() => Console.WriteLine("Operation was cancelled."));

        // Simulate a long-running task
        await PerformTaskWithCancellation(cts.Token);
        
        Console.WriteLine("Program completed.");
    }

    static async Task PerformTaskWithCancellation(CancellationToken token)
    {
        int count = 0;
        while (!token.IsCancellationRequested)
        {
            Console.WriteLine($"Working... count: {count}");
            count++;
            
            // Simulate work with a delay
            await Task.Delay(1000, token);
            
            // Early exit if cancelled
            if (count > 10)
                break;
        }
    }
}
