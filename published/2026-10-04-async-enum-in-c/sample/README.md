## What this demonstrates

This POC demonstrates how to use `IAsyncEnumerable<T>` in C# to stream data asynchronously, one item at a time, without loading all items into memory.

## How it works

The code defines a simple async enumerator that yields integers from 1 to 10, one at a time. Each value is produced asynchronously using `await Task.Yield()`, simulating a delay between values. The consumer reads items one by one, making it ideal for processing large datasets efficiently.

## How to run

1. Create a new C# console application.
2. Copy the code into the `Program.cs` file.
3. Build and run the project. The output will show each number from 1 to 10, printed sequentially with a 1-second delay between each.

## Things to try

- Modify the range (e.g., 1 to 100) to see how performance scales.
- Replace the delay with a real data source (e.g., file, database).
- Add error handling to simulate failure during streaming.
- Use `await foreach` to consume the stream in a loop.
