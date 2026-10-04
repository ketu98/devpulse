using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

public class AsyncEnumExample
{
    public async IAsyncEnumerable<int> GenerateNumbersAsync()
    {
        int current = 0;
        while (true)
        {
            // Yield each number asynchronously
            await Task.Yield(); // Simulate async delay
            yield return current;
            current++;
            // Stop after 5 numbers for demo
            if (current >= 5) break;
        }
    }

    public async Task RunAsync()
    {
        await foreach (var num in GenerateNumbersAsync())
        {
            Console.WriteLine($"Received number: {num}");
        }
    }
}
