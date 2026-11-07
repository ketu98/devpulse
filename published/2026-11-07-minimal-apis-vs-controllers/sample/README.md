## What this demonstrates

This POC compares Minimal APIs and Controllers in .NET, showing how to achieve the same HTTP endpoints with minimal configuration versus traditional MVC-style controllers.

## How it works

Minimal APIs use a simple, declarative syntax with `app.MapGet()` and `app.MapPost()`, while Controllers rely on action methods in a class with `Controller` base. Both serve HTTP requests, but Minimal APIs are more concise and lightweight.

## How to run

1. Open the project in Visual Studio or VS Code.
2. Ensure .NET 8 is installed.
3. Run `dotnet run` in the project directory.
4. Access endpoints at `http://localhost:5000` — both APIs and controllers are available.

## Things to try

- Replace a controller with a minimal API for a simple endpoint.
- Add authentication to both and observe differences in setup.
- Measure startup time and code size for each approach.
- Try routing with query parameters in both models.
