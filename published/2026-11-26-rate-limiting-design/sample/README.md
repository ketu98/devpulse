## What this demonstrates

This POC demonstrates efficient rate limiting strategies using Python to prevent abuse and ensure scalability in API or service systems. It implements sliding window and fixed window rate limiting with configurable limits.

## How it works

The code uses a dictionary to track request timestamps. For each request, it checks if the current time minus the earliest timestamp exceeds the window duration. If yes, it resets the window. Otherwise, it rejects the request if the count exceeds the limit.

## How to run

```bash
python rate_limiter.py
```

The script runs a simple HTTP server that accepts requests and applies rate limiting based on a 10-second window and 5 requests per window.

## Things to try

- Change the window duration (e.g., 30 seconds) to observe impact on throughput.
- Adjust the max requests per window (e.g., 10) to test different limits.
- Add user ID support to enable per-user rate limiting.
- Integrate with a real API endpoint to simulate production use.
