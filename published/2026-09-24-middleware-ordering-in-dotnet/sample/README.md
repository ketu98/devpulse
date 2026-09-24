## What this demonstrates

This POC shows how middleware ordering affects request processing in ASP.NET Core. Middleware components are executed in the order they are added to the pipeline, with earlier items running first.

## How it works

The app defines two middleware components: one that logs "Before" and another that logs "After". When a request arrives, the middleware pipeline executes from top to bottom. The order of `Use` calls determines execution sequence. The first middleware runs first, and each subsequent one runs after the previous one completes.

## How to run

1. Open the project in Visual Studio or VS Code.
2. Build and run the app using `dotnet run`.
3. Navigate to `http://localhost:5000` in a browser.
4. Observe the console output showing the log messages in sequence.

## Things to try

- Swap the order of `UseMiddleware1` and `UseMiddleware2` in Program.cs.
- Add a middleware that modifies the response.
- Insert a middleware that redirects or returns a custom response.
- Test with a custom HTTP method or route to see how ordering affects behavior.
