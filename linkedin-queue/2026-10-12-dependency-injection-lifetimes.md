⚙️ I spent some time experimenting with how dependency injection lifetimes work in .NET — not just the theory, but the real behavior in different scenarios.  

I built a small POC to observe how services behave across different scopes: singleton, transient, and scoped.  

• Singleton instances are shared across the entire app — great for lightweight services, but risky if state is involved.  
• Transient instances are created every time they’re requested — useful for stateless operations, but can lead to inconsistent behavior if not handled carefully.  
• Scoped instances live only for the lifetime of a request — ideal for per-request state, like logging or user context.  

One thing that stood out: the choice of lifetime directly affects how you design service interactions — especially when sharing state or handling side effects. 🚀 💡

💻 Small POC

class Program
{
    static void Main()
    {
        var services = new ServiceCollection();

        // Register a service with singleton lifetime
        services.AddSingleton(new Logger());

        // Register a service with transient lifetime
        services.AddTransient(new DatabaseService());

✅ Key takeaway

For me, the useful part of a small POC is seeing where the concept actually holds up once it reaches code.

📚 References

• DbContext Lifetime, Configuration, and Initialization - EF Core
  https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/

• Dependency injection - .NET
  https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/overview

🎥 Reference video

YouTube results for Dependency Injection Lifetimes
https://www.youtube.com/results?search_query=Dependency+Injection+Lifetimes+tutorial

🔗 Full runnable POC

https://github.com/ketu98/devpulse/tree/main/published/2026-10-12-dependency-injection-lifetimes/sample

🏷️ #DotNet #CSharp #BackendEngineering #SoftwareEngineering
