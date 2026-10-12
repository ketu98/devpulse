# Understanding Dependency Injection Lifetimes in .NET

**Topic:** Dependency Injection Lifetimes  
**Category:** dotnet

# Understanding Dependency Injection Lifetimes in .NET

Dependency Injection (DI) is a pattern that helps decouple components, making code more testable and maintainable. In .NET, DI containers manage object lifetimes—how long an object lives and when it’s created or disposed. Choosing the right lifetime matters, especially when you’re building services that interact with databases, caches, or external APIs.

There are three main lifetimes in .NET DI:

- **Singleton**: One instance per container lifetime. Shared across all components. Good for services that are stateless and expensive to create—like configuration or logging.
- **Scoped**: One instance per request or scope (e.g., per HTTP request in web apps). Ideal for services that need to maintain state per user or session, like a database context.
- **Transient**: A new instance every time it’s requested. Best for lightweight, stateless services—like a simple validator or helper.

I built a mini-POC to compare these lifetimes in a simple console app. I created a service that logs messages with a timestamp and a user ID. I injected it into three different components: a singleton, a scoped, and a transient instance.

In the singleton case, all components shared the same instance. The log message was written once, and the user ID was always the same—because the instance was reused. This worked fine when the service was stateless, but failed when I tried to assign a different user ID per call.

In the scoped case, each component got its own instance tied to a scope. When I simulated a user session, each instance had the correct user ID. This matched real-world use cases like web API controllers with user-specific data.

The transient case created a new instance every time. It was fast and clean, but I noticed memory bloat when the service was called frequently. Each call generated a new object, even if it didn’t need one. This is fine for small helpers, but can become a problem in performance-sensitive scenarios.

## What I learned

- Singleton is great for shared, stateless services but risky if state is involved.
- Scoped is ideal for request-based services—like web APIs—where each user session needs its own context.
- Transient is efficient for small, stateless operations but can lead to performance or memory issues under load.

I also learned that lifetime choice isn’t just about logic—it’s about performance, memory, and correctness. Misusing a lifetime can silently introduce bugs or scalability problems.

## Key Takeaways

- Match the lifetime to your service’s behavior: stateful vs. stateless.
- Scoped is often the best choice for web apps with user sessions.
- Avoid singleton for services that should not share state.
- Profile memory usage when using transient in high-frequency scenarios.
- Always consider how the service is used—what data it holds, how often it’s called.

In practice, start simple. Use scoped for most services. Only move to singleton or transient when you have a clear, tested reason. This keeps your app stable and predictable.
