using Microsoft.Azure.ServiceBus;

class Program
{
    static async Task Main(string[] args)
    {
        // Connection string for Service Bus (use a real one in production)
        const string connectionString = "Endpoint=sb://your-servicebus.namespace.servicebus.windows.net/;SharedAccessKey=your-key;SharedAccessKeyName=RootManageSharedAccessKey";
        
        // Create a receiver for a queue named "myqueue"
        var queueName = "myqueue";
        var client = new QueueClient(connectionString, queueName);
        
        // Receive messages from the queue
        Console.WriteLine($"Listening for messages in queue '{queueName}'...");
        
        var messageHandler = async (message, token) =>
        {
            Console.WriteLine($"Received message: {message.Body}");
            await Task.Delay(1000); // Simulate processing
        };
        
        // Register message handler with error handling
        await client.RegisterMessageHandler(messageHandler, new MessageHandlerOptions()
        {
            MaxConcurrentCalls = 1,
            DefaultLockDuration = TimeSpan.FromMinutes(1),
            OnError = async (exception, token) =>
            {
                Console.WriteLine($"Error handling message: {exception.Message}");
            }
        });
        
        // Keep the app running to receive messages
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
        
        // Close the client
        await client.CloseAsync();
    }
}
