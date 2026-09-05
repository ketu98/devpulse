# Retry and Dead Letter Strategies in Azure

## What this demonstrates  
This proof-of-concept shows how to implement retry and dead-letter strategies for Azure Queue Storage using C#. It simulates transient errors and demonstrates handling them with exponential backoff and fallback to a dead-letter queue.

## How it works  
The app sends messages to an Azure Queue. On failure, it retries with exponential backoff (1s, 2s, 4s). If retries fail, the message is moved to a dead-letter queue. The retry logic is implemented using a loop with increasing delays. Dead-letter handling is triggered when the maximum retry count is exceeded.

## How to run  
1. Install Azure Storage SDK via NuGet.  
2. Set environment variables:  
   `AZURE_STORAGE_CONNECTION_STRING=your-connection-string`  
   `QUEUE_NAME=your-queue-name`  
   `DEAD_LETTER_QUEUE_NAME=your-dead-letter-queue-name`  
3. Run the program. It sends a test message and logs success or failure.  

## Notes  
- This is a simplified demo. Real scenarios may require monitoring, custom error handling, or integration with Azure Event Grid.  
- Retry policies should be tuned to application-specific error patterns.  
- Dead-letter queues must be pre-created and accessible.  
- No authentication is used; production use requires secure connection strings.  
- All operations are synchronous for clarity.  

This demo illustrates core resilience patterns in cloud messaging systems.
