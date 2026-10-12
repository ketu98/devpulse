## What this demonstrates

This POC shows how dependency injection (DI) lifetimes work in .NET, focusing on `Singleton`, `Transient`, and `Scoped` lifetimes. It demonstrates how each lifetime affects object creation and lifecycle across different service calls.

## How it works

The app defines a service interface and implementations. The DI container registers services with specific lifetimes. When services are injected into components, the container provides instances based on the lifetime. `Transient` creates a new instance per request, `Scoped` per request scope, and `Singleton` shares one instance across the app.

## How to run

1. Open the solution in Visual Studio or .NET CLI.
2. Build and run the project.
3. Observe console output showing instance creation counts for each lifetime.

## Things to try

- Change a service from `Scoped` to `Singleton` and observe shared behavior.
- Add logging to track instance creation.
- Inject a service with `Transient` into a class that calls it multiple times—verify new instances are created.
