## What this demonstrates

This POC demonstrates implementing API idempotency in a .NET service using C#. Idempotency ensures that repeated identical requests have the same effect as a single request, preventing duplicate processing and improving reliability.

## How it works

The service uses a unique request ID (generated per call) stored in a dictionary. Before processing a request, it checks if the ID already exists. If yes, it returns a response without processing. If no, it processes the request and stores the ID. This prevents duplicates while maintaining consistency.

## How to run

1. Build and run the project using `dotnet run`.
2. Send POST requests to `/api/submit` with a unique `idempotency-key` header.
3. Observe responses: first call returns processed data, subsequent identical calls return the same result.

## Things to try

- Test with identical requests using the same `idempotency-key`.
- Modify the storage to use in-memory or database persistence.
- Add timeout handling for long-running operations.
