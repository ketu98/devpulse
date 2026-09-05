using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using System;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        var connectionString = "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net";
        var blobServiceClient = new BlobServiceClient(connectionString);

        try
        {
            var blobClient = blobServiceClient.GetBlobContainerClient("test").GetBlobClient("data.txt");
            await blobClient.UploadAsync("content");
            Console.WriteLine("Upload successful.");
        }
        catch (RequestFailedException ex) when (ex.ErrorCode == "StorageError")
        {
            Console.WriteLine("Retry failed. Moving to dead letter.");
            await MoveToDeadLetter("deadletter.txt", "StorageError");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Unexpected error: {ex.Message}");
        }
    }

    static async Task MoveToDeadLetter(string fileName, string error)
    {
        var deadLetterClient = new BlobServiceClient("DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net")
            .GetBlobContainerClient("deadletters")
            .GetBlobClient(fileName);

        await deadLetterClient.UploadAsync($"Error: {error} at {DateTime.Now}");
        Console.WriteLine("Error moved to dead letter queue.");
    }
}
