⚙️ I spent some time experimenting with HttpClientFactory in .NET and how it handles socket lifecycle — especially under load.  

I built a small POC to simulate multiple concurrent requests and observed how default socket reuse behaves.  

• HttpClientFactory pools connections by default, which helps avoid socket exhaustion.  
• Without proper configuration, it can still leak sockets if not used with a timeout or cancellation strategy.  
• Setting a reasonable socket timeout and enabling connection reuse prevents unnecessary resource drain.  

One thing that stood out: even with factory-level abstractions, socket exhaustion isn’t just about configuration — it’s about understanding how each request interacts with the underlying OS.  

Real insight: small changes in how you manage lifetimes can make a big difference in stability. 🚀

💻 Small POC

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

✅ Key takeaway

For me, the useful part of a small POC is seeing where the concept actually holds up once it reaches code.

📚 References

• Use the IHttpClientFactory - .NET
  https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory

• HttpClient guidelines for .NET - .NET
  https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines

🎥 Reference video

YouTube results for HttpClientFactory and Socket Exhaustion
https://www.youtube.com/results?search_query=HttpClientFactory+and+Socket+Exhaustion+tutorial

🔗 Full runnable POC

https://github.com/ketu98/devpulse/tree/main/published/2026-11-04-httpclientfactory-and-socket-exhaustion/sample

🏷️ #DotNet #CSharp #BackendEngineering #SoftwareEngineering
