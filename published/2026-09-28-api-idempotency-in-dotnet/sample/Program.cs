using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;

public class IdempotencyService
{
    private readonly ConcurrentDictionary<string, bool> _idempotencyMap = new();

    public async Task<bool> ProcessRequestAsync(string idempotencyKey, Func<Task<bool>> operation)
    {
        // If we've already processed this key, return success (idempotent)
        if (_idempotencyMap.TryGetValue(idempotencyKey, out bool processed) && processed)
        {
            Console.WriteLine($"Idempotency key {idempotencyKey} already processed.");
            return true;
        }

        // Mark as processed to avoid reprocessing
        _idempotencyMap[idempotencyKey] = true;

        try
        {
            var result = await operation();
            Console.WriteLine($"Request {idempotencyKey} processed successfully.");
            return result;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error processing request {idempotencyKey}: {ex.Message}");
            // Optionally: remove from map on failure if needed
            _idempotency或[idempotencyKey] = false;
            throw;
        }
    }
}
