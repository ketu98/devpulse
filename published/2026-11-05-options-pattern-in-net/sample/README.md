## What this demonstrates

This POC demonstrates the Options Pattern in .NET for clean, flexible, and maintainable configuration. It shows how to define and inject configuration options using `IOptions<T>` and `IOptionsMonitor<T>`, enabling decoupled, type-safe configuration without hardcoding values.

## How it works

The pattern uses `IOptions<T>` to expose configuration as a strongly-typed object. A configuration class (e.g., `AppSettings`) is defined with properties like `ApiUrl`, `Timeout`, and `LoggingLevel`. The `IOptionsMonitor<T>` provides real-time updates, allowing configuration to change dynamically at runtime.

## How to run

1. Create a new .NET Console App.
2. Add `Microsoft.Extensions.Configuration` and `Microsoft.Extensions.Options`.
3. Define `AppSettings` class with properties.
4. Register configuration in `Program.cs` using `AddOptions()` and `Configure()`.
5. Inject `IOptions<AppSettings>` into a service to access values.

## Things to try

- Change configuration values in `appsettings.json` and observe real-time updates.
- Use `IOptionsMonitor<T>` to react to configuration changes.
- Add validation or defaults to properties to improve robustness.
