# CancellationToken Best Practices for .NET Applications

**Topic:** CancellationToken Best Practices  
**Category:** dotnet

# CancellationToken Best Practices for .NET Applications

In real-world .NET code, `CancellationToken` is often used to allow operations to be gracefully canceled—like a long-running background task or a network request. But it’s easy to misuse it: passing it around without proper handling, ignoring cancellation in loops, or not propagating it correctly through method chains.

## What I learned

I recently worked on a POC where a service polled a remote API every 10 seconds to check for updates. The polling loop was simple, but I initially implemented it with a `Task.Delay(10000)` inside a `while` loop, and only canceled the loop when the token was signaled. That worked—but only because the loop didn’t run long. When I added a delay of 30 seconds to simulate a longer run, I saw a memory leak: the task kept running even after cancellation, because the `Task.Delay` didn’t respect the token.

The fix was to use `CancellationToken.WaitHandle` or `CancellationToken.Token` with `Task.Delay` and ensure the loop body didn’t hold references to long-lived objects. I also added a guard that breaks the loop immediately when the token is canceled, without waiting for the next delay.

I learned that cancellation isn’t just about “stopping” a task—it’s about *responding* to cancellation in a way that avoids side effects. For example, if a method calls `HttpClient.SendAsync`, it should not continue to send requests after cancellation is signaled. A common mistake is to use `await` on a delay and then ignore the token in the next step.

Another key insight: don’t create new tokens inside methods. Instead, pass the token down from the caller and avoid re-creating it. If you need to combine tokens (e.g., from multiple sources), use `CancellationTokenSource` carefully—only when you’re managing a shared cancellation point.

## Key Takeaways

- Always check the token in loops and long-running operations. Never rely on `Task.Delay` to respect cancellation without explicit handling.
- Never ignore cancellation in async methods. If a method can be canceled, it should respond immediately.
- Avoid creating new `CancellationToken` instances inside methods. Pass the token from the caller and use it directly.
- Use `CancellationToken` with `Task.WhenAny` or `Task.WhenAll` to allow cancellation of multiple tasks, but ensure the cancellation is respected in all participants.
- Test cancellation paths with real cancellation signals—don’t just test “does it stop?” but “does it stop cleanly and avoid memory leaks?”

In practice, a simple rule: if a method runs for more than a second, and it’s not a one-off, it should accept a `CancellationToken`. This makes it easier to refactor later and supports better observability and debugging.

The POC showed that even small changes in how we handle cancellation can prevent subtle bugs and improve reliability. It’s not glamorous, but it’s essential for building maintainable async code.
