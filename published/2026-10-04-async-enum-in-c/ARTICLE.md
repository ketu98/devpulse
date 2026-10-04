# async-enum-in-c

**Topic:** IAsyncEnumerable in C#  
**Category:** dotnet

# async-enum-in-c

In C#, `IAsyncEnumerable<T>` is a type that enables streaming of data asynchronously — one item at a time — without loading everything into memory at once. This is especially useful when dealing with large datasets or sources that produce data over time, like logs, file streams, or network responses.

The key difference from `IEnumerable<T>` is that `IAsyncEnumerable<T>` doesn't require all items to be materialized upfront. Instead, it yields values lazily, on demand, through a `ValueTask`-based iterator. This makes it ideal for scenarios where memory usage or performance matters — like processing a large file line-by-line or streaming API responses.

Here’s a practical example: imagine you have a file with millions of lines. Loading the entire file into memory would be wasteful. With `IAsyncEnumerable<string>`, you can read the file one line at a time, process it, and discard it immediately.

```csharp
public async IAsyncEnumerable<string> ReadLinesAsync(string filePath)
{
    using var stream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read);
    using var reader = new StreamReader(stream);
    string line;
    while ((line = await reader.ReadLineAsync()) != null)
    {
        yield return line;
    }
}
```

This small POC shows how you can wrap a file reader into a streaming interface. The method doesn’t load all lines into memory — it yields each line as it’s read. This makes it safe and efficient for large files.

You can then consume this stream in a method that processes each line individually:

```csharp
public async Task ProcessLinesAsync(string filePath)
{
    await foreach (var line in ReadLinesAsync(filePath))
    {
        Console.WriteLine($"Processing: {line}");
        // Do work per line — no memory bloat
    }
}
```

The `await foreach` syntax is critical here. It’s the pattern that allows you to consume an `IAsyncEnumerable<T>` in a clean, readable way — without needing to manually manage state or buffer results.

## What I learned

I learned that `IAsyncEnumerable<T>` isn’t just a theoretical construct — it’s a practical tool for handling real-world data streams. It avoids memory spikes, supports cancellation, and integrates well with async workflows. But it does require careful handling: you must ensure the enumerator doesn’t leak resources or leave dangling tasks.

Also, the `yield return` pattern in async enumerables is not a magic bullet. It can’t be used inside `async` methods that return `Task`, unless you’re using `IAsyncEnumerable<T>` correctly. Misuse can lead to deadlocks or unhandled exceptions.

## Key Takeaways

- `IAsyncEnumerable<T>` enables memory-efficient, streaming data consumption.
- Use `await foreach` to consume streams without managing iteration manually.
- Always ensure resource disposal (like streams) happens in the iterator.
- It’s not a replacement for `Task<T>` or `Task`, but a better fit for data that arrives over time.
- Test edge cases: empty files, large files, cancellation, and error recovery.
